from datetime import datetime, timedelta
import uuid
import jwt

from django.conf import settings
from django.utils import timezone  # Użyj Django timezone zamiast datetime.timezone
from core.exceptions import TokenExpiredError


class JWTManager(object):
    ALGORITHM = 'HS256'
    DEFAULT_EXPIRY_SECONDS = 1800
    SECRET_KEY = "$+#hqc5(f0#y84^!$a!suex3(k@3dlzphefh42ls=(bk)jrctr"

    @classmethod
    def create_access_token(cls, user_id: int):
        """
            Encodes user data to JWT mechanism

            Args:
                user_id: int

            Returns:
                String access_token
        """
        now = timezone.now()  # Użyj Django timezone.now()
        expire_time = now + timedelta(seconds=cls.DEFAULT_EXPIRY_SECONDS)

        payload = {
            "token_type": "access",
            "exp": int(expire_time.timestamp()),
            "iat": int(now.timestamp()),
            "jti": str(uuid.uuid4().hex),
            "user_id": user_id
        }

        access_token = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM,
        )

        return access_token, payload

    @classmethod
    def decode_token(cls, token: str) -> dict:
        """
        Decodes and validates a JWT token.

        Args:
            token: The JWT token string to decode

        Returns:
            Dictionary containing the decoded payload

        Raises:
            jwt.ExpiredSignatureError: If token has expired
            jwt.InvalidTokenError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired - decode function")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid token")

    @classmethod
    def validate_token(cls, token: str):
        """
            Validate expiration date of passed token
        Args:
            token: JWT token string
        Returns:
            Boolean or raises exception
        """
        decoded_token = cls.decode_token(token)
        current_time = timezone.now().timestamp()  # Użyj Django timezone
        expiration_time = decoded_token.get('exp', None)

        if expiration_time is None:
            return False
        elif expiration_time < current_time:
            raise TokenExpiredError("Token validation expired")
        return True

    @classmethod
    def create_refresh_token(cls, user_id: int):
        """
            Creates refresh token for the given user
        Args:
            user_id: User ID

        Returns:
            String refresh token
        """
        token_life_time = getattr(settings, "TOKEN_LIFETIME_DAYS", 7)
        now = timezone.now()  # Użyj Django timezone
        expires_at = now + timedelta(days=token_life_time)

        payload = {
            "token_type": "refresh",
            "exp": int(expires_at.timestamp()),
            "iat": int(now.timestamp()),
            "jti": str(uuid.uuid4().hex),
            "user_id": user_id
        }

        refresh_token = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )
        return refresh_token

    @classmethod
    def refresh_access_token(cls, refresh_token: str):
        """
        Creates a new access token using a valid refresh token.

        Args:
            refresh_token: String refresh token

        Returns:
            String new access token
        """
        try:
            payload = cls.decode_token(refresh_token)

            if payload.get('token_type') != 'refresh':
                raise ValueError("Token is not a refresh token")

            user_id = payload.get('user_id')
            if not user_id:
                raise ValueError("Invalid token payload")

            access_token, user_payload = cls.create_access_token(user_id)
            return access_token

        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise jwt.InvalidTokenError("Invalid refresh token")