from django.db import models, transaction
from django.core.files import base
from django.core.files.storage import default_storage
from django.contrib import auth
from django.db.models import constraints
from . import utils
from usermgmt import models as user_models
#from editmgmt import models as edit_models
import zipfile, re, json
from pathlib import Path
#from google.cloud.storage import Blob


class Folder(models.Model):
    name = models.CharField(max_length=250)
    owner = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='folder')  
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='subfolder', blank=True, null=True)

    class Meta:
        ordering = ['owner', 'name']
        constraints = [
            # This constraint only applies to non-root folders (i.e. folders where parent != None)
            # Because parent is a foreign key the constraint does not need to include the owner
            models.UniqueConstraint(fields=['name','parent'], name='unique_subfolder'),
            # This constraint only applies to root folders (i.e. folders with parent == None)
            models.UniqueConstraint(fields=['name', 'owner'], condition=models.Q(parent=None), name='unique_folder'),
        ]

    # this method is useful for the shell and for the admin view
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # TODO test, if this is actually not needed, then omit the save method
        # if self.is_shared_folder() and not isinstance(self, SharedFolder):
        #     sf = self.sharedfolder
        #     sf.name = self.name
        #     sf.save()

    #Used for permission checks
    def is_owner(self, user):
        return self.owner == user

    def get_parent_name(self):
        if self.parent == None:
            return None
        return self.parent.name

    def is_shared_folder(self):
        """
        This method returns True if called on a Folder instance for which a corresponding SharedFolder instance exists.
        """
        return hasattr(self, 'sharedfolder')
    
    def get_path(self):
        return utils.folder_relative_path(self)

    def make_shared_folder(self):
        if self.is_shared_folder():
            return self.sharedfolder
        if self.subfolder.all().exists():
            raise TypeError("This folder can't be a shared folder")
        # create SharedFolder instance
        sf = SharedFolder(folder_ptr=self, name=self.name, owner=self.owner, parent=self.parent)
        sf.save()
        # create actual folders and files:
        #sf_path = Path(sf.get_path())
        #logfile = uploadedfile.SimpleUploadedFile('', '')
        #default_storage.save(str(sf_path/'log.txt'), logfile)
        return sf

"""
def stm_upload_path(instance, filename):
    sf_path = instance.get_path()
    title = re.sub(r"[\- ]", "_", instance.name)
    title = title.lower()
    return f'{sf_path}/{title}.stm'


def log_upload_path(instance, filename):
    sf_path = instance.get_path()
    return f'{sf_path}/log.txt'
"""

class SharedFolder(Folder):
    editor = models.ManyToManyField(auth.get_user_model(), related_name='sharedfolder', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    #Used for permission checks
    def is_editor(self, user):
        return self.editor.filter(id=user.id).exists()
    
    def make_shared_folder(self):
        return self
    
    def get_path(self):
        path = super().get_path()
        return path + utils.NAME_ID_SPLITTER + str(self.id)

    def get_readable_path(self):
        path = super().get_path()
        return path

    def create_zip_for_download(self):
        zip_path = self.get_path()+'/download.zip'
        with default_storage.open(zip_path, 'wb') as f:
            with zipfile.ZipFile(f, 'w') as zf:
                for transcript in self.transcription.all():
                    transcript.write_transcripts_to_zip(zf)
        return zip_path
                    

    

def tr_upload_path(instance, filename):
    """
    Generates the upload path for a transcript
    """
    sf_path = Path(instance.shared_folder.sharedfolder.get_path())
    path = sf_path/instance.title/filename
    return path

class Transcription(models.Model):

    title = models.CharField(max_length=100)
    shared_folder = models.ForeignKey(SharedFolder, on_delete=models.CASCADE, related_name='transcription')

    srcfile = models.FileField(upload_to=tr_upload_path)
    trfile = models.FileField(upload_to=tr_upload_path)  # text + timestamps as json

    class Meta:
        ordering = ['shared_folder', 'title']
        constraints = [
            models.UniqueConstraint(fields=['title', 'shared_folder'], name='unique_tr'),
        ]
    
    def get_correction_from(self, user):
        if self.correction.filter(editor=user).exists():
            return self.correction.get(editor=user).id
        return None
    
    def __str__(self) -> str:
        return self.title
    
    #Used for permission checks
    def is_owner(self, user):
        return self.shared_folder.is_owner(user)

    #Used for permission checks
    def is_editor(self, user):
        return self.shared_folder.is_editor(user)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # if not self.phrases.exists():
        #     self.create_phrases()

    # def phrase_count(self):
    #     return self.phrases.count()
    
    # def get_content(self):
    #     content = []
    #     for phrase in self.phrases.all():
    #         content.append(phrase.content)
    #     return content

    # def get_meta_content(self):
    #     content = []
    #     for phrase in self.phrases.all():
    #         content.append({
    #             'index': phrase.index,
    #             'content': phrase.content,
    #             'start': phrase.start,
    #             'end': phrase.end,
    #         })
    #     return content

    # def write_transcripts_to_zip(self, file: zipfile.ZipFile):
    #     with self.srcfile.open('rb') as src_file:
    #         file.writestr(self.srcfile.name.replace(self.shared_folder.get_path(), self.title), src_file.read())
    #     file.writestr(self.title+'/original.txt', '\n'.join(self.get_content()))
    #     for correction in self.correction.all():
    #         filename = 'by_' + correction.editor.username + '_'
    #         if correction.active_phrase > self.phrase_count():
    #             filename += 'completed'
    #         else:
    #             filename += '(' + str(correction.active_phrase) + '/' + self.phrase_count + ')'
    #         filename += '.txt'
    #         file.writestr(self.title+'/'+filename, '\n'.join(correction.get_content()))

    
    # def create_phrases(self):
    #     with transaction.atomic():
    #         if not self.phrases.exists():
    #             #for now we assume the files to be basic json with dict keys start, end, content
    #             with self.trfile.open('r') as json_file:
    #                 data = json.load(json_file)
    #                 for index, json_obj in enumerate(data):
    #                     self.phrases.create(content=json_obj['content'], index=index+1, start=float(json_obj['start']), end=float(json_obj['end']))



# class Phrase(models.Model):
#     transcription = models.ForeignKey(Transcription, on_delete=models.CASCADE, related_name='phrases')
#     content = models.CharField(max_length=500)
#     index = models.IntegerField()
#     start = models.FloatField()
#     end = models.FloatField()

#     class Meta:
#         ordering = ['transcription', 'index']
#         constraints = [
#             models.UniqueConstraint(fields=['transcription', 'index'], name='unique_phrase')
#         ]
    
#     def __str__(self) -> str:
#         return self.transcription.title + " (" + str(self.index) + "): " + self.content