import pytest
import time

from django.test import RequestFactory, Client

from django.http import HttpResponse
from django.urls import reverse

from ..utils import auth_decorator

@pytest.mark.django_db
class TestAuthDecorator:
    # TODO: test entire oauth2 mechanism
    @pytest.fixture
    def request_factory(self):
        """
            Request factory fixture used to generate simulate real application
            request using api endpoint
        Returns:

        """
        return RequestFactory()

    @pytest.fixture
    def google_user(self):
        """
            We generate real life email string to check does oauth2 mechanism
            will work fine
        Returns:
            dict - emial
        """
        return {
            'email': 'kamilholb@gmail.com'
        }

    def valid_session_request(self, request_factory):
        """Request with valid user session in oauth2 context"""
        request = request_factory.get('/')
        assert request.session.get('user_data') is not None



