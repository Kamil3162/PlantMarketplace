import pytest
from django.test import TestCase
from ..forms import RegisterForm, LoginForm
from faker import Faker

from django.contrib.auth import get_user_model
User = get_user_model()

fake = Faker()
class TestRegisterForm(TestCase):
    def setUp(self):
        '''
            Setup runs before each test method
        '''
        self.valid_data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': 'test_password123'
        }

        self.invalid_data = self.valid_data.copy()
        self.invalid_data['email'] = 'testemail@'

    def test_user_create_by_valid_form(self):
        register_form = RegisterForm(self.valid_data)
        self.assertEqual(register_form.is_valid(), True)

        user = register_form.save()
        self.assertEqual(user.first_name, self.valid_data['first_name'])
        self.assertEqual(user.last_name, self.valid_data['last_name'])
        self.assertEqual(user.email, self.valid_data['email'])

    def test_user_create_by_invalid_form(self):
        form = RegisterForm(self.invalid_data)
        self.assertEqual(form.is_valid(), False)


class TestLoginForm(TestCase):
    @classmethod
    def setUpClass(cls):
        '''
            Prepare user data from login form test
        '''
        cls.valid_data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'password': fake.password()
        }

        cls.invalid_data = {
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': 'testxyz',
            'password': fake.password()
        }

    def test_user_create_by_valid_form(self):
        register_form = RegisterForm(self.valid_data)
        self.assertEqual(register_form.is_valid(), True)

    def test_user_create_by_invalid_form(self):
        form = LoginForm(self.invalid_data)
        self.assertEqual(form.is_valid(), True)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_form_login_based_on(self):
        self.assertEqual(LoginForm.Meta.model, User)