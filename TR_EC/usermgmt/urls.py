from django.urls import path
from . import views
from django_cas_ng import views as cas_views


urlpatterns = [
    path('users/', views.PubUserListView.as_view(), name="users"),
    path('users/checkname/', views.check_username, name="user-check"),
    path('user/', views.UserDetailedView.as_view(), name="user"),
#    path('pub/speakerstats/', views.pub_speaker_stats, name="pub-speaker-stats"),
#    path('langs/', views.LanguageListView.as_view(), name="langs"),
#    path('countries/', views.country_list, name="countries"),
#    path('accents/', views.accent_list, name="accents"),
#    path('locale/<lang>', views.MenuLanguageView.as_view(), name="locale"),

    path('auth/login/', cas_views.LoginView.as_view(), name='cas_ng_login'),
    path('auth/logout/', cas_views.LogoutView.as_view(), name='cas_ng_logout'),
]