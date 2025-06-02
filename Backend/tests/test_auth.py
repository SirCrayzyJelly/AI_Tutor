import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


# Testira registraciju korisnika putem /register/ rute
@pytest.mark.django_db
def test_user_registration():
    client = APIClient()
    response = client.post("/register/", {
        "username": "testuser",
        "password": "securepassword123"
    }, format='json')
    assert response.status_code == 200
    assert "success" in response.json()["status"]
    

# Testira prijavu korisnika putem /login/ rute nakon što je korisnik kreiran
@pytest.mark.django_db
def test_user_login():
    User.objects.create_user(username="loginuser", password="mypassword")

    client = APIClient()
    response = client.post("/login/", {
        "username": "loginuser",
        "password": "mypassword"
    }, format='json')
    assert response.status_code == 200
    assert "success" in response.json()["status"]
