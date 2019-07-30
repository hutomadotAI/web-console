import os
import logging
import datetime
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__)


class KnowledgeBaseFile(models.Model):
    path = models.CharField(max_length=4096)
    name = models.CharField(max_length=128)
    size = models.IntegerField()
    last_update = models.IntegerField()

    @classmethod
    def create(cls, path, name, size, last_update):
        file = cls(path=path, name=name, size=size, last_update=last_update)
        return file

    def delete(self):
        if self.path and os.path.exists(self.path):
            try:
                logger.warn('removing file ' + self.path)
                os.remove(self.path)
                return True
            except OSError as e:
                logger.error('Could not remove file', extra = {'filename': self.path, 'error': e})

        return False


class KnowledgeBaseFileBundle(models.Model):
    devid = models.CharField(max_length=50)
    aiid = models.CharField(max_length=50)
    files = []

    def _ensure_path_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path, mode=0o755, exist_ok=True)

    @property
    def basepath(self):
        return '{basepath}/{devid}/{aiid}'.format(
            basepath=settings.KB_BASE_DIR,
            devid=self.devid,
            aiid=self.aiid)

    @classmethod
    def create(cls, devid, aiid):
        bundle = cls(devid=devid, aiid=aiid)
        return bundle


    def scan_folder(self):
        path = self.basepath
        self._ensure_path_exists(path)
        self.files = []
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file() and not entry.is_dir() and not entry.name.startswith('.'):
                    stat = entry.stat()
                    file = KnowledgeBaseFile.create(
                        path = '{}/{}'.format(self.basepath, entry.name),
                        name = entry.name, 
                        size = stat.st_size, 
                        last_update = stat.st_mtime
                    )
                    self.files.append(file)

        return self.files

    def delete(self, filename=None):
        self.scan_folder()
        for file in self.files:
            if filename is None or file.name==filename:
                result = file.delete()
                if not result:
                    return False
        return True   

    def upload(self, uploaded_files):
        for uploaded_file in uploaded_files:
            destination = '{basepath}/{devid}/{aiid}/{filename}'.format(
                basepath=settings.KB_BASE_DIR,
                devid=self.devid,
                aiid=self.aiid,
                filename=uploaded_file.name)
            with open(destination, 'wb+') as f_dest:
                for chunk in uploaded_file.chunks():
                    f_dest.write(chunk)
        return True         
