from django.urls import path
from . import views

urlpatterns = [
    path('edit/corrections/', views.CorrectionView.as_view(), name='corrections'),
    path('edit/edits/', views.EditView.as_view(), name='edits'),
]