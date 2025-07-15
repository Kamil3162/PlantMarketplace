class BaseError(Exception):
    """Custom exception for mechanism validation errors"""
    pass

class TokenExpiredError(BaseError):
    """Custom exception for mechanism expired errors"""
    pass

class UnauthorizedAccess(BaseError):
    """Custom exception for unauthorized access"""
    pass

class MissingTokenError(BaseError):
    """Custom exception for missing mechanism"""
    pass

class InvalidTokenError(BaseError):
    """
        Custom exception for invalid mechanism
    """

class PermissionDenied(BaseError):
    """
        Custom exception for permission denied
    """

