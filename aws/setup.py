from setuptools import setup, find_packages

setup(
    name="aws",
    version="1.0.0",
    description="AWS S3 client with file operations for Django and FastAPI",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.39.3",
        "python-dotenv>=0.19.0",
        "Django>=4.0.0"
    ],
    python_requires=">=3.9",
)