import os
import logging

from io import BytesIO
from datetime import datetime
from pathlib import Path
import uuid
from dotenv import load_dotenv
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from .exceptions import (
    S3AuthenticationError,
    S3ConnectionError,
    S3FileUploadError,
    S3TypeError,
    S3FileTypeError,
    S3FileValidationError,
    S3ConfigurationError
)

from .utils import file_name_handler, connection_handler, AWS_ERROR_MAPPING

load_dotenv()

class S3Client:

    __file_extensions = {".jpg", ".jpeg", ".png"}

    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        bucket_name: str,
        logs_path: str = ""
    ):
        """
           logs_path - you have to pass you current path to check logs of working
           Library in main compatible in case django upload files i doenst test that in scenario for example fast api or flask
        """

        if not all([access_key, secret_key, region, bucket_name]):
            raise S3ConfigurationError("Missing required parameters")

        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.bucket_name = bucket_name
        self.logs_path = logs_path
        self.logger = self._setup_logging()
        self.client = self._initialise_client()

    def _setup_logging(self):
        """
            Konfiguruje logging dla tej klasy, bez modyfikowania globalnego loggera.
        """
        path = Path(os.path.join(self.logs_path, "logs"))
        path.mkdir(exist_ok=True)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Logger dla tej klasy
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if logger.handlers:
            logger.handlers.clear()

        log_filename = Path(
            os.path.join(
                path,
                f"s3_client_{datetime.now().strftime('%Y_%m_%d')}.log"
            )
        )

        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @connection_handler
    def _initialise_client(self) -> boto3.client:
        """
        Inicjalizuje klienta S3.
        Zwraca klienta lub None w przypadku błędu.
        """
        try:
            self.logger.info("Inicjalizacja klienta S3...")

            client = boto3.client(
                's3',
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region,
            )

            client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(
                f"Pomyślnie zainicjalizowano klienta S3 dla bucketa {self.bucket_name}")
            return client

        except NoCredentialsError:
            raise S3AuthenticationError("Problem with AWS credentials",
                                        error_code="NoCredentialsError")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            request_id = e.response.get('ResponseMetadata', {}).get(
                'RequestId', 'Unknown')

            exception_class = AWS_ERROR_MAPPING.get(
                error_code,
                S3ConnectionError
            )
            raise exception_class(f"{error_message} (RequestId: {request_id})",
                                  error_code=error_code)

        except Exception as e:
            self.logger.error(f"Błąd inicjalizacji klienta S3: {str(e)}")
            raise S3ConnectionError(f"Unexpected error: {str(e)}")

    @connection_handler
    def upload_image(self, file_object: BinaryIO, file_name:str = None):
        """
        Wrzuca obraz do S3 z pliku lub obiektu Django.

        Args:
            file_object: Ścieżka do pliku lub obiekt Django
            s3_key: Opcjonalny klucz S3 dla pliku
            file_object - jest to plik który jest używany głownie w przyapdku django, mogą pojawic sie problemy w przypadku innych frameworków lub bibliotek
        Returns:
            str: Klucz S3 do wrzuconego pliku lub None w przypadku błędu
        """
        if not file_name:
            raise S3FileValidationError("Provided file_name is None")

        try:
            if hasattr(file_object, 'name') and hasattr(file_object, 'read'):
                self.client.upload_fileobj(
                    file_object,
                    self.bucket_name,
                    file_name
                )
                self.logger.info(f"Pomyślnie wrzucono plik do {file_name}")
            else:
                raise S3FileTypeError("Passed file is not an image file")

            return file_name

        except ClientError as e:
            raise ClientError(
                e.response['Error']['Code'],
                e.response['Error']['Message']
            )

    @file_name_handler
    def generate_file_name(self, original_name: str):
        """
        Generuje unikalną nazwę pliku dla S3.

        Args:
            original_name: Oryginalna nazwa pliku lub obiekt pliku z atrybutem 'name'

        Returns:
            str: Unikalny klucz S3
        """
        if not isinstance(original_name, str):
            raise S3TypeError("Argument 'original_name' must be of type 'str'")

        extension = Path(original_name).suffix

        if extension not in self.__file_extensions:
            raise S3FileTypeError(
                "Argument 'original_name' must be of type 'str'"
            )

        prefix = str(uuid.uuid4())

        return f"{prefix}{extension}"

    @connection_handler
    def list_buckets(self):
        """
        Zwraca listę wszystkich dostępnych bucketów.
        """

        try:
            response = self.client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            return buckets
        except Exception as e:
            self.logger.error(f"Błąd podczas listowania bucketów: {str(e)}")
            return []

    def get_presigned_url(self, object_key:str, expiration=3600):
        """
        Generates a pre-signed URL for accessing an S3 object

        Args:
            object_key: The S3 object key (path in bucket)
            expiration: URL expiration time in seconds (default: 1 hour)

        Returns:
            str: Pre-signed URL or None if error
        """
        if not object_key:
            self.logger.warning("No object key provided")
            return None

        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            self.logger.info(f"Generated pre-signed URL for {object_key}")
            return url
        except Exception as e:
            self.logger.error(f"Error generating URL: {str(e)}")
            return None

    def show_files_from_bucket(self, bucket_name: str):
        status = self.client.head_bucket(Bucket=bucket_name)
        bucket_files = self.client.list_objects(Bucket=bucket_name)
        return bucket_files




