import smtplib
import os.path as op
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime
import pytz

# Define time variables
dt_us_central = datetime.now(pytz.timezone('US/Eastern'))
new_york_date = dt_us_central.strftime("%d")
new_york_month = dt_us_central.strftime("%m")
new_york_year = dt_us_central.strftime("%Y")

# Define sender and recipient email addresses
sender_email = "stevefights@gmail.com"
recipient_email = "stevefights@gmail.com"
app_password = ""  ################################################ Replace with your generated password

def send_email(filename, body, subject):
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Open the file in bynary mode
    attachment = open(filename, "rb")

    # Add the attachment to the message
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', "attachment; filename= %s" % op.basename(filename))
    msg.attach(part)

    # Add message body
    msg.attach(MIMEText(body, 'plain'))

    # Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls() # enable security
    session.login(sender_email, app_password)  # Use app-specific password instead of actual password
    text = msg.as_string()
    session.sendmail(sender_email, recipient_email, text)
    session.quit()
    print('Mail Sent')

if __name__ == "__main__":
    send_email("test__data.csv", "body", "subject")
