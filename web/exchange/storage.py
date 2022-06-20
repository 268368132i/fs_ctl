from .models import Settings
import os.path

def check_dir(path):
    return os.path.isdir(path)
