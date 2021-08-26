from django.db import models, transaction
from django.core.files import base
from django.core.files.storage import default_storage
from django.contrib import auth
from . import utils
from usermgmt import models as user_models
import zipfile, re
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


def stm_upload_path(instance, filename):
    sf_path = instance.get_path()
    title = re.sub(r"[\- ]", "_", instance.name)
    title = title.lower()
    return f'{sf_path}/{title}.stm'


def log_upload_path(instance, filename):
    sf_path = instance.get_path()
    return f'{sf_path}/log.txt'


class SharedFolder(Folder):
    editor = models.ManyToManyField(auth.get_user_model(), related_name='sharedfolder', blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    #Used for permission checks
    def is_editor(self, user):
        return self.public or self.speaker.filter(id=user.id).exists()
    
    def make_shared_folder(self):
        return self
    
    def get_path(self):
        path = super().get_path()
        return path + utils.NAME_ID_SPLITTER + str(self.id)

    def get_readable_path(self):
        path = super().get_path()
        return path
    

def upload_path(instance, filename):
    """
    Generates the upload path for a text
    """
    sf_path = Path(instance.shared_folder.sharedfolder.get_path())
    path = sf_path/filename
    return path
