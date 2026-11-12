import shutil

def compress_folder(folder):
    shutil.make_archive("backup", "gztar", root_dir=folder)