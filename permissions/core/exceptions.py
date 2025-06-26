
class Error(Exception):
    """
        Base error for subclass errors
    """


class PermissionGroupError(Error):
    """
        Exception raised when a permission group doesn't exist
    """

class PermissionGroupExists(Error):
    """
        Exception raised when a permission group already exists
    """

class PermissionGroupDenied(Error):
    """
        Exception raised when a permission group denied
    """

class PermissionIntegrityError(Error):
    """
        Exception raised when a permission group already exists
    """

class ModelDoesNotExists(Error):
    """
        Exception raised when a model doesn't exists'
    """
