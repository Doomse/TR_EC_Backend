from django.core import exceptions
from TR_EC.transcriptmgmt import models
from rest_framework import serializers
from . import models
from transcriptmgmt import models as transcript_models


class TranscriptPKField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        user = self.context['request'].user
        queryset = transcript_models.Transcript.objects.filter(shared_folder__editor__id=user.id)
        return queryset


class CorrectionSerializer(serializers.ModelSerializer):

    transcript = TranscriptPKField()

    class Meta:
        model = models.Correction
        fields = ['id', 'editor', 'transcript', 'active_sentence']
        read_only_fields = ['editor']


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