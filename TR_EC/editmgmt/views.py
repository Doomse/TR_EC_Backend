from django.core import exceptions
from rest_framework import generics, status, response, exceptions as rf_exceptions
from . import serializers, models
from transcriptmgmt import models as transcript_models


class CorrectionView(generics.ListCreateAPIView):

    queryset = models.Correction.objects.all()
    serializer_class = serializers.CorrectionSerializer

    def get_queryset(self):
        user = self.request.user
        try:
            transcript = transcript_models.Transcript.objects.get(id=self.request.query_params['transcript'], shared_folder__editor = user)
            return models.Correction.objects.filter(transcript = transcript, editor = user)
        except (KeyError, ValueError, exceptions.ObjectDoesNotExist):
            raise rf_exceptions.ValidationError("Invalid text id")

    
    def perform_create(self, serializer):
        # specify request.user as the editor of a correction upon creation
        serializer.save(editor=self.request.user)

    def get(self, *args, **kwargs):
        """
        handles the get request
        """
        resp = super().get(*args, **kwargs)
        if not self.get_queryset().exists():
            #response.status_code = status.HTTP_204_NO_CONTENT
            resp = response.Response(status=status.HTTP_204_NO_CONTENT)
        return resp

class EditView(generics.CreateAPIView):

    queryset = models.Edit.objects.all()
    serializer_class = serializers.EditSerializer