

class UserNotFound(Exception):
    """
        Exception raised when a user doesn't exist
    """


class PermissionGroupError(Exception):
    """
        Exception raised when a permission group doesn't exist
    """

class PermissionGroupExists(Exception):
    """
        Exception raised when a permission group already exists
    """

class PermissionGroupDenied(Exception):
    """
        Exception raised when a permission group denied
    """

class PermissionIntegrityError(Exception):
    """
        Exception raised when a permission group already exists
    """

