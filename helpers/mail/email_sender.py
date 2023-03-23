# # from __future__ import print_function

# import os
# import base64
# import secrets 

# from pathlib import Path

# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build
# from googleapiclient.errors import HttpError

# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# # If modifying these scopes, delete the file token.json.

# to_email = 'stevenvilla70@gmail.com'

# def gmail_send_verification_code(to_email):

#     SCOPES = ['https://www.googleapis.com/auth/gmail.send']

#     # setup
#     creds = None
#     # The file token.json stores the user's access and refresh tokens, and is
#     # created automatically when the authorization flow completes for the first
#     # time.
#     if os.path.exists('token.json'):
#         creds = Credentials.from_authorized_user_file('token.json', SCOPES)
#     # If there are no (valid) credentials available, let the user log in.
#     print(creds.valid)
#     if not creds or not creds.valid:
#         if creds and creds.expired and creds.refresh_token:
#             creds.refresh(Request())
#         else:
#             print("These are both None") #TODO: Fix token/Oauth
#             flow = InstalledAppFlow.from_client_secrets_file(
#                 'credentials.json', SCOPES)
#             creds = flow.run_local_server(port=0)
#         # Save the credentials for the next run
#         with open('token.json', 'w') as token:
#             token.write(creds.to_json())
#     # Trying to send email
#     try:
#         # API Init
#         service = build('gmail', 'v1', credentials=creds)

#         # Adding data to email
#         message = MIMEMultipart()

#         message['To'] = to_email
#         message['From'] = 'team@weareinit.org'
#         message['Subject'] = 'Verify your Discord User'

#         # Opening HMTL File to convert to text to send in Email
#         pathToEmailMessage = Path(__file__).parent / './email_message.html'
#         with open(pathToEmailMessage, 'r', encoding='utf-8') as file: # Encoding is necessary to open HTML file
#             html = file.read()

#         # Generate code
#         verification_token = secrets.token_hex(4).upper()

#         # print(html)
#         updatedhtml = html.replace('GENERATEDCODE', verification_token)
#         message.attach(MIMEText(updatedhtml, "html"))

#         # encoded message
#         encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
#             .decode()

#         create_message = {
#             'raw': encoded_message
#         }
#         print('Can we make it here?')
#         # sending message
#         send_message = (service.users().messages().send
#                         (userId="me", body=create_message).execute())
#         print(F'Message Id: {send_message["id"]}')

#     except HttpError as error:
#         print(F'An error occurred: {error}')
#         send_message = None
#     return verification_token

# gmail_send_verification_code(to_email)

# from __future__ import print_function

import os
import base64
from dotenv import load_dotenv

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

password = os.getenv('GMAIL_APP_PASSWORD')

# # If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def send_SMTP_email(subject, bodyPath, sender, recipients):
    # Trying to send email
    try:
        msg = MIMEMultipart()

        pathToEmailMessage = Path(__file__).parent / bodyPath
        with open(pathToEmailMessage, 'r', encoding='utf-8') as file: # Encoding is necessary to open HTML file
            body = file.read()

        body.replace('GENERATEDCODE', 'ABC123')

        print(password)

        msg.attach(MIMEText(body, "html"))
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
        smtp_server.quit()  
        
    except HttpError as error:
        print(F'An error occurred: {error}')


subject = "INIT Alumni Verefication Code"
# body = "This is the body of the text message"
sender = "team@weareinit.org"
recipients = ["Stevenvilla70@gmail.com", "ivan@weareinit.org"]

send_SMTP_email(subject, './email_message.html', sender, recipients)
