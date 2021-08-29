from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from . import models


admin.site.register(models.CustomUser, auth_admin.UserAdmin)