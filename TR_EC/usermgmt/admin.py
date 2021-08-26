from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from . import forms, models


admin.site.register(models.CustomUser, auth_admin.UserAdmin)