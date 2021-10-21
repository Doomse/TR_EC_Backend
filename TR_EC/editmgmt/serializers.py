from django.core import exceptions
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import fields
from rest_framework import serializers
from . import models
from transcriptmgmt import models as transcript_models
import json


class TranscriptPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = transcript_models.Transcription.objects.filter(shared_folder__editor__id=user.id)
        return queryset


class CorrectionCreateSerializer(serializers.ModelSerializer):

    transcription = TranscriptPKField()
    
    class Meta:
        model = models.Correction
        fields = ['id', 'editor', 'transcription']
        read_only_fields = ['editor']

# # currently not in use
# class CorrectionSerializer(serializers.ModelSerializer):

#     transcript = TranscriptPKField()
#     content = serializers.ListField(source='get_meta_content', read_only=True)

#     class Meta:
#         model = models.Correction
#         fields = ['id', 'editor', 'content', 'transcript', 'active_phrase']
#         read_only_fields = ['editor', 'active_phrase']


class CorrectionSerializer(serializers.ModelSerializer):

    # def validate_active_phrase(self, value):
    #     if value <= self.instance.active_phrase:
    #         raise serializers.ValidationError("The active phrase can only be increased")
    #     return value
    content = serializers.JSONField(source='get_content', read_only=True)
    transcription_title = serializers.SerializerMethodField()  # read-only by default
    trfile_json = serializers.JSONField(binary=False, write_only=True)

    class Meta:
        model = models.Correction
        fields = ['id', 'transcription_title', 'content', 'trfile_json'] 
    
    def get_transcription_title(self, obj):
        return obj.transcription.title
    
    def update(self, instance, validated_data):
        # put the json in a file
        validated_data['trfile'] = SimpleUploadedFile("correction.json", bytes(json.dumps(validated_data.pop('trfile_json')), encoding='utf-8'), content_type='text/json')
        return super().update(instance, validated_data)


class CorrectionPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = models.Correction.objects.filter(editor__id=user.id)
        return queryset


# class EditSerializer(serializers.ModelSerializer):

#     correction = CorrectionPKField()

#     #When serializing a model, this field accesses the SentenceRecording index method
#     index = serializers.IntegerField()

#     def validate(self, data):
#         try:
#             index = data.pop('index')
#             correction = data['correction']
#             phrase = correction.transcript.phrases.get(index=index)
#             correction.edits.filter(phrase=phrase).delete()
#         except (KeyError, exceptions.ObjectDoesNotExist):
#             raise serializers.ValidationError("Invalid index")
#         data['phrase'] = phrase
#         return super().validate(data)

#     def validate_index(self, value):
#         if value < 1:
#             raise serializers.ValidationError("Invalid index.")
#         return value

#     class Meta:
#         model = models.Edit
#         fields = ['correction', 'content', 'index']