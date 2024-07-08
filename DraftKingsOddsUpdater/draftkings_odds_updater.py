import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from send_message import send_email_no_attachment
import os


def fighters_to_be_tracked(csv_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path, dtype={'fighter_odds': str})  # Convert fighter_odds column to str
    fighter_name = df['fighter_name'].tolist()  # Convert fighter names to a list
    fighter_odds = df['fighter_odds'].tolist()  # Convert fighter odds to a list
    # Create a dictionary with fighter names as keys and their odds as values
    fighters_to_be_tracked_dict = {k: v for k, v in zip(fighter_name, fighter_odds)}
    return fighters_to_be_tracked_dict  # Return the dictionary

def scrape_dk():
    # URL of the DraftKings UFC odds page
    url = "https://sportsbook.draftkings.com/leagues/mma/ufc"

    # Fetch the HTML content from the URL
    response = requests.get(url)

    if response.status_code == 200:
        # Store response content
        html_content = response.content

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the "root" id in the HTML content
        root_id = soup.find(id="root")

        # Make list of all the fighter names found in the HTML content within the "root" id
        all_fighters_list = [fighter.text.strip() for fighter in root_id.find_all("div", class_="event-cell__name-text")]

        # Make a list of all the fighter moneyline odds
        all_fighters_odds_list = [fighter_odds.text.strip() for fighter_odds in root_id.find_all("span", class_="sportsbook-odds american no-margin default-color")]

        # Creating a dictionary
        current_fighter_odds_dict = {k: v for k, v in zip(all_fighters_list, all_fighters_odds_list)}

        return current_fighter_odds_dict # Return the dictionary
    else:
        print(f"Failed to retrieve data: {response.status_code}")
        return None # Return None if data retrieval fails

def update_csv_with_new_odds(csv_file_path, updated_fighters_dict):
    # Read the existing CSV file
    df = pd.read_csv(csv_file_path)
    # Update the 'fighter_odds' column with new odds from the dictionary
    df['fighter_odds'] = df['fighter_name'].map(updated_fighters_dict)
    # Save the updated DataFrame back to the CSV file
    df.to_csv(csv_file_path, index=False)

def normalize_odds(odds_str):
    # Replace non-standard minus sign with standard ASCII minus sign
    normalized_str = odds_str.replace('−', '-')
    return int(normalized_str) # Convert the normalized string to an integer

def odds_comparison_fix(current_odds, tracked_odds):
    # If current and tracked are both positive
    if current_odds > 0 and tracked_odds > 0:
        return current_odds - tracked_odds
    # If current and tracked are both negative
    elif current_odds < 0 and tracked_odds < 0:
        return current_odds - tracked_odds
    # If current is negative and tracked is positive
    elif current_odds < 0 and tracked_odds > 0:
        return (current_odds + 100) - (tracked_odds - 100)
    # If current is positive and tracked is negative
    else:
        return (current_odds - 100) - (tracked_odds + 100)
    

def main():
    # Specify the path to your CSV file
    csv_file_path = 'fighters_to_be_tracked.csv'

    while True:
        # Get the fighters to be tracked from the CSV file
        fighters_to_be_tracked_dict = fighters_to_be_tracked(csv_file_path)
        # Scrape the current fighter odds from DraftKings
        current_fighter_odds_dict = scrape_dk()

        if fighters_to_be_tracked_dict and current_fighter_odds_dict:
            for fighter in fighters_to_be_tracked_dict:
                # Get the tracked odds and normalize them
                tracked_odds = normalize_odds(fighters_to_be_tracked_dict[fighter])
                # Get the current odds for the fighter (default to tracked odds if not found)
                current_odds_str = current_fighter_odds_dict.get(fighter, str(tracked_odds))
                # Normalize the current odds
                current_odds = normalize_odds(current_odds_str)
                
                # Check if the odds have changed by at least 10 points
                if abs(odds_comparison_fix(current_odds, tracked_odds)) >= 10:
                    print(f"Odds change detected for {fighter}: {fighters_to_be_tracked_dict[fighter]} -> {current_fighter_odds_dict[fighter]}")
                    # Send email update on new odds
                    send_email_no_attachment(f"The odds for {fighter} have changed from {fighters_to_be_tracked_dict[fighter]} to {current_fighter_odds_dict[fighter]}.", f"{fighter} odds updated")
                    # Update the dictionary with the new odds
                    fighters_to_be_tracked_dict[fighter] = current_odds_str

            # Update local csv file with new odds
            update_csv_with_new_odds(csv_file_path, fighters_to_be_tracked_dict)

        time.sleep(3600)  # Wait for 3600 seconds (one hour) before scraping again

if __name__ == "__main__":
    main()
