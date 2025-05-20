import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(username, password):
        return User.objects.create_user(username=username, password=password)

    return _create_user


@pytest.mark.django_db
def test_obtain_auth_token(api_client, create_user):
    create_user("testuser", "testpassword")
    url = reverse("obtain-auth-token")
    response = api_client.post(
        url, {"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "token" in response.data


@pytest.mark.django_db
def test_obtain_jwt_token(api_client, create_user):
    create_user("testuser", "testpassword")
    url = reverse("token_obtain_pair")
    response = api_client.post(
        url, {"username": "testuser", "password": "testpassword"}
    )
    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_refresh_jwt_token(api_client, create_user):
    create_user("testuser", "testpassword")
    obtain_url = reverse("token_obtain_pair")
    obtain_response = api_client.post(
        obtain_url, {"username": "testuser", "password": "testpassword"}
    )
    refresh_token = obtain_response.data["refresh"]

    refresh_url = reverse("token_refresh")
    refresh_response = api_client.post(refresh_url, {"refresh": refresh_token})
    assert refresh_response.status_code == 200
    assert "access" in refresh_response.data


@pytest.mark.django_db
def test_verify_jwt_token(api_client, create_user):
    create_user("testuser", "testpassword")
    obtain_url = reverse("token_obtain_pair")
    obtain_response = api_client.post(
        obtain_url, {"username": "testuser", "password": "testpassword"}
    )
    access_token = obtain_response.data["access"]

    verify_url = reverse("token_verify")
    verify_response = api_client.post(verify_url, {"token": access_token})
    assert verify_response.status_code == 200
