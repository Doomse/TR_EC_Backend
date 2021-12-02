from django.contrib import admin
from django.urls import path, include
from django_cas_ng import views as cas_views

admin.site.site_header = "TR_EC Administration"
admin.site.site_title = "TR_EC Admin"
admin.site.index_title = "App administration"

urlpatterns = [
    path('api/', include('transcriptmgmt.urls')),
    path('api/', include('usermgmt.urls')),
    path('api/', include('editmgmt.urls')),
    path('admin/', admin.site.urls),
    path('', cas_views.LoginView.as_view(), name='cas_ng_login'),
    path('logout/', cas_views.LogoutView.as_view(), name='cas_ng_logout'),
]
