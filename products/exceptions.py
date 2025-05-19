from django.core.exceptions import ObjectDoesNotExist


class BaseException(Exception):
    """
        Base exception for subclass excpetions
    """

class ProductNotFound(BaseException):
    """
        Exception invoke during product doesnt not exists
    """
    pass

class ProductImproperDataFormat(BaseException):
    """
        Passed data format is not proper
    """
    pass

