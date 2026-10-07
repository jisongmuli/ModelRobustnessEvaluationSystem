"""Bounded ZIP extraction into a newly generated dataset directory."""
from pathlib import Path, PurePosixPath
import shutil
import stat
import zipfile

MAX_EXPANDED_SIZE = 1024 * 1024 * 1024
MAX_ARCHIVE_FILES = 20000

def extract_dataset(archive_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    with zipfile.ZipFile(archive_path) as archive:
        members = archive.infolist()
        if len(members) > MAX_ARCHIVE_FILES or sum(member.file_size for member in members) > MAX_EXPANDED_SIZE:
            raise ValueError('压缩包解压后过大或文件数量超过限制')
        for member in members:
            name = PurePosixPath(member.filename.replace('\\', '/'))
            if name.is_absolute() or '..' in name.parts or any(':' in part for part in name.parts):
                raise ValueError('压缩包包含非法路径')
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError('压缩包不能包含符号链接')
            if '__MACOSX' in name.parts or name.name in ('.DS_Store', 'Thumbs.db'):
                continue
            target = (destination / str(name)).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError('压缩包路径超出数据集目录')
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as source, target.open('wb') as stream:
                    shutil.copyfileobj(source, stream)
    children = list(destination.iterdir())
    # A single class containing images is already a valid root: do not flatten it.
    if len(children) == 1 and children[0].is_dir() and any(child.is_dir() for child in children[0].iterdir()):
        return children[0]
    return destination
