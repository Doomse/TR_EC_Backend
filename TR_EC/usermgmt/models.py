from django.db import models, transaction
from django.contrib import auth
from django.contrib.auth import models as auth_models
from . import utils, storages, countries


class CustomUser(auth_models.AbstractUser):
    """
    Custom User Model which represents a TEQST user
    """

    class Meta:
        ordering = ['username']

    def is_publisher(self):
        p = auth_models.Group.objects.get(name='Publisher')
        return p in self.groups.all()