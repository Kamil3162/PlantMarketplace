

class TokenError(Exception):
    """
        Base exception for token related errors
    """
    pass

class TokenNotFound(TokenError):
    """
        Raises when token is not found in request
    """
    pass

class TokenExpired(TokenError):
    """
        Raises when token validation time expired
    """
    pass

class InvalidRequestError(TokenError):
    """
        Raises when the request object is invalid
    """
    pass


