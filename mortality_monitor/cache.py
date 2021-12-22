import datetime
import os
from dataclasses import dataclass
from typing import Callable

import pandas as pd


@dataclass(frozen=True)
class DataFrameFileCache:
    data_folder: str
    file_extension: str = "csv"
    timeout_hours: float = 24.0
    archive_folder: str = "archive"

    def put_data(self, data: pd.DataFrame, filename: str) -> None:
        if not os.path.isdir(self.data_folder):
            os.makedirs(self.data_folder)

        if self.file_extension == "csv":
            data.to_csv(
                f"{self.data_folder}/{filename}.{self.file_extension}", index=False
            )
        else:
            raise NotImplementedError("Please use an implemented file extension")

    def get_data(self, filename: str, read_function: Callable) -> pd.DataFrame:
        if self._check_if_file_already_exists(filename=filename):
            if self._is_timedout(filename=filename):
                print("The file exists but not up to date - please get new data")
                print("Archiving old file now ...")
                self._archive_data(filename=filename)
                raise IOError(
                    "The file exists but not up to date - please get new data"
                )
            if self.file_extension == "csv":
                print(f"Reading csv {filename} from disk")
                return read_function(
                    f"{self.data_folder}/{filename}.{self.file_extension}"
                )
            else:
                raise NotImplementedError(
                    "This file extension is not implemented yet, pick another one"
                )
        else:
            print("This file does not exist - please cache it first")
            raise IOError("This file does not exist - please cache it first")

    def _archive_data(self, filename: str) -> None:
        if not os.path.isdir(self.archive_folder):
            os.makedirs(self.archive_folder)

        os.rename(
            f"{self.data_folder}/{filename}.{self.file_extension}",
            (
                f"{self.archive_folder}/"
                f"{datetime.datetime.now().strftime('%d_%m_%Y')}_{filename}"
                f".{self.file_extension}"
            ),
        )

    def _check_if_file_already_exists(self, filename: str) -> bool:
        return os.path.isfile(f"{self.data_folder}/{filename}.{self.file_extension}")

    def _is_timedout(self, filename: str):
        last_modified_date_of_file = datetime.datetime.fromtimestamp(
            os.stat(f"{self.data_folder}/{filename}.{self.file_extension}").st_mtime
        ).replace(tzinfo=datetime.timezone.utc)
        return (
            datetime.datetime.now(datetime.timezone.utc) - last_modified_date_of_file
        ) > (datetime.timedelta(hours=self.timeout_hours))