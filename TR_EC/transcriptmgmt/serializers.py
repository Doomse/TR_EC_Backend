from rest_framework import serializers
from . import models, utils
from usermgmt import models as user_models, serializers as user_serializers
from recordingmgmt import models as rec_models
import django.core.files.uploadedfile as uploadedfile
import chardet, math


class FolderPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = models.Folder.objects.filter(owner=user, sharedfolder=None)
        return queryset


class FolderFullSerializer(serializers.ModelSerializer):
    """
    to be used by view: PubFolderListView
    for: Folder creation, top-level-folder list retrieval
    """
    parent = FolderPKField(allow_null=True)
    is_sharedfolder = serializers.BooleanField(source='is_shared_folder', read_only=True)
    # is_sharedfolder in the sense that this folder has a corresponding Sharedfolder object with the same pk as this Folder
 
    class Meta:
        model = models.Folder
        fields = ['id', 'name', 'owner', 'parent', 'is_sharedfolder']
        read_only_fields = ['owner']
    
    def validate_name(self, value):
        """
        validates the name field
        """
        if utils.NAME_ID_SPLITTER in value:
            raise serializers.ValidationError('The folder name contains invalid characters "' + utils.NAME_ID_SPLITTER + '"')
        return value

    def validate(self, data):
        """
        validation that has to do with multiple fields of the serializer
        """
        if models.Folder.objects.filter(owner=self.context['request'].user, name=data['name'], parent=data['parent']).exists():
            raise serializers.ValidationError('A folder with the given name in the given place already exists')
        return super().validate(data)

class FolderBasicSerializer(serializers.ModelSerializer):
    """
    to be used by: FolderDetailedSerializer
    """
    is_sharedfolder = serializers.BooleanField(source='is_shared_folder', read_only=True)
    # is_sharedfolder in the sense that this folder has a corresponding Sharedfolder object with the same pk as this Folder
    
    class Meta:
        model = models.Folder
        fields = ['id', 'name', 'is_sharedfolder']
        read_only_fields = ['name']

class FolderDetailedSerializer(serializers.ModelSerializer):
    """
    to be used by view: PubFolderDetailView
    for: retrieval of a Folder with its subfolders
    """
    parent = FolderPKField(allow_null=True)
    is_sharedfolder = serializers.BooleanField(source='is_shared_folder', read_only=True)
    subfolder = FolderBasicSerializer(many=True, read_only=True)
    # is_sharedfolder in the sense that this folder has a corresponding Sharedfolder object with the same pk as this Folder
    
    class Meta:
        model = models.Folder
        fields = ['id', 'name', 'owner', 'parent', 'subfolder', 'is_sharedfolder']
        read_only_fields = fields


class SharedFolderPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = models.Folder.objects.filter(owner=user, subfolder=None)
        return queryset


class SharedFolderEditorSerializer(serializers.ModelSerializer):
    """
    to be used by view: PubSharedFolderEditorView
    for: retrieval and update of the editors of a shared folder
    """
    editor_ids = serializers.PrimaryKeyRelatedField(queryset=user_models.CustomUser.objects.all(), many=True, allow_null=True, source='editor', write_only=True)
    editors = user_serializers.UserBasicSerializer(many=True, read_only=True, source='editor')

    class Meta:
        model = models.SharedFolder
        fields = ['id', 'name', 'editors', 'editor_ids', 'public']
        read_only_fields = ['name']
        depth = 1


class EditPublisherSerializer(serializers.ModelSerializer):
    """
    to be used by view: EditPublisherListView, EditPublisherDetailedView
    for: retrieval of single publisher or list of publishers, who own sharedfolders (freedfolders) shared with request.user
    """
    freedfolders = serializers.SerializerMethodField(read_only=True, method_name='get_freed_folders')

    class Meta:
        model = user_models.CustomUser
        fields = ['id', 'username', 'freedfolders']
        read_only_fields = ['username']
    
    def get_freed_folders(self, obj):
        pub = obj
        spk = self.context['request'].user
        info = []
        for sf in models.SharedFolder.objects.filter(owner=pub, editor=spk):
            info.append({"id": sf.pk, "name": sf.name, "path": sf.get_readable_path()})
        return info

