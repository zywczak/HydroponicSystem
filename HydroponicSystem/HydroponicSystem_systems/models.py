from django.db import models

from HydroponicSystem_authentication.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class HydroponicSystem(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Measurement(models.Model):
    system = models.ForeignKey(HydroponicSystem, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    ph = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(14.0)],
    )
    
    temperature = models.FloatField(
        validators=[MinValueValidator(-10.0), MaxValueValidator(50.0)],
    )

    tds = models.IntegerField(
        validators=[MinValueValidator(0)],
    )