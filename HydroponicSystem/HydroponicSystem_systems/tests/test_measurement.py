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


@pytest.mark.django_db
def test_create_measurement(api_client, user1, hydroponic_system1):
    api_client.force_authenticate(user=user1)
    url = reverse("measurement", args=[hydroponic_system1.id])
    data = {"ph": 6.5, "temperature": 22.5, "tds": 900, "timestamp": "2025-02-16"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert Measurement.objects.filter(system=hydroponic_system1).exists()

@pytest.mark.django_db
def test_create_measurement_invalid_data(api_client, user1, hydroponic_system1):
    api_client.force_authenticate(user=user1)
    url = reverse("measurement", args=[hydroponic_system1.id])
    data = {"ph": 300, "temperature": 22.5, "tds": 900, "timestamp": "2025-02-16"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "ph" in response.data

@pytest.mark.django_db
def test_create_measurement_permission_denied(api_client, user2, hydroponic_system1):
    api_client.force_authenticate(user=user2)
    url = reverse("measurement", args=[hydroponic_system1.id])
    data = {"ph": 6.5, "temperature": 22.5, "tds": 900, "timestamp": "2025-02-16"}
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.django_db
def test_list_measurements(api_client, user1, hydroponic_system1, measurements1):
    api_client.force_authenticate(user=user1)
    url = reverse("measurement", args=[hydroponic_system1.id])
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) <= 10

    if len(measurements1) > 10:
        assert "next" in response.data
        assert response.data["next"] is not None
        assert isinstance(response.data["next"], str) 
    else:
        assert response.data["next"] is None 

@pytest.mark.django_db
def test_filter_measurements_by_ph(api_client, user1, hydroponic_system1, measurements1):
    api_client.force_authenticate(user=user1)
    url = reverse("measurement", args=[hydroponic_system1.id]) + "?ph_min=6.0&ph_max=7.0"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert all(6.0 <= m["ph"] <= 7.0 for m in response.data["results"])

@pytest.mark.django_db
def test_filter_measurements_invalid_date(api_client, user1, hydroponic_system1):
    api_client.force_authenticate(user=user1)
    url = reverse("measurement", args=[hydroponic_system1.id]) + "?timestamp_after=invalid-date"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid timestamp format" in response.data["detail"]

@pytest.mark.django_db
def test_sort_measurements_descending(api_client, user1, hydroponic_system1, measurements1):
    api_client.force_authenticate(user=user1)
    url = reverse("measurement", args=[hydroponic_system1.id]) + "?sort_by=timestamp&sort_order=desc"
    response = api_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    timestamps = [datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ") for m in response.data["results"]]
    assert timestamps == sorted(timestamps, reverse=True)
