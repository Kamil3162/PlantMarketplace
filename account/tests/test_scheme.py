import pytest
from django.contrib.auth import get_user_model
from faker import Faker
from django.test import TestCase
from ..scheme import UserScheme

fake = Faker()

class TestUserScheme(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_data = {
            'id': None,  # Using int since Django's default ID is AutoField
            'first_name': 'John',
            'last_name': 'Dave',
            'email': 'john@example.com',
            'password': 'test123',
            'is_staff': False,
            'is_confirmed': False
        }

        cls.test_user = get_user_model().objects.create_user(
            first_name=cls.test_data['first_name'],
            last_name=cls.test_data['last_name'],
            email=cls.test_data['email'],
            password=cls.test_data['password'],
            is_staff=cls.test_data['is_staff'],
            is_confirmed=cls.test_data['is_confirmed']
        )

        # update test id data after create a new user
        cls.test_data['id'] = cls.test_user.id

    def test_user_scheme_creation(self):
        user_scheme = UserScheme.by_django_user(self.test_user)

        self.assertEqual(user_scheme.id, self.test_data['id'])
        self.assertEqual(user_scheme.first_name, self.test_data['first_name'])
        self.assertEqual(user_scheme.last_name, self.test_data['last_name'])
        self.assertEqual(user_scheme.email, self.test_data['email'])

    def test_convert_scheme_to_dict(self):
        user_scheme = UserScheme(**self.test_data).to_dict()

        self.assertEqual(type(user_scheme), dict)

    def test_default_values(self):
        test_data = {
            'id': 1,
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john@example.com'
        }
        user_scheme = UserScheme(**test_data)

        self.assertEqual(user_scheme.is_staff, UserScheme.is_staff)
        self.assertEqual(user_scheme.is_confirmed, UserScheme.is_confirmed)

    @classmethod
    def tearDownClass(cls):
        cls.test_user.delete()
        super().tearDownClass()