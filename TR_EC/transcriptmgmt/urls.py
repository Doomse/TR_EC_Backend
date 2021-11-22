from django.urls import path
from . import views

urlpatterns = [

    path('folders/', views.PubFolderListView.as_view(), name='folders'),

    path('folders/<int:pk>/', views.PubFolderDetailedView.as_view(), name='folder-detail'),

    path('pub/folders/delete/', views.multi_delete_folders, name='folder-delete'),

    path('publishers/', views.EditPublisherListView.as_view(), name='publishers'),

    path('publishers/<int:pk>/', views.EditPublisherDetailedView.as_view(), name='publisher-detail'),

    path('pub/transcripts/formats/', views.TranscriptionFormatView.as_view()),
    
    path('pub/transcripts/', views.PubTranscriptListView.as_view(), name='pub-transcripts'),

    path('pub/transcripts/multiupload/', views.PubTranscriptMultiUploadView.as_view()), 

    path('edt/sharedfolders/<int:pk>/', views.EditTranscriptListView.as_view(), name='sharedfolder-detail'),

    path('sharedfolders/<int:pk>/', views.PubSharedFolderEditorView.as_view(), name='sharedfolder-editors'),

    path('pub/sharedfolders/<int:pk>/download/', views.PubSharedFolderDownloadView.as_view(), name='sharedfolder-download'),

    path('pub/transcripts/<int:pk>/', views.PubTranscriptDetailedView.as_view(), name='pub-transcript-detail'),

    path('pub/transcripts/delete/', views.multi_delete_transcriptions, name='transcript-multi-delete'),

    path('edt/transcripts/<int:pk>/', views.EditTranscriptDetailedView.as_view(), name='edt-transcript-detail'),

    path('transcripts/<int:pk>/download/', views.EditTranscriptDownloadView.as_view(), name='transcript-download'),

    
]