from rest_framework import generics, response, status, views, exceptions, decorators, permissions as rf_permissions
from django import http
from django.db.models import Q
from django.core.files.storage import default_storage
from . import models, serializers
from usermgmt import models as user_models, permissions
from pathlib import Path


@decorators.api_view(['POST'])
@decorators.permission_classes([rf_permissions.IsAuthenticated, permissions.IsPublisher])
def multi_delete_folders(request):
    result, _ = request.user.folder.filter(id__in=request.data).delete()
    if result == 0:
        raise exceptions.NotFound('No folders matched your list of ids')
    return response.Response(status=204)


class PubFolderListView(generics.ListCreateAPIView):
    """
    url: api/folders/
    use: list the topmost layer of folders for a publisher, folder creation
    """
    queryset = models.Folder.objects.all()
    serializer_class = serializers.FolderFullSerializer
    permission_classes = [rf_permissions.IsAuthenticated, permissions.IsPublisher]

    def get_queryset(self):
        user = self.request.user
        #the use of the parent param is deprecated. you should get this info with folderDetailView
        if 'parent' in self.request.query_params:
            if not models.Folder.objects.filter(pk=self.request.query_params['parent']).exists():
                raise exceptions.NotFound("parent not found")
            if models.Folder.objects.get(pk=self.request.query_params['parent']).is_shared_folder():
                raise exceptions.NotFound("parent not found")
            #if parent is a sharedfolder: error message
            return models.Folder.objects.filter(parent=self.request.query_params['parent'], owner=user.pk)

        return models.Folder.objects.filter(parent=None, owner=user.pk)  # parent=None means the folder is in the topmost layer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PubFolderDetailedView(generics.RetrieveDestroyAPIView):
    """
    url: api/folders/:id/
    use: retrieve a Folder with its subfolders, Folder deletion
    """
    queryset = models.Folder.objects.all()
    serializer_class = serializers.FolderDetailedSerializer
    permission_classes = [rf_permissions.IsAuthenticated, permissions.IsPublisher, permissions.IsOwner]


class PubSharedFolderEditorView(generics.RetrieveUpdateAPIView):
    """
    url: api/sharedfolders/:id/
    use: retrieve and update the editors of a shared folder
    """
    queryset = models.SharedFolder.objects.all()
    serializer_class = serializers.SharedFolderEditorSerializer
    permission_classes = [rf_permissions.IsAuthenticated, permissions.IsPublisher, permissions.IsOwner]


class EditPublisherListView(generics.ListAPIView):
    """
    url: api/publishers/
    use: get list of publishers who own sharedfolders shared with request.user
    """
    queryset = user_models.CustomUser.objects.all()
    serializer_class = serializers.EditPublisherSerializer

    def get_queryset(self):
        # does not check for is_publisher. This is not necessary

        # possible alternative solution
        # return CustomUser.objects.filter(folder__sharedfolder__editors=self.request.user)
        # current code
        user = self.request.user
        pub_pks = user.sharedfolder.all().values_list('owner', flat=True)
        return user_models.CustomUser.objects.filter(pk__in = pub_pks)


class EditPublisherDetailedView(generics.RetrieveAPIView):
    """
    url: api/publishers/:id/
    use: in speak tab: retrieve a publisher with their folders which they shared with request.user
    """
    queryset = user_models.CustomUser.objects.all()
    serializer_class = serializers.EditPublisherSerializer

    def get_object(self):
        pub = super().get_object()
        user = self.request.user
        if user.sharedfolder.filter(owner=pub).exists():
            return pub
        raise exceptions.PermissionDenied('This publisher has not shared any folders with you as editor.')

