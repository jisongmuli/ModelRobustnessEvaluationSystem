"""Replace JSON metadata atomically, including when a background task saves it."""
import json
import os
import tempfile
from pathlib import Path
from threading import RLock

_lock = RLock()

def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    with _lock:
        try:
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=path.parent,
                                             suffix='.tmp', delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(value, stream, ensure_ascii=False, indent=2, default=str)
                stream.flush()
                os.fsync(stream.fileno())
            temporary.replace(path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
