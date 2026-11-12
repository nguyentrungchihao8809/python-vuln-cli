import os

def compress_folder(folder):
    os.system(f"tar -czf backup.tar.gz {folder}")