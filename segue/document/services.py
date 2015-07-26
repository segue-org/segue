import re
import codecs
import os.path
import magic

from subprocess import Popen, PIPE
from xml.sax.saxutils import escape

from segue.core import config, logger
from segue.document.errors import DocumentNotFound

class DocumentService(object):
    def __init__(self, override_root=None, template_root=None, magic_impl=None, tmp_dir=None):
        self.template_root = template_root or os.path.join(config.APP_PATH, 'segue')
        self.override_root = override_root
        self.magic         = magic_impl or magic
        self.tmp_dir       = tmp_dir or '/tmp'

    def get_by_hash(self, kind, document_hash):
        root = self.override_root or config.STORAGE_DIR
        filename = "{}-{}".format(kind, document_hash)
        path = self.path_for_filename(root, filename)
        if not os.path.exists(path): raise DocumentNotFound(filename)
        content = open(path,'r').read()
        mimetype = self.magic.from_buffer(content, mime=True)
        return content, mimetype

    def path_for_filename(self, root, filename, ensure_viable=False):
        return os.path.join(self.dir_for_filename(root, filename, ensure_viable), filename)

    def dir_for_filename(self, root, filename, ensure_exists=False):
        kind, top, rest = re.match("^(.*)-(..)(.*)$", filename).groups()
        full_path = os.path.join(root, kind, top)
        if ensure_exists and not os.path.exists(full_path):
            os.makedirs(full_path)
        return full_path

    def all_files_with_kind(self, kind):
        root = self.override_root or config.STORAGE_DIR
        result = []
        for path, dirs, files in os.walk(root):
            if not files: continue
            result.extend([ f for f in files if f.startswith(kind) ])
        return sorted(result)

    def svg_to_pdf(self, template, kind, hash_code, variables=dict()):
        template_path = os.path.join(self.template_root, template)

        with codecs.open(template_path, "rb", "utf8") as template_file:
            content = template_file.read()
            for key, value in variables.items():
                content = content.replace("%%{}%%".format(key), escape(value))

        temp_path = os.path.join(self.tmp_dir, "{}-{}.svg".format(kind, hash_code))
        with codecs.open(temp_path, "wb", "utf8") as temp_file:
            temp_file.write(content)

        logger.info("created %s with length of %d ", temp_path, len(content))

        output_root = self.override_root or config.STORAGE_DIR
        output_path = self.path_for_filename(output_root, "{}-{}.pdf".format(kind, hash_code), ensure_viable=True)

        logger.info("attempting to convert %s to %s", temp_path, output_path)

        command = [ "/usr/bin/inkscape", "-z", "-f", temp_path, "-A", output_path ]
        process = Popen(command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        logger.info("invoked inscape with command %s pid %d", " ".join(command), process.pid)

        process.wait()
        if not os.path.isfile(output_path):
            logger.info("output does not look like a file! dumping stderr and stdout next")
            logger.info(process.stderr.read())
            logger.info(process.stdout.read())
            raise DocumentGenerationFailed()

        return "{}-{}.pdf".format(kind, hash_code)
