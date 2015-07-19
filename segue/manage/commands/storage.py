import os

from segue.core import config

from segue.document.services import DocumentService

from support import *

def folderize(commit=False):
    init_command()

    documents = DocumentService()
    root = config.STORAGE_DIR

    dirs_to_create = set()
    files_to_move  = []

    for filename in os.listdir(root):
        full_path = os.path.join(root, filename)
        if os.path.isdir(full_path): continue

        new_dir  = documents.dir_for_filename(root, filename)
        new_path = documents.path_for_filename(root, filename)
        dirs_to_create.add(new_dir)
        files_to_move.append( (full_path,new_path) )

    for new_dir in dirs_to_create:
        print "{}trying to create {}{}{}...".format(F.RESET, F.GREEN, new_dir, F.RESET),
        if os.path.exists(new_dir):
            print "{}already there!{}".format(F.YELLOW, F.RESET)
        elif commit:
            os.makedirs(new_dir)
            print "{}created!{}".format(F.GREEN, F.RESET)
        else:
            print "{}would create if --commit was on{}".format(F.YELLOW, F.RESET)

    for origin, destination in files_to_move:
        print "{}moving {}{}{} to {}{}{}...".format(F.RESET,
                F.RED,   origin,      F.RESET,
                F.GREEN, destination, F.RESET
        ),
        if os.path.exists(destination):
            print "{}already there!{}".format(F.YELLOW, F.RESET)
        elif commit:
            os.rename(origin, destination)
            print "{}moved!{}".format(F.GREEN, F.RESET)
        else:
            print "{}would move if --commit was on{}".format(F.YELLOW, F.RESET)

    if commit:
        print "run {}find {}{} to check if things look right".format(F.GREEN, root, F.RESET)
