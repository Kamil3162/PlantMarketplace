import uuid

import minio
import urllib3

from django.db.models import ImageField

from .config import  MinioConfig

class MinioCLient:
    def __init__(self, minioConfig: MinioConfig):
        self.config = minioConfig
        self.client = minio.Minio(
            "localhost:9000",
            self.config.access_key,
            self.config.secret_key,
            secure=False,
            http_client=urllib3.PoolManager(
            num_pools=10
            )
        )

    def create_bucket(self, bucket_name):
        try:
            # check bucket existance
            bucket_exist = self.bucket_exists(bucket_name)
            if not bucket_exist:
                bucket = self.client.make_bucket(
                    bucket_name=bucket_name
                )
                return True
            else:
                print('Bucket already exist')
                return False
        except minio.error.S3Error as e:
            print(f'Error creating bucket: {str(e)}')
            raise

    def bucket_exists(self, bucket_name):
        try:
            bucket = self.client.bucket_exists(bucket_name)
            return bucket
        except minio.error.ServerError as e:
            raise minio.error.ServerError(str(e))

    def list_aviable_buckets(self):
        try:
            buckets = self.client.list_buckets()
            print("Bucket List:")
            for bucket in buckets:
                print(f"{bucket.name}, Created:{bucket.creation_date}")
            return buckets
        except minio.error.MinioException:
            raise minio.error.MinioException(str(e))
        except minio.error.ServerError:
            raise minio.error.ServerError(str(e))

    def delete_bucket(self, bucket_name):
        try:
            bucket_exist = self.bucket_exists(bucket_name)
            if not bucket_exist:
                bucket = self.client.remove_bucket(
                    bucket_name=bucket_name
                )
                return True
            else:
                print('Bucket already exist')
                return False
        except minio.error.S3Error as e:
            print(f'Error creating bucket: {str(e)}')
            raise

    def insert_image(self, bucket_name, file):
        """
        Upload an image from a Django ImageField to a MinIO bucket.

        Args:
            bucket_name (str): Name of the bucket to upload to
            file (ImageFieldFile): Django ImageField file to upload
            object_name (str, optional): Custom name for the object. If not provided,
                                         a UUID will be generated.
            content_type (str, optional): Content type of the file. If not provided,
                                          it will be guessed from the file extension.

        Returns:
            dict: Information about the uploaded image including URL
        """
        try:
            bucket = self.bucket_exists(bucket_name)
            if not bucket:
                self.create_bucket(bucket_name)
            id = uuid.uuid4()
            _, file_extenstion = file.split(".")[-1]
            file_indentifier = f"{id}.{file_extenstion}"
            content_type = mimetypes.guess_type(uploaded_file.name)[0] or 'application/octet-stream'
            file_data= file.read()

            # Upload directly to MinIO
            result = self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(file_data),  # Wrap in BytesIO for streaming
                length=len(file_data),
                content_type=content_type
            )
            return "Test"
        except Exception as e:
            raise Exception(str(e))

#
# # if __name__ == '__main__':
# config = MinioConfig()
# client_storage = MinioCLient(minioConfig=config)
# client_storage.list_aviable_buckets()
# client_storage.create_bucket('product-images')
