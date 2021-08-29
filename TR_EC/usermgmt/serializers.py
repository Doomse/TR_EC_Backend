from rest_framework import serializers
from . import models


class UserFullSerializer(serializers.ModelSerializer):
    '''
    Is used to retrieve a list of all users
    '''
    class Meta():
        model = models.CustomUser
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username']


class UserBasicSerializer(serializers.ModelSerializer):
    '''
    Is used to retrieve a list of all users
    '''
    class Meta():
        model = models.CustomUser
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class UserRegisterSerializer(serializers.ModelSerializer):
    '''
    Is used to retrieve a list of all users
    '''
    class Meta():
        model = models.CustomUser
        fields = ['id', 'username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True, 'required': True}}