import os
import dotenv
import jwt
from functools import wraps

from django.utils import timezone  # Użyj Django timezone zamiast datetime.timezone

dotenv.load_dotenv()

def validate_secret_key(function):
    @wraps(function)
    def wrapper(cls, *args, **kwargs):
        if not hasattr(cls, 'SECRET_KEY') or not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY is not configurated")

        if len(cls.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY too short (min 32 chars)")

        return function(cls, *args, **kwargs)
    return wrapper


class TokenHasher:
    SECRET_KEY = os.getenv('SECRET_KEY')
    RESET_EXPIRY_SECONDS = 900

    @classmethod
    @validate_secret_key
    def generate_reset_token(cls, user_id):
        """Generate reset password token (15 min TTL)"""
        try:
            now = timezone.now()
            expire_time = now + timedelta(seconds=cls.RESET_EXPIRY_SECONDS)  # 900s = 15min

            payload = {
                "token_type": "reset",  # ZMIANA: było "access"
                "exp": int(expire_time.timestamp()),
                "iat": int(now.timestamp()),
                "jti": str(uuid.uuid4().hex),
                "user_id": user_id
            }

            reset_token = jwt.encode(
                payload,
                cls.SECRET_KEY,
                algorithm=cls.ALGORITHM,
            )
            return reset_token, payload

        except jwt.InvalidSignatureError:
            raise jwt.InvalidSignatureError("Invalid encryption key")

    @classmethod
    @validate_secret_key
    def validate_reset_token(cls, token: str):
        """Validate reset token specifically"""
        try:
            payload = cls.decode_token(token)

            # Check if it's reset token
            if payload.get('token_type') != 'reset':
                raise ValueError("Not a reset token")

            return payload.get('user_id')

        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Reset token expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid reset token")
