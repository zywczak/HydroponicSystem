from django.db import models

from managers import CustomUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission, Group


class User(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(max_length=100, unique=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	USERNAME_FIELD = 'email'
	objects = CustomUserManager()

	groups = models.ManyToManyField(Group, related_name='custom_user_set')

	user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')