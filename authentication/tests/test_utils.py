import pytest
import time

from django.test import RequestFactory
from django.http import HttpResponse
from django.urls import reverse

from ..utils import auth_decorator

# request factory will simulate making a real request using our endpoints etc
class TestAuthDecorator:
    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def valid_session_request(self, request_factory):
        """Request with valid user session"""
        request = request_factory.get('/')

    @pytest.fixture
    def google_user(self):
        return {
            'email': 'kamilholb@gmail.com'
        }

    def test_sign_in_oauth(self, request_factory):
        user_data = request_factory.get('/')

