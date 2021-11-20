from django.db import models, utils
from django.contrib import auth
from django.conf import settings
from django.db.models import constraints
from transcriptmgmt import models as transcript_models
from pathlib import Path
import shutil, os, json
from . import storages


def correction_upload_path(instance, filename):
    """
    Generates the upload path for a correction transcript
    """
    sf_path = Path(instance.transcription.shared_folder.sharedfolder.get_path())
    path = sf_path/instance.transcription.title/str(instance.editor.id)/"correction.json"
    return path


class Correction(models.Model):
    """
    Acts as a relation between a user and a transcript and saves all information that are specific to that correction.
    """
    editor = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='correction')
    transcription = models.ForeignKey(transcript_models.Transcription, on_delete=models.CASCADE, related_name='correction')
    trfile = models.FileField(upload_to=correction_upload_path, storage=storages.OverwriteStorage())

    class Meta:
        ordering = ['transcription', 'editor']
        constraints = [
            models.UniqueConstraint(fields=['editor', 'transcription'], name='unique_correction')
        ]

    def save(self, *args, **kwargs):
        if self._state.adding:
            sf_path = Path(self.transcription.shared_folder.sharedfolder.get_path())
            trfile_src_path = self.transcription.trfile.path
            trfile_trg_dir_path = settings.MEDIA_ROOT/sf_path/self.transcription.title/str(self.editor.id)
            # need to create the editor directory upon user creation for shutil.copy.
            # exist_ok, because an editor could be added, removed and readded to a sf.
            os.makedirs(trfile_trg_dir_path, exist_ok=True)
            shutil.copy(trfile_src_path, trfile_trg_dir_path/"correction.json")
            self.trfile.name = f"{sf_path}/{self.transcription.title}/{self.editor.id}/correction.json"
        super().save()

    #Used for permission checks
    def is_owner(self, user):
        return self.transcription.is_owner(user)

    #Used for permission checks
    def is_editor(self, user):
        return self.editor == user
    
    def get_content(self):
        return json.load(self.trfile)



"""
class Edit(models.Model):
    ""
    Stores the edits made by the editor
    ""
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
"""
