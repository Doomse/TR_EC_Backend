from django.urls import path
from django.views.generic.base import View
from . import views

urlpatterns = [
    path('edt/corrections/', views.CorrectionView.as_view(), name='corrections'),
    path('edt/corrections/<int:pk>/', views.CorrectionUpdateView.as_view(), name='correction-update'),
    path('edt/corrections/<int:pk>/download/', views.CorrectionDownloadView.as_view(), name='correction-download'),
    # path('edt/edits/', views.EditView.as_view(), name='edits'),
]