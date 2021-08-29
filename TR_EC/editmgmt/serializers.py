from django.core import exceptions
from rest_framework import serializers
from . import models
from transcriptmgmt import models as transcript_models


class TranscriptPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = transcript_models.Transcription.objects.filter(shared_folder__editor__id=user.id)
        return queryset


class CorrectionSerializer(serializers.ModelSerializer):

    transcript = TranscriptPKField()
    content = serializers.ListField(source='get_meta_content', read_only=True)

    class Meta:
        model = models.Correction
        fields = ['id', 'editor', 'content', 'transcript', 'active_phrase']
        read_only_fields = ['editor', 'active_phrase']


class CorrectionUpdateSerializer(serializers.ModelSerializer):

    def validate_active_phrase(self, value):
        if value <= self.instance.active_phrase:
            raise serializers.ValidationError("The active phrase can only be increased")
        return value

    class Meta:
        model = models.Correction
        fields = ['id', 'active_phrase']


class CorrectionPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = models.Correction.objects.filter(editor__id=user.id)
        return queryset


class EditSerializer(serializers.ModelSerializer):

    correction = CorrectionPKField()

    #When serializing a model, this field accesses the SentenceRecording index method
    index = serializers.IntegerField()

    def validate(self, data):
        try:
            index = data.pop('index')
            correction = data['correction']
            phrase = correction.transcript.phrases.get(index=index)
            correction.edits.filter(phrase=phrase).delete()
        except (KeyError, exceptions.ObjectDoesNotExist):
            raise serializers.ValidationError("Invalid index")
        data['phrase'] = phrase
        return super().validate(data)

    def validate_index(self, value):
        if value < 1:
            raise serializers.ValidationError("Invalid index.")
        return value

    class Meta:
        model = models.Edit
        fields = ['correction', 'content', 'index']