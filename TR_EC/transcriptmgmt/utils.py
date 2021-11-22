import os, json
from django.conf import settings
from django.core.files.base import ContentFile
import zipfile
from pathlib import Path
from . import models, trformats

NAME_ID_SPLITTER = '__'


def folder_relative_path(folder):
    dirs = []
    user = str(folder.owner.username)
    while folder != None:  # go through the folders
        dirs.append(str(folder.name))
        folder = folder.parent
    dirs.append(user)
    dirs.reverse()
    media_path = '/'.join(dirs)
    return media_path


def create_transcriptions_from_zipfile(sharedfolder: int, zfile: zipfile.ZipFile, format: str):

    def zinfo_endswith(zinfo: zipfile.ZipInfo, *formats):
        for format in formats:
            if zinfo.filename.endswith(format):
                return True
        return False
    
    extension, _, _ = trformats.formats[format]

    sf = models.SharedFolder.objects.get(pk=sharedfolder)
    sf_path = Path(sf.get_path())
    zinfo_list = zfile.infolist()
    for zinfo in zinfo_list:
        # zinfo.filename example: "myzipfolder/mytitle/myaudio.mp3"

        # if it is a file and not a directory, skip
        # This is essentially only a safety check, bc file zipinfos
        # are later dynamically removed from zinfo_list
        if not zinfo.filename.endswith('/'):
            continue
        # help: "a/b/".split('/') == ['a', 'b', '']
        _, tr_title, _ = zinfo.filename.split('/')
        # find zipinfo objects of src and tr file
        zinfo_src = list(filter(lambda x: tr_title in x.filename and zinfo_endswith(x, 'wav', 'mp3', 'mp4'), zinfo_list))[0]
        zinfo_tr = list(filter(lambda x: tr_title in x.filename and zinfo_endswith(x, extension), zinfo_list))[0]
        # removing the file zipinfos from zinfo_list dynamically,
        # so that the for loop effectively only loops over folder zipinfos.
        zinfo_list.remove(zinfo_src)
        zinfo_list.remove(zinfo_tr)
        # change zipinfo filenames from 'a/b/c.mp3' to 'c.mp3'
        # This is need to extract them to a custom location.
        zinfo_src.filename = os.path.basename(zinfo_src.filename)
        zinfo_tr.filename = os.path.basename(zinfo_tr.filename)

        path_base = sf_path/tr_title
        
        # actual extraction
        os.makedirs(settings.MEDIA_ROOT/path_base, exist_ok=True)
        zfile.extract(zinfo_src, settings.MEDIA_ROOT/path_base)
        zfile.extract(zinfo_tr, settings.MEDIA_ROOT/path_base)
        # create Transcription object
        new_transcription = models.Transcription(title=tr_title, shared_folder=sf)
        # assign files
        new_transcription.srcfile.name = str(path_base/zinfo_src.filename)
        new_transcription.trfile.name = str(path_base/zinfo_tr.filename)
        # save
        new_transcription.save()
        # convert from format to trjson
        convert_tr_from_format(new_transcription, format)


def convert_tr_from_format(obj, format: str):
    _, to_trjson, _ = trformats.formats[format]
    content = ''
    with obj.trfile.open() as f:
        content = f.read().decode()
    content_trjson = to_trjson(content)
    # TODO delete the old file
    obj.trfile = ContentFile(json.dumps(content_trjson), name='transcription.json')
    obj.save()


#Deprecated, since absolute paths aren't used anymore
def folder_path(folder):
    media_path = folder_relative_path(folder)
    path = settings.MEDIA_ROOT/media_path
    return path
