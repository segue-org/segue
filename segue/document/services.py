import re
import os.path
import magic

from segue.core import config
from segue.document.errors import DocumentNotFound

class DocumentService(object):
    def __init__(self, override_root=None, magic_impl=None):
        self.override_root = override_root
        self.magic         = magic_impl or magic

    def get_by_hash(self, kind, document_hash):
        root = self.override_root or config.STORAGE_DIR
        filename = "{}-{}".format(kind, document_hash)
        path = self.path_for_filename(root, filename)
        if not os.path.exists(path): raise DocumentNotFound(filename)
        content = open(path,'r').read()
        mimetype = self.magic.from_buffer(content, mime=True)
        return content, mimetype

    def path_for_filename(self, root, filename):
        return os.path.join(self.dir_for_filename(root, filename), filename)

    def dir_for_filename(self, root, filename):
        kind, top, rest = re.match("^(.*)-(..)(.*)$", filename).groups()
        return os.path.join(root, kind, top)

    def all_files_with_kind(self, kind):
        root = self.override_root or config.STORAGE_DIR
        result = []
        for path, dirs, files in os.walk(root):
            if not files: continue
            result.extend([ f for f in files if f.startswith(kind) ])
        return result


