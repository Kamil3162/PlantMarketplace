
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

class ModelDoesNotExists(Exception):
    """
        Exception raised when a model doesn't exists'
    """
