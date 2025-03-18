import os
import uuid
from datetime import datetime, timezone, timedelta

import pytest
import jwt
from faker import Faker
from django.core.management.utils import get_random_string

from core.jwt_manager import JWTManager
from account.models import CustomUser
import dotenv

dotenv.load_dotenv()
fake = Faker()

class TestJWTManager:
    @pytest.fixture
    def jwt_manager(self):
        return JWTManager()

    @pytest.fixture
    def create_user(self):
        return CustomUser(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            password='password'
        )

    @pytest.fixture
    def user_token(self, jwt_manager, create_user):
        user_id = create_user.id
        access_token = jwt_manager.create_access_token(user_id)
        return access_token

    @pytest.fixture
    def generate_random_key(self):
        return get_random_string(len(os.getenv('DJANGO_SEC')))

    def test_decode_invalid_key(
        self,
        user_token,
        jwt_manager,
        create_user,
        generate_random_key
    ):
        decoded_token =  jwt_manager.decode_token(
            user_token,
        )

        test_decoded_token = jwt.decode(
            user_token,
            generate_random_key,
            algorithms=[jwt_manager.ALGORITHM],
        )

        assert decoded_token['user_id'] == create_user.id
        assert decoded_token['user_id'] != test_decoded_token['user_id']

    def test_create_access_token_structure(self, jwt_manager, create_user):
        """Test that created tokens have the correct structure and fields"""
        token = jwt_manager.create_access_token(create_user.id)
        decoded = jwt.decode(token, options={"verify_signature": False},
                             algorithms=[jwt_manager.ALGORITHM])

        # Check required fields
        assert "token_type" in decoded
        assert "exp" in decoded
        assert "iat" in decoded
        assert "jti" in decoded
        assert "user_id" in decoded

        # Check values
        assert decoded["token_type"] == "access"
        assert decoded["user_id"] == create_user.id

        # Check time fields
        now = datetime.now(timezone.utc).timestamp()
        assert abs(decoded["iat"] - now) < 10  # Within 10 seconds of now
        assert abs(
            decoded["exp"] - (now + jwt_manager.DEFAULT_EXPIRY_SECONDS)) < 10

    def test_tampered_token(self, jwt_manager, create_user):
        """Test that tampered tokens are rejected"""
        token = jwt_manager.create_access_token(create_user.id)

        # Decode the token without verification
        decoded_payload = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=[jwt_manager.ALGORITHM]
        )

        # Tamper with the payload
        decoded_payload["user_id"] = 999999

        # Re-encode with a bogus key
        tampered_token = jwt.encode(
            decoded_payload,
            "invalid-key",
            algorithm=jwt_manager.ALGORITHM
        )

        # Verify it's rejected
        with pytest.raises(jwt.InvalidTokenError):
            jwt_manager.decode_token(tampered_token)

    def test_invalid_token_signature(self, jwt_manager, create_user, generate_random_key):
        access_token = jwt_manager.create_access_token(create_user.id)

        # decoded token
        decoded_token = jwt_manager.decode_token(access_token)

        assert decoded_token['user_id'] == create_user.id

        # create a token with different singing key
        payload = {
            "token_type": "access",
            "exp": int((datetime.now(timezone.utc) + timedelta(seconds=900)).timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "jti": str(uuid.uuid4().hex),  # Unique token identifier
            "user_id": create_user.id
        }
        fake_token = jwt.encode(
            payload,
            generate_random_key,
            algorithm=jwt_manager.ALGORITHM
        )

        with pytest.raises(jwt.InvalidTokenError):
            jwt_manager.decode_token(fake_token)


    def test_exp_time(self, user_token, jwt_manager, create_user):
        decoded_token =  jwt_manager.decode_token(user_token)
        base_time = jwt_manager.DEFAULT_EXPIRY_SECONDS

        assert decoded_token['exp'] == base_time


