import pytest
import faker

from django.contrib.auth import get_user_model
from ..utils import get_user


fake = faker.Faker()
User = get_user_model()

@pytest.mark.django_db
class TestGetUser:
    @pytest.fixture
    def user_data(self):
        return {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': 'test'
        }

    @pytest.fixture
    def create_user(self, user_data):
        return User.objects.create(**user_data)

    def test_get_user(self, create_user):
        user = get_user(create_user.id)

        assert user.first_name == create_user.get('first_name')
        assert user.last_name == create_user.get('last_name')
        assert user.email == create_user.get('email')

    def test_get_user_not_found(self):
        with pytest.raises(User.DoesNotExist):
            get_user(fake.user_id)

    def test_get_user_by_invalid_id(self):
        assert get_user('test') is None