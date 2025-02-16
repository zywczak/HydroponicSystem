import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'HydroponicSystem.settings'
import django
django.setup()

import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime
from ..models import HydroponicSystem, Measurement, User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user1():
    user = User.objects.create(email="newuser@example.com")
    user.set_password("securepassword")
    user.save()
    return user

@pytest.fixture
def user2():
    user = User.objects.create(email="seconduser@example.com")
    user.set_password("securepassword2")
    user.save()
    return user

@pytest.fixture
def hydroponic_system1(user1):
    return HydroponicSystem.objects.create(owner=user1, name="Test System 1", location="Greenhouse 1")

@pytest.fixture
def hydroponic_system2(user2):
    return HydroponicSystem.objects.create(owner=user2, name="Test System 2", location="Greenhouse 2")

@pytest.fixture
def measurements1(hydroponic_system1):
    measurements = [
        Measurement.objects.create(
            system=hydroponic_system1,
            ph=6.5,
            temperature=22.0,
            tds=800,
            timestamp=datetime(2024, 2, 15, 10, i)
        )
        for i in range(15)
    ]
    return measurements

@pytest.fixture
def measurements2(hydroponic_system2):
    measurements = [
        Measurement.objects.create(
            system=hydroponic_system2,
            ph=6.7,
            temperature=23.0,
            tds=850,
            timestamp=datetime(2024, 2, 15, 11, i)
        )
        for i in range(15)
    ]
    return measurements

@pytest.mark.django_db
def test_create_hydroponic_system(api_client, user1):
    api_client.force_authenticate(user=user1)
    url = reverse("hydroponicsystem-list")
    data = {"name": "My System", "location": "Garden"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["name"] == "My System"
    assert response.data["owner"] == user1.id

@pytest.mark.django_db
def test_retrieve_hydroponic_system(api_client, user1, hydroponic_system1, measurements1):
    api_client.force_authenticate(user=user1)
    url = reverse("hydroponicsystem-detail", args=[hydroponic_system1.id])
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert "latest_measurements" in response.data
    assert len(response.data["latest_measurements"]) == 10

@pytest.mark.django_db
def test_retrieve_hydroponic_system_permission_denied(api_client, user2, hydroponic_system1):
    api_client.force_authenticate(user=user2)
    url = reverse("hydroponicsystem-detail", args=[hydroponic_system1.id])
    response = api_client.get(url)
    print(response.data)
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.django_db
def test_update_hydroponic_system(api_client, user1, hydroponic_system1):
    api_client.force_authenticate(user=user1)
    url = reverse("hydroponicsystem-detail", args=[hydroponic_system1.id])
    data = {"name": "Updated System", "location": "New Greenhouse"}
    response = api_client.put(url, data)
    
    assert response.status_code == status.HTTP_200_OK
    hydroponic_system1.refresh_from_db()
    assert hydroponic_system1.name == "Updated System"

@pytest.mark.django_db
def test_delete_hydroponic_system(api_client, user1, hydroponic_system1):
    api_client.force_authenticate(user=user1)
    url = reverse("hydroponicsystem-detail", args=[hydroponic_system1.id])
    response = api_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not HydroponicSystem.objects.filter(id=hydroponic_system1.id).exists()

@pytest.mark.django_db
def test_list_hydroponic_systems(api_client, user2, hydroponic_system2):
    api_client.force_authenticate(user=user2)
    url = reverse("hydroponicsystem-list") + "?name=Test "
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 1

@pytest.mark.django_db
def test_list_hydroponic_systems_invalid_date(api_client, user1, hydroponic_system1):
    api_client.force_authenticate(user=user1)
    url = reverse("hydroponicsystem-list") + "?created_after=invalid-date"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid date format" in response.data["detail"]
