import os
import base64
from dotenv import load_dotenv
import secrets 

from pathlib import Path
import smtplib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# # If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_verification_SMTP_email(recipient):
    SUBJECT = "🟡 INIT: Alumni Association Verification Code"
    SENDER = "team@weareinit.org"
    # Trying to send email
    try:
        msg = MIMEMultipart()
        bodyPath = './email_message.html'
        pathToEmailMessage = Path(__file__).parent / bodyPath
        with open(pathToEmailMessage, 'r', encoding='utf-8') as file: # Encoding is necessary to open HTML file
            body = file.read()

        # Generate code
        verification_token = secrets.token_hex(4).upper()

        # print(html)
        updatedhtml = body.replace('VERIFICATION_CODE', verification_token)

        msg.attach(MIMEText(updatedhtml, "html"))
        msg['Subject'] = SUBJECT
        msg['From'] = SENDER
        msg['To'] = recipient
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(SENDER, GMAIL_APP_PASSWORD)
        smtp_server.sendmail(SENDER, recipient, msg.as_string())
        smtp_server.quit()  

        return verification_token
        
    except HttpError as error:
        print(F'An error occurred: {error}')

if __name__ == "__main__":
    recipient = "ivan@weareinit.org"
    send_SMTP_email(recipient)
