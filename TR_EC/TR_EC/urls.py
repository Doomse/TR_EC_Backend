from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "TR_EC Administration"
admin.site.site_title = "TR_EC Admin"
admin.site.index_title = "App administration"

urlpatterns = [
    path('api/', include('transcriptmgmt.urls')),
    path('api/', include('usermgmt.urls')),
    path('api/', include('editmgmt.urls')),
    path('admin/', admin.site.urls),
]
