from typing import Callable
from functools import wraps
from time import perf_counter_ns

import logging

from botocore.exceptions import ClientError, NoCredentialsError

from .exceptions import S3FileTypeError, S3TypeError, S3LibraryError, \
    S3ConnectionError, S3ObjectError, S3AuthenticationError, S3BucketError

AWS_ERROR_MAPPING = {
    'NoSuchBucket': S3BucketError,
    'AccessDenied': S3AuthenticationError,
    'SignatureDoesNotMatch': S3AuthenticationError,
    'InvalidAccessKeyId': S3AuthenticationError,
    'NoSuchKey': S3ObjectError,
    'InvalidObjectName': S3ObjectError,
    'RequestTimeout': S3ConnectionError,
    'ServiceUnavailable': S3ConnectionError,
}


def connection_handler(func: Callable):
    """
        Decorator to handle AWS connection-related errors and convert them to library exceptions.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            time_start = perf_counter_ns()
            logger = getattr(self, 'logger')
            response = func(self, *args, **kwargs)
            final_time = (perf_counter_ns() - time_start) / 1000000
            logger.info(
                f"Czas wykonania {func.__name__}: {final_time} ms"
            )
            return response

        except NoCredentialsError:
            logger.error("AWS credentials not found or invalid")
            raise

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            logger.error(f"AWS ClientError: {error_code} - {error_message}")

            exception_class = AWS_ERROR_MAPPING.get(error_code,
                                                    S3ConnectionError)
            raise exception_class(f"{error_message}", error_code=error_code)

        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise S3LibraryError(f"Unexpected error: {str(e)}")

    return wrapper


def file_name_handler(func: Callable):
    """
        Decorator to handle file name generation and validation.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            time_start = perf_counter_ns()
            logger = getattr(self, 'logger')
            response = func(self, *args, **kwargs)
            final_time = (perf_counter_ns() - time_start) / 1000000
            logger.info(
                f"Czas wykonania {func.__name__}: {final_time} ms"
            )
            return response

        except S3FileTypeError as exc:
            logger.error(f"File type validation failed: {str(exc)}")
            # Convert to more general type error
            raise

        except S3TypeError as exc:
            logger.error(f"Type validation failed: {str(exc)}")
            raise

        except Exception as exc:
            logger.error(
                f"Unexpected error in filename handling: {str(exc)}")
            raise

    return wrapper
