import json
import ssl
import smtplib
import logging

from celery import Celery
from celery_conf import ConfigCelery, GoogleConfig

from email.message import EmailMessage


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create configuration
config = ConfigCelery()

# Create Celery app - this needs to be at module level for Celery to find it
app = Celery(config.name)

print(
    config.broker_url,
)

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
        logger.info(email_data)

        msg = EmailMessage()
        msg['From'] = email_data.get('sender', GoogleConfig.default_sender)
        msg['To'] = email_data.get('sender', GoogleConfig.default_sender)
        msg['Subject'] = email_data.get('subject', 'test message')

        if 'body_html' in email_data and email_data['body_html']:
            msg.add_alternative(email_data['body_html'], subtype='html')

        body_text = json.dumps(email_data.get('body_text', email_data.get('body', '')))

        msg.set_content(body_text)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(GoogleConfig.smtp_server, GoogleConfig.smtp_port, context=context) as server:
            logger.info(GoogleConfig.smtp_username, GoogleConfig.smtp_password)
            server.login(GoogleConfig.smtp_username, GoogleConfig.smtp_password)
            server.send_message(msg)

        logger.info(f"Email successfully sent to {email_data.get('receiver')}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


@app.task(bind=True, name='send_email')
def send_email(task_self, **email_data):
    print(email_data)
    """Task that processes and sends an email"""
    try:
        logger.info(f"Processing email for: {email_data.get('receiver', 'unknown')}")
        return send_email_function(email_data)

    except Exception as e:
        logger.error(f"Email sending failed: {e}")
        retry_count = task_self.request.retries
        task_self.retry(exc=e, countdown=60 * (2 ** retry_count))  # Retry with backoff
        return False