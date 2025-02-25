import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ..models import UserManager

from faker import Faker

fake = Faker()
User = get_user_model()

@pytest.mark.django_db
class TestUserModel:

    @pytest.fixture
    def valid_user_data(self):
        return {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': 'test_password123'
        }

    @pytest.fixture
    def user(self, valid_user_data):
        return User.objects.create_user(**valid_user_data)

    def test_email_uniqueness(self, valid_user_data):
        User.objects.create_user(self.valid_user_data)

        # Try to create another user with the same email
        with pytest.raises(Exception):  # Could be IntegrityError or ValidationError depending on your implementation
            User.objects.create_user(
                first_name='Another',
                last_name='User',
                email=valid_user_data['email'],
                password='different_password'
            )

    def test_user_str_representation(self, user):
        expected = f"{user.email}"  # Adjust according to your __str__ implementation
        assert str(user) == expected

    def test_email_normalization(self):
        email = 'TEST@Example.Com'
        user = User.objects.create_user(
            first_name='Test',
            last_name='User',
            email=email,
            password='test123'
        )
        assert user.email == 'TEST@example.com'  # Assuming normalize_email is implemented

    def test_username_field(self):
        assert User.USERNAME_FIELD == 'email'

    def test_required_fields(self):
        assert set(User.REQUIRED_FIELDS) == {'first_name', 'last_name'}

@pytest.mark.django_db
class TestUserManager:
    @pytest.fixture
    def user_data(self):
        return {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': 'test_password123'
        }

    def test_user_create(self, user_data):
        user = User.objects.create_user(**user_data)

        # in this section i will check does fields and privilages are fine
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['first_name']
        assert user.is_confirmed == False
        assert user.is_staff == False
        assert user.is_active == True

    def test_admin_user_create(self, user_data):
        user = User.objects.create_superuser(**user_data)

        # in this section i will check does fields and privilages are fine
        assert user.email == user_data['email']
        assert user.first_name == user_data['first_name']
        assert user.last_name == user_data['first_name']
        assert user.is_staff == True
        assert user.is_active == True
        assert user.is_superuser == True

    def test_create_user_without_req_fields(self):
        # Test missing first_name
        with pytest.raises(ValueError, match='User first_name cannot be empty'):
            User.objects.create_user(
                first_name=None,
                last_name='Test',
                email='test@test.com'
            )

        # Test missing last_name
        with pytest.raises(ValueError, match='User last_name cannot be empty'):
            User.objects.create_user(
                first_name='Test',
                last_name=None,
                email='test@test.com'
            )

        # Test missing email
        with pytest.raises(ValueError, match='User email cannot be empty'):
            User.objects.create_user(
                first_name='Test',
                last_name='Test',
                email=None
            )

        with pytest.raises(ValueError, match='User password cannot be empty'):
            User.objects.create_user(
                first_name='Test',
                last_name='Test',
                email=None,
                password=None
            )


