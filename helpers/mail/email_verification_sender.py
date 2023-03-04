# from __future__ import print_function

import os
import base64
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# # If modifying these scopes, delete the file token.json.
SCOPES = ['https://mail.google.com/']

def gmail_send_message(toEmail, inGenCode):
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'token.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Trying to send email
    try:
        # API Init
        service = build('gmail', 'v1', credentials=creds)

        # Adding data to email
        message = MIMEMultipart()

        message['To'] = toEmail
        message['From'] = 'Stevenvilla70@gmail.com'
        message['Subject'] = 'INIT Alumni Verefication Code'

        # Opening HMTL File to convert to text to send in Email
        pathToEmailMessage = Path(__file__).parent / './email_message.html'
        with open(pathToEmailMessage, 'r', encoding='utf-8') as file: # Encoding is necessary to open HTML file
            html = file.read()

        # print(html)
        updatedhtml = html.replace('GENERATEDCODE',inGenCode)

        message.attach(MIMEText(updatedhtml, "html"))

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        
        # sending message
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message

gmail_send_message('Stevenvilla70@gmail.com', 'ABC123')