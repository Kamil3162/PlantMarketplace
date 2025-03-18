import json

import pytest
from django.test import RequestFactory
from django.urls import reverse

from faker import Faker

from ..models import CustomUser

fake = Faker()

@pytest.mark.django_db
class TestAccountViews:
    """
        We have to concentrate on return data type, we care about json data type
    """

    @pytest.fixture
    def request_factory(self):
        return RequestFactory()

    @pytest.fixture
    def prefix_set_up(self):
        return 'users/api'

    @pytest.fixture
    def create_test_users(self):
        users = []
        for _ in range(25):
            user = CustomUser.objects.create_user(
                username=fake.user_name(),
                last_name=fake.last_name(),
                email=fake.email(),
                password=fake.password(),
            )
            users.append(user)
        return users

    def test_users_list(self, request_factory, prefix_set_up):
        response = request_factory.get(reverse('users_list'))

        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/json'

    def test_users_list_content_structure(self, request_factory):
        response = request_factory.get(reverse('users_list'))
        data = json.loads(response.content)

        assert isinstance(data, list)
        assert len(data) == 25
        assert data[0]['id'] == 1
        assert isinstance(data[0], CustomUser)

    def test_users_list_with_empty_database(self, client):
        """Test behavior when there are no users in the database"""
        # Make sure no users exist
        CustomUser.objects.all().delete()

        response = client.get(reverse('users_list'))
        data = json.loads(response.content)

        assert response.status_code == 200
        assert isinstance(data, list)
        assert len(data) == 0  # Should be an empty list