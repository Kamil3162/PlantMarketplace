import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

twilio_number = os.getenv("TWILIO_NUMBER")
twilio_account_id = os.getenv("ACCOUNT_SID")
twilio_auth_token = os.getenv('ACCOUNT_TOKEN')
my_phone_number = os.getenv("PHONE_NUMBER")

client = Client(twilio_account_id, twilio_auth_token)
message = client.messages.create(
    to=my_phone_number,
    from_=twilio_number,
    body='Test msg Python Application'
)


