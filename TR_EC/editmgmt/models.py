from django.db import models, utils
from django.contrib import auth
from transcriptmgmt import models as transcript_models


class Correction(models.Model):
    """
    Acts as a relation between a user and a transcript and saves all information that are specific to that correction.
    """
    editor = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE)
    transcript = models.ForeignKey(transcript_models.Transcript, on_delete=models.CASCADE)

    active_sentence = models.PositiveIntegerField(default=1)

    #Used for permission checks
    def is_owner(self, user):
        return self.transcript.is_owner(user)

    #Used for permission checks
    def is_editor(self, user):
        return self.editor == user


class Edit(models.Model):
    """
    Stores the edits made by the editor
    """
    correction = models.ForeignKey(Correction, on_delete=models.CASCADE, related_name='edits')
    phrase = models.ForeignKey(transcript_models.Phrase, on_delete=models.CASCADE, related_name='edits')

    content = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        #This check can't be a db constraint, since those don't support cross-table lookups.
        #Because of that, it is moved to the next closest spot.
        if self.correction.transcript != self.phrase.transcript:
            raise utils.IntegrityError('Transcript reference is ambiguos')

        super().save(*args, **kwargs)

    #Used for permission checks
    def is_owner(self, user):
        return self.correction.is_owner(user)

    #Used for permission checks
    def is_editor(self, user):
        return self.correction.is_editor(user)

    def index(self):
        return self.phrase.index