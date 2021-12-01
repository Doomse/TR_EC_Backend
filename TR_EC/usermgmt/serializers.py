from rest_framework import serializers
from . import models


class UserFullSerializer(serializers.ModelSerializer):
    '''
    
    '''
    # same name as model function
    is_publisher = serializers.BooleanField(read_only=True)

    class Meta():
        model = models.CustomUser
        fields = ['id', 'username', 'is_publisher']
        read_only_fields = ['id', 'username']


class UserBasicSerializer(serializers.ModelSerializer):
    '''
    Is used to retrieve a list of all users
    '''
    class Meta():
        model = models.CustomUser
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


