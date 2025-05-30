from celery import Celery
from celery_conf import ConfigCelery
from email.message import EmailMessage
import ssl
import smtplib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create configuration
config = ConfigCelery()

# Create Celery app - this needs to be at module level for Celery to find it
app = Celery(config.name)

# Configure Celery
app.conf.update(
    broker_url=config.broker_url,
    task_serializer=config.task_serializer,
    accept_content=config.accept_content,
    result_serializer=config.result_serializer,
    timezone=config.timezone,
    enable_utc=config.enable_utc
)

def send_email_function(email_data):
    """The actual email sending function"""
    try:
        # Email settings
        default_sender = 'kamilholb@gmail.com'
        smtp_server = 'smtp.gmail.com'
        smtp_port = 465
        smtp_username = 'kamilholb@gmail.com'
        smtp_password = 'iwyj juvk dees ctcx'

        # Create email message
        msg = EmailMessage()
        msg['From'] = email_data.get('sender', default_sender)
        # msg['To'] = mail_data.get('receiver', default_sender)
        msg['To'] = 'kamilholb@gmail.com'
        msg['Subject'] = email_data.get('subject', 'test message')

        # Set content - handle both HTML and plain text
        if 'body_html' in email_data and email_data['body_html']:
            msg.add_alternative(email_data['body_html'], subtype='html')

        # Use body_text if available, otherwise use body key for backwards compatibility
        body_text = email_data.get('body_text', email_data.get('body', ''))
        msg.set_content(body_text)

        # Send the email via SMTP
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(msg)

        logger.info(f"Email successfully sent to {email_data.get('receiver')}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


@app.task(bind=True, name='send_email')
def send_email(task_self, **email_data):
    """Task that processes and sends an email"""
    try:
        logger.info(f"Processing email for: {email_data.get('receiver', 'unknown')}")
        return send_email_function(email_data)

    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        retry_count = task_self.request.retries
        task_self.retry(exc=e, countdown=60 * (2 ** retry_count))  # Retry with backoff
        return False