import tempfile
import shutil
from pathlib import Path

def update_filename(filename, prefix="", suffix=""):
    path_obj = Path(filename)
    base = path_obj.stem
    ext = path_obj.suffix

    return f"{prefix}{base}{suffix}{ext}"

def update_file_ext(filename, new_ext):
    path_obj = Path(filename)
    base = path_obj.stem

    return f"{base}{new_ext}"

def tmp_dir():
    return Path(tempfile.mkdtemp())

def rm_tmp(dir_path):
    shutil.rmtree(dir_path)

def dir_filepath(dir, filename):
    return Path(dir) / filename