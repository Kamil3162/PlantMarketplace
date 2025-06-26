

class BaseError(Exception):
    """Custom exception for token validation errors"""
    pass

class TokenExpiredError(BaseError):
    """Custom exception for token expired errors"""
    pass

class UnauthorizedAccess(BaseError):
    """Custom exception for unauthorized access"""
    pass

class MissingTokenError(BaseError):
    """Custom exception for missing token"""
    pass

class InvalidTokenError(BaseError):
    """
        Custom exception for invalid token
    """

class PermissionDenied(BaseError):
    """
        Custom exception for permission denied
    """