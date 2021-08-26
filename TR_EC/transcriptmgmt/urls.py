from django.urls import path
from . import views

urlpatterns = [
    # ideas for better understandable urls:
    # pub/folders/
    path('folders/', views.PubFolderListView.as_view(), name='folders'),
    # pub/folders/<int:pk>/
    path('folders/<int:pk>/', views.PubFolderDetailedView.as_view(), name='folder-detail'),

    path('pub/folders/delete/', views.multi_delete_folders, name='folder-delete'),
    # spk/publishers/
    path('publishers/', views.EditPublisherListView.as_view(), name='publishers'),
    # spk/publishers/<int:pk>/
    path('publishers/<int:pk>/', views.EditPublisherDetailedView.as_view(), name='publisher-detail'),
    
    # pub/sharedfolders/<int:pk>/editors/
    path('sharedfolders/<int:pk>/', views.PubSharedFolderEditorView.as_view(), name='sharedfolder-editors'),
]