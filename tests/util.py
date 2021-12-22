from __future__ import annotations

import os


class CleanUpManager:
    def __init__(
        self, files_to_delete: tuple[str, ...], dirs_to_delete: tuple[str, ...]
    ):
        self.files_to_delete = files_to_delete
        self.dirs_to_delete = dirs_to_delete

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for file_to_delete in self.files_to_delete:
            os.remove(file_to_delete)
        for dir_to_delete in self.dirs_to_delete:
            os.removedirs(dir_to_delete)
