import os
import logging
from io import BytesIO
from datetime import datetime
from pathlib import Path
import uuid

import boto3
from dotenv import load_dotenv

# Ładujemy zmienne środowiskowe
load_dotenv()


class S3Client:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        region: str,
        bucket_name: str
    ):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.bucket_name = bucket_name

        # Konfiguracja loggera dla klasy, a nie globalnego
        self.logger = self._setup_logging()

        # Inicjalizacja klienta
        self.client = self._initialise_client()

        # Sprawdzamy czy klient został poprawnie zainicjalizowany
        if not self.client:
            raise RuntimeError("Nie udało się zainicjalizować klienta S3")

    def _setup_logging(self):
        """
            Konfiguruje logging dla tej klasy, bez modyfikowania globalnego loggera.
        """
        # Tworzymy katalog logs jeśli nie istnieje
        Path("logs").mkdir(exist_ok=True)

        # Formatowanie logów
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Logger dla tej klasy
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Usuwamy istniejące handlery aby uniknąć duplikatów
        if logger.handlers:
            logger.handlers.clear()

        # Handler do pliku
        log_filename = f"logs/s3_client_{datetime.now().strftime('%Y_%m_%d')}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Handler do konsoli
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Dodajemy handlery
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _initialise_client(self):
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

            # Sprawdzamy czy mamy dostęp do bucketa
            client.head_bucket(Bucket=self.bucket_name)
            self.logger.info(f"Pomyślnie zainicjalizowano klienta S3 dla bucketa {self.bucket_name}")

            return client

        except Exception as e:
            self.logger.error(f"Błąd inicjalizacji klienta S3: {str(e)}")
            return None

    def upload_image(self, file_object, s3_key=None):
        """
        Wrzuca obraz do S3 z pliku lub obiektu Django.

        Args:
            file_object: Ścieżka do pliku lub obiekt Django
            s3_key: Opcjonalny klucz S3 dla pliku

        Returns:
            str: Klucz S3 do wrzuconego pliku lub None w przypadku błędu
        """
        if not self.client:
            self.logger.error("Klient S3 nie jest zainicjalizowany")
            return None

        try:
            # Generujemy klucz S3 jeśli nie został podany
            if s3_key is None:
                if hasattr(file_object, 'name'):
                    s3_key = self.generate_file_name(file_object.name)
                else:
                    s3_key = self.generate_file_name(str(file_object))

            # Sprawdzamy czy to obiekt Django
            if hasattr(file_object, 'name') and hasattr(file_object, 'read'):
                # Wrzucamy obiekt Django
                self.client.upload_fileobj(
                    file_object,
                    self.bucket_name,
                    s3_key
                )
                self.logger.info(f"Pomyślnie wrzucono plik Django do {s3_key}")
            else:
                # Wrzucamy z ścieżki pliku
                file_path = Path(file_object)
                if not file_path.exists():
                    self.logger.error(f"Plik {file_path} nie istnieje")
                    return None

                self.client.upload_file(
                    str(file_path),
                    Bucket=self.bucket_name,
                    Key=s3_key
                )
                self.logger.info(f"Pomyślnie wrzucono plik {file_path} do {s3_key}")

            return s3_key

        except Exception as e:
            self.logger.error(f"Błąd wrzucania pliku: {str(e)}")
            return None

    def generate_file_name(self, original_name):
        """
        Generuje unikalną nazwę pliku dla S3.

        Args:
            original_name: Oryginalna nazwa pliku lub obiekt pliku z atrybutem 'name'

        Returns:
            str: Unikalny klucz S3
        """
        # Sprawdzamy czy to obiekt pliku czy nazwa pliku
        if hasattr(original_name, 'name'):
            filename = original_name.name
        else:
            filename = str(original_name)

        # Pobieramy rozszerzenie pliku
        extension = Path(filename).suffix

        # Generujemy unikalny prefix z UUID
        prefix = str(uuid.uuid4())

        # Zwracamy ścieżkę w formacie: bucket_name/YYYY-MM-DD/UUID.ext
        today = datetime.now().strftime('%Y-%m-%d')
        return f"{prefix}{extension}"

    def list_buckets(self):
        """
        Zwraca listę wszystkich dostępnych bucketów.
        """
        if not self.client:
            self.logger.error("Klient S3 nie jest zainicjalizowany")
            return []

        try:
            response = self.client.list_buckets()
            buckets = [bucket['Name'] for bucket in response.get('Buckets', [])]
            return buckets
        except Exception as e:
            self.logger.error(f"Błąd podczas listowania bucketów: {str(e)}")
            return []

    def get_presigned_url(self, object_key, expiration=3600):
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

# Inicjalizacja klienta S3
S3Instance = S3Client(
    access_key=os.getenv("AWS_ACCESS_KEY_ID"),
    secret_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region=os.getenv("AWS_REGION", "eu-north-1"),
    bucket_name=os.getenv("AWS_BUCKET_NAME", "awsbucketv1.2.3")
)




