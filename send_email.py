import os.path
import ssl
from email.message import EmailMessage
import smtplib
import dotenv

dotenv.load_dotenv()

email_sender = 'kamilholb@gmail.com'
email_receiver = 'kamilholb@gmail.com'
email_password = os.getenv('APP_PASSWORD')

subject = 'PlantMarketplace Email Test'
body = """I've test my email appi"""

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

context = ssl.create_default_context()

def send_email_reset():
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.send_message(em)
