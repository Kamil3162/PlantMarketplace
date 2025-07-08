
class BaseExc(Exception):
    """
        Base exception for subclass excpetions
    """

class ProductNotFound(BaseExc):
    """
        Exception invoke during product doesnt not exists
    """
    pass

class ProductImproperDataFormat(BaseExc):
    """
        Passed data format is not proper
    """
    pass

class FileNameError(BaseExc):
    """
        Exception raise when file name is None
    """
    pass
