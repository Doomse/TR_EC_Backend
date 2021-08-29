from django.db import models, utils
from django.contrib import auth
from django.db.models import constraints
from transcriptmgmt import models as transcript_models


class Correction(models.Model):
    """
    Acts as a relation between a user and a transcript and saves all information that are specific to that correction.
    """
    editor = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='correction')
    transcript = models.ForeignKey(transcript_models.Transcription, on_delete=models.CASCADE, related_name='correction')

    active_phrase = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['transcript', 'editor']
        constraints = [
            models.UniqueConstraint(fields=['editor', 'transcript'], name='unique_correction')
        ]

    #Used for permission checks
    def is_owner(self, user):
        return self.transcript.is_owner(user)

    #Used for permission checks
    def is_editor(self, user):
        return self.editor == user

    def get_content(self):
        content = []
        for phrase in self.transcript.phrases.all():
            try: 
                edit = self.edits.get(phrase=phrase)
                content.append(edit.content)
            except Edit.DoesNotExist:
                content.append(phrase.content)
        return content

    def get_meta_content(self):
        content = []
        for phrase in self.transcript.phrases.all():
            try:
                edit = self.edits.get(phrase=phrase)
                content.append({
                    'index': phrase.index,
                    'content': edit.content,
                    'start': phrase.start,
                    'end': phrase.end,
                })
            except Edit.DoesNotExist:
                content.append({
                    'index': phrase.index,
                    'content': phrase.content,
                    'start': phrase.start,
                    'end': phrase.end,
                })
        return content


class Edit(models.Model):
    """
    Stores the edits made by the editor
    """
    correction = models.ForeignKey(Correction, on_delete=models.CASCADE, related_name='edits')
    phrase = models.ForeignKey(transcript_models.Phrase, on_delete=models.CASCADE, related_name='edits')

    content = models.CharField(max_length=200)

    class Meta:
        ordering = ['correction', 'phrase']
        constraints = [
            models.UniqueConstraint(fields=['correction', 'phrase'], name='unique_edit')
        ]

    def save(self, *args, **kwargs):
        #This check can't be a db constraint, since those don't support cross-table lookups.
        #Because of that, it is moved to the next closest spot.
        if self.correction.transcript != self.phrase.transcription:
            raise utils.IntegrityError('Transcript reference is ambiguos')

        if self.phrase.index >= self.correction.active_phrase:
            self.correction.active_phrase = self.phrase.index + 1
            self.correction.save()

        super().save(*args, **kwargs)

    #Used for permission checks
    def is_owner(self, user):
        return self.correction.is_owner(user)

    #Used for permission checks
    def is_editor(self, user):
        return self.correction.is_editor(user)

    def index(self):
        return self.phrase.index