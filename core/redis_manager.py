from datetime import time

import redis

from account.scheme import UserScheme
from redis import RedisError

from .jwt_manager import JWTManager
from .exceptions import TokenValidationError

class RedisManager(object):
    def __init__(self):
        self.redInst = redis.Redis(
            host='redis',
            port=6379,
            db=0,
            # decode_responses=True
        )
        self.blocked_token_prefix = "blocked-"
        self.user_prefix = "user-"

    def generate_user_data(self, user_instance):
        """
            Generate user data and token for Redis storage

            Args:
                user_instance (User): User instance

            Returns:
                user_dict - converted django User instance to dict
                access_token - generated access token for passed user
        """
        if not user_instance:
            raise ValueError("Invalid user instance")

        user_dict = UserScheme.by_django_user(user_instance)
        user_dict['is_staff'] = 'false'
        user_dict['is_confirmed'] = 'false'

        access_token = JWTManager.create_access_token(
            data=user_dict,
            expires_delta=1800
        )
        return user_dict, access_token

    def assign_user(self, user_instance):
        """
        Assign a user to Redis storage.

        Args:
            user_instance: Django user model instance

        Raises:
            ValueError: If user_instance is invalid
            RedisError: If Redis operation fails
        """
        try:
            # Generate user data and token
            user_data, token = self.generate_user_data(user_instance)
            key = f'{self.user_prefix}{token}'

            print(key)
            print(user_data)

            # Store in Redis
            self.redInst.hset(
                name=key,  # Using 'name' instead of 'key' for clarity
                mapping=user_data,
            )

            return token

        except RedisError as e:
            # Log the error here if needed
            raise RedisError(f"Failed to store user data: {str(e)}")

    def check_token_validation(self, token):
        try:
            decoded_token = JWTManager.decode(token)
            exp_token = decoded_token.get('exp')

            # Check if expiration time exists
            if not exp_token:
                return False

            # Compare expiration timestamp with current time
            current_time = datetime.datetime.now(
                datetime.timezone.utc).timestamp()
            if current_time > exp_token:
                return False

            return True

        except Exception as e:
            # Handle potential decode errors or invalid tokens
            return False

    def is_blocked_token(self, token):
        """
            Check does user token can be used for future authentication
        """
        blocked_key = f"{self.blocked_tokens_prefix}{token}"
        return bool(self.redInst.exists(blocked_key))

    def block_token(self, token):
        """
            Block token use for future usage

        """
        try:
            blocked_key = f"{self.blocked_tokens_prefix}{token}"
            self.redInst.set(
                blocked_key,
                True
            )

            # delete all user data with key
            user_key = f'{self.user_prefix}{token}'
            self.redInst.delete(user_key)
        except RedisError as e:
            raise RedisError(f"Failed to store user data: {str(e)}")

    def get_user_data(self, token):
        """
            Generate user data and token for user request
        """
        key = f'{self.user_prefix}{token}'
        user_data = self.redInst.hgetall(key)
        return user_data

