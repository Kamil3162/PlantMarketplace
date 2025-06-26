import datetime
from datetime import datetime, timezone, timedelta

import jwt
import uuid

from fastapi import Cookie, FastAPI, Query, Header
from core.config import SECRET_KEY

class AuthService:
    ALGORITHM = "HS256"
    DEFAULT_EXPIRY_SECONDS = 1800
    SECRET_KEY = "$+#hqc5(f0#y84^!$a!suex3(k@3dlzphefh42ls=(bk)jrctr"

    @classmethod
    def decode_token(cls, token):
        """
            Decodes and validates a JWT mechanism.

            Args:
                secret_key:
                token: The JWT mechanism string to decode

            Returns:
                Dictionary containing the decoded payload

            Raises:
                jwt.ExpiredSignatureError: If mechanism has expired
                jwt.InvalidTokenError: If mechanism is invalid
        """
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError as exc:
            raise jwt.ExpiredSignatureError(f"{str(exc)}")
        except jwt.InvalidTokenError as exc:
            raise jwt.InvalidTokenError(f"{str(exc)}")

    @classmethod
    def encode_token(cls, user_id: uuid) -> dict:
        """
            Encodes user data to JWT mechanism

            Args:
                secret_key:
                user_id: int
                expires_delta - timedelta - timedelta

            Returns:
                Dictionary access_token
        """
        now = datetime.now(timezone.utc)
        expire_time = now + timedelta(seconds=cls.DEFAULT_EXPIRY_SECONDS)

        payload = {
            "token_type": "access",
            "exp": int(expire_time.timestamp()),
            "iat": int(now.timestamp()),
            "jti": str(uuid.uuid4().hex),  # Unique mechanism identifier
            "user_id": user_id
        }

        access_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=cls.ALGORITHM,
        )

        return access_token

    @classmethod
    def is_token_valid(cls, token: str) -> bool:
        try:
            payload = cls.decode_token(token)
            print(f"Decoded payload: {payload}")

            current_time = datetime.now(timezone.utc).timestamp()
            exp_time = payload.get('exp')  # ✅ Poprawna nazwa zmiennej

            # Check if expiration time exists
            if exp_time is None:  # ✅ Poprawiona zmienna
                print("No expiration time found")
                return False

            if current_time > exp_time:  # ✅ Poprawiona zmienna
                print("Token expired")
                return False

            print("Token is valid")
            return True

        except Exception as e:
            # Handle potential decode errors or invalid tokens
            return False

