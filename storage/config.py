import os
from dataclasses import dataclass
import dotenv

dotenv.load_dotenv()

@dataclass
class MinioConfig:
    end_point: str = os.getenv('MINIO_HOST')
    access_key: str = os.getenv('MINIO_ROOT_USER')
    secret_key: str = os.getenv('MINIO_ROOT_PASSWORD')