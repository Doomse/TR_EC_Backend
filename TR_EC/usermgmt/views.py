from django import http
from django.contrib import auth
from rest_framework import status, exceptions, response, generics, decorators, permissions as rf_permissions
from rest_framework.authtoken import models as token_models, views as token_views
from . import permissions, models, serializers


class PubUserListView(generics.ListAPIView):
    '''
    Is used to get a list of users, publishers should use this to assign speakers to their texts(sharedFolders)
    '''
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserBasicSerializer
    permission_classes = [rf_permissions.IsAuthenticated, permissions.IsPublisher]

    def get_queryset(self):
        if 'query' in self.request.query_params:
            name_pre = self.request.query_params['query']
            return models.CustomUser.objects.filter(username__startswith=name_pre)
        else:
            return models.CustomUser.objects.all()


class UserDetailedView(generics.RetrieveUpdateDestroyAPIView):
    '''
    Is used by all users to retrieve and update their data
    '''
    serializer_class = serializers.UserFullSerializer

    def get_object(self):
        return self.request.user
   

@decorators.api_view()
@decorators.permission_classes([])
def check_username(request):
    if not 'username' in request.query_params:
        raise exceptions.NotFound('no username specified')
    username = request.query_params['username']
    available = not models.CustomUser.objects.filter(username=username).exists()
    return response.Response({'available': available}, status=status.HTTP_200_OK)