import base64
import os.path
import smtplib
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText

from requests import HTTPError


subject =  'Test message'
body = 'Test message'
sender = 'kamilholb@gmail.com'
to = 'kamilholb@gmail.com'

scopes = ['https://www.googleapis.com/auth/gmail.send']

flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets_file='googleapi.json',
    scopes=scopes,
)

creds = flow.run_local_server(
    port=8000,
    redirect_uri_trailing_slash=False
)

service = build('gmail', 'v1', credentials=creds)

message = MIMEText(body, 'plain')
message['to'] = to
message['from'] = sender
message['subject'] = subject
create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

try:
    message = (service.users().messages().send(userId='me', body=create_message).execute())
    print('Emial sended')
except HttpError as error:
    print('error occured')
