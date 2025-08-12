

class UserNotFound(Exception):
    """
        Exception raised when a user doesn't exist
    """

class UserPermissionDenied(Exception):
    """
        Exception raise when a user pass inproper data
    """
    def __init__(self, detail, status_code):
        self.detail = detail
        self.status_code = status_code

class MethodException(Exception):
    """
        Raise when we use improper request method during request
    """

class UserDataFormat(Exception):
    """
        Raise when user send empty user_email
    """


class PageNumberException(Exception):
    """
        Raise when someone send a page with negative page number
    """