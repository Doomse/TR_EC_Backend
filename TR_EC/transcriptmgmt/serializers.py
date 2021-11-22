from django.db.models import fields
from rest_framework import serializers
from . import models, utils
from usermgmt import models as user_models, serializers as user_serializers

import django.core.files.uploadedfile as uploadedfile



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


class TranscriptionFullSerializer(serializers.ModelSerializer):
    """
    to be used by view: PubTranscriptListView, PubTranscriptDetailedView, EditTranscriptDetailedView
    for: transcription creation and retrieval
    """
    #content = serializers.ListField(source='get_meta_content', read_only=True)
    content = serializers.JSONField(source='get_content', read_only=True)
    shared_folder = SharedFolderPKField()
    format = serializers.CharField(write_only=True)

    class Meta:
        model = models.Transcription
        fields = ['id', 'title', 'shared_folder', 'srcfile', 'trfile', 'content', 'format']
        extra_kwargs = {'srcfile': {'write_only': True}, 'trfile': {'write_only': True}}
    
    def validate(self, data):
        if models.Transcription.objects.filter(shared_folder=data['shared_folder'], title=data['title']).exists():
            raise serializers.ValidationError("A Transcription with this title in this folder already exists")
        return super().validate(data)
    
    def create(self, validated_data):
        sf = validated_data['shared_folder']
        sf = sf.make_shared_folder()
        validated_data['shared_folder'] = sf
        format = validated_data.pop('format')
        obj = super().create(validated_data)
        utils.convert_tr_from_format(obj, format)
        return obj


class TranscriptionBasicSerializer(serializers.ModelSerializer):
    """
    to be used by view: PubTranscriptListView
    for: retrieval of a list of Transcriptions contained in a sharedfolder
    """
    class Meta:
        model = models.Transcription
        fields = ['id', 'title']


class EditTranscriptionInfoSerializer(serializers.ModelSerializer):
    """
    """
    correction = serializers.SerializerMethodField()

    class Meta:
        model = models.Transcription
        fields = ['id', 'title', 'correction']
    
    def get_correction(self, obj):
        user = self.context['request'].user
        return obj.get_correction_from(user)


class EditSharedFolderTranscriptSerializer(serializers.ModelSerializer):
    """
    to be used by view: EditTranscriptListView
    for: retrieval of a list of Transcriptions contained in a sharedfolder
    """
    transcripts = EditTranscriptionInfoSerializer(read_only=True, many=True, source='transcription')
    path = serializers.CharField(read_only=True, source='get_readable_path')

    class Meta:
        model = models.SharedFolder
        fields = ['id', 'name', 'owner', 'transcripts', 'path']
        read_only_fields = ['name', 'owner']


class SharedFolderEditorSerializer(serializers.ModelSerializer):
    """
    to be used by view: PubSharedFolderEditorView
    for: retrieval and update of the editors of a shared folder
    """
    editor_ids = serializers.PrimaryKeyRelatedField(queryset=user_models.CustomUser.objects.all(), many=True, allow_null=True, source='editor', write_only=True)
    editors = user_serializers.UserBasicSerializer(many=True, read_only=True, source='editor')

    class Meta:
        model = models.SharedFolder
        fields = ['id', 'name', 'editors', 'editor_ids']
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

