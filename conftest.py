import pytest
from django.conf import settings
import psycopg2

# settings.configure()

@pytest.fixture
def db_conncection():
    test_db_config = settings.DATABASES['test']
    # Get connection parameters from settings
    db_params = {
        'dbname': test_db_config['NAME'],
        'user': test_db_config['USER'],
        'password': test_db_config['PASSWORD'],
        'host': test_db_config['HOST'],
        'port': test_db_config.get('PORT', '5432'),
        # Default to 5432 for PostgreSQL
    }

    # Create a connection
    conn = psycopg2.connect(**db_params)
    conn.autocommit = False  # Set autocommit mode based on your needs

    yield conn

@pytest.fixture
def db_cursor(db_conncection):
    cursor = db_conncection.cursor()

