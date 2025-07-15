
class RedisManager:
    def __init__(self):
        self.redInst = redis.Redis(
            host='redis',
            port=6379,
            db=0,
            # decode_responses=True
        )
        self.reset_prefix  = "reset-"

    def store_reset_token(self, user_id, token):
        """Store reset token in Redis with 15min TTL"""
        try:
            reset_key = f"{self.reset_prefix}{token}"
            self.redInst.setex(
                reset_key,
                900,  # 15 minutes TTL
                user_id
            )
            return True
        except RedisError as e:
            raise RedisError(f"Failed to store reset token: {str(e)}")

    def get_user_from_reset_token(self, token):
        """Get user_id from reset token"""
        try:
            reset_key = f"{self.reset_prefix}{token}"
            user_id = self.redInst.get(reset_key)
            return user_id.decode('utf-8') if user_id else None
        except RedisError as e:
            raise RedisError(f"Failed to get reset token: {str(e)}")

    def invalidate_reset_token(self, token):
        """Remove reset token (single use)"""
        try:
            reset_key = f"{self.reset_prefix}{token}"
            self.redInst.delete(reset_key)
        except RedisError as e:
            raise RedisError(f"Failed to delete reset token: {str(e)}")

    def cleanup_user_reset_tokens(self, user_id):
        """Remove all reset tokens for user (security)"""
        try:
            pattern = f"{self.reset_prefix}*"
            for key in self.redInst.scan_iter(match=pattern):
                stored_user_id = self.redInst.get(key)
                if stored_user_id and stored_user_id.decode('utf-8') == str(user_id):
                    self.redInst.delete(key)
        except RedisError as e:
            raise RedisError(f"Failed to cleanup reset tokens: {str(e)}")