from django.utils import timezone
from data.models import CustomUser


def generate_reset_email(email:str, instance: CustomUser) -> dict:
    if not isinstance(user, CustomUser):
        raise TypeError(f"variable user type: {type(instance)} is not a CustomUser")

    email_data = {
        'to_email': email,
        'subject': 'Password Reset Request - PlantMarketplace',
        'template': 'password_reset',
        'context': {
            'user_name': instance.first_name,
            'user_last_name': instance.last_name,
            'user_id': instance.id,
            'reset_link': f"http://yourdomain.com/reset-password/{instance.id}/",
            'platform_name': 'PlantMarketplace',
            'request_time': timezone.now().strftime(
                '%Y-%m-%d %H:%M:%S'),
            'support_email': 'support@plantmarketplace.com'
        }
    }

    return email_data

def generate_del_email(email:str, instance: CustomUser) -> dict:
    if not isinstance(instance, CustomUser):
        raise TypeError(f"variable user type: {type(instance)} is not a CustomUser")

    email_data = {
        'to_email': instance.email,
        'subject': 'Account Deletion Confirmation',
        'template': 'account_deleted',
        'context': {
            'user_name': instance.first_name,
            'user_last_name': instance.last_name,
            'deletion_date': timezone.now().strftime(
                '%Y-%m-%d %H:%M:%S'),
            'registration_date': instance.created_at.strftime('%Y-%m-%d'),
            'platform_name': 'PlantMarketplace',
            'support_email': 'support@plantmarketplace.com'
        }
    }
    return email_data

def generate_register_email(email:str, instance: CustomUser) -> dict:
    if not isinstance(instance, CustomUser):
        raise TypeError(f"variable user type: {type(instance)} is not a CustomUser")

    email_data = {
        'to_email': instance,
        'subject': 'Account Deletion Confirmation',
        'template': 'account_deleted',
        'context': {
            'user_name': instance.first_name,
            'user_last_name': instance.last_name,
            'deletion_date': timezone.now().strftime(
                '%Y-%m-%d %H:%M:%S'),
            'registration_date': instance.created_at.strftime('%Y-%m-%d'),
            'platform_name': 'PlantMarketplace',
            'support_email': 'support@plantmarketplace.com'
        }
    }
    return email_data

def get_dict_model(instance: CustomUser):
    if not isinstance(instance, CustomUser):
        raise TypeError(f"variable user type: {user} is not a CustomUser")

    return instance.__dict__

async def send_email_async(email_data, method):
    """Helper function to send emails asynchronously"""
    try:
        email_service = EmailClient()
        endpoint = "/email/send/"
        response = await email_service.make_request(
            endpoint,
            method=method,
            json_data=email_data
        )
        return response
    except Exception as e:
        print(f"Email sending error: {e}")
        return None