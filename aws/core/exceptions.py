from botocore.exceptions import ClientError

class S3LibraryError(Exception):
    """
        Custom Base Exception for AWSS3 library.
    """
    def __init__(self, message: str, error_code=None):
        self.message = message
        self.error_code = error_code

    def __str__(self):
        base = f"{self.__class__.__name__}: {self.message}"
        if self.error_code:
            base += f" (Code: {self.error_code})"
        return base


class S3ConnectionError(S3LibraryError):
    """Raised when S3 connection fails"""
    pass


class S3AuthenticationError(S3LibraryError):
    """Raised when authentication fails"""
    pass


class S3BucketError(S3LibraryError):
    """Raised for bucket-related errors"""
    pass


class S3ObjectError(S3LibraryError):
    """Raised for object-related errors"""
    pass


class S3FileValidationError(S3LibraryError):
    """Raised when file validation fails"""
    def __init__(self, message: str, file_name: str = None, file_size: int = None):
        self.file_name = file_name
        self.file_size = file_size
        super().__init__(message)

    def __str__(self):
        base = f"{self.__class__.__name__}: {self.message}"
        if self.file_name:
            base += f" (File Name: {self.file_name})"
        if self.file_size:
            base += f" (File Size: {self.file_size})"
        return base


class S3FileTypeError(S3FileValidationError):
    def __init__(self, message: str):
        super().__init__(message)


class S3FileUploadError(S3LibraryError):
    """Raise when file upload fails"""
    def __init__(self, message: str):
        super().__init__(message)


class S3FileDownloadError(S3LibraryError):
    """Raise when file download fails"""
    pass


class S3ConfigurationError(S3LibraryError):
    """Raised for configuration issues"""
    pass


class S3TypeError(S3LibraryError):
    def __init__(self, message: str):
        super().__init__(message)
