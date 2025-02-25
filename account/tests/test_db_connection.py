from django.db import connections
import pytest

@pytest.mark.django_db
def test_db_connection():
    connection = connections['default']
    print(connection.settings_dict)
    assert False

