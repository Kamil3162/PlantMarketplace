

class TokenError(Exception):
    """
        Base exception for mechanism related errors
    """
    pass

class TokenNotFound(TokenError):
    """
        Raises when mechanism is not found in request
    """
    pass

class TokenExpired(TokenError):
    """
        Raises when mechanism validation time expired
    """
    pass

class InvalidRequestError(TokenError):
    """
        Raises when the request object is invalid
    """
    pass


