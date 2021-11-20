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
   

class UserRegisterView(generics.CreateAPIView):
    '''
    Is used to register a new user to the system
    Obviously no permission requirements
    '''
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserRegisterSerializer
    permission_classes = []


class GetAuthToken2(token_views.ObtainAuthToken):
    """
    This is the view used to log in a user (get his Authentication Token)
    """
    permission_classes = []

    def post(self, request, *args, **kwargs):
        resp = super(GetAuthToken2, self).post(request, *args, **kwargs)
        token = token_models.Token.objects.get(key=resp.data['token'])
        user = models.CustomUser.objects.get(id=token.user_id)
        user_serializer = serializers.UserFullSerializer(user, many=False)
        return response.Response({'token': token.key, 'user': user_serializer.data})


class GetAuthToken(token_views.ObtainAuthToken):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = token_models.Token.objects.get_or_create(user=user)
        #return Response({'token': token.key})
        user_serializer = serializers.UserFullSerializer(user, many=False)
        return response.Response({'token': token.key, 'created': created, 'user': user_serializer.data}, status=status.HTTP_200_OK)


@decorators.api_view(['POST'])
@decorators.permission_classes([])
def login(request):
    try:
        username = request.data['username']
        password = request.data['password']
        user = auth.authenticate(username=username, password=password)
        if not user:
            raise exceptions.NotAuthenticated('Invalid credentials')
        token, created = token_models.Token.objects.get_or_create(user=user)
        user_serializer = serializers.UserFullSerializer(user, many=False)
        return response.Response({'token': token.key, 'created': created, 'user': user_serializer.data}, status=status.HTTP_200_OK)
    except KeyError:
        raise exceptions.NotAuthenticated('No credentials provided')


@decorators.api_view(['POST'])
def logout(request):
    token = request.auth 
    token.delete()
    return response.Response('Logout successful!', status=status.HTTP_200_OK)


@decorators.api_view()
@decorators.permission_classes([])
def check_username(request):
    if not 'username' in request.query_params:
        raise exceptions.NotFound('no username specified')
    username = request.query_params['username']
    available = not models.CustomUser.objects.filter(username=username).exists()
    return response.Response({'available': available}, status=status.HTTP_200_OK)