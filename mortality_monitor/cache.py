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
        """Caches data by saving it as a csv.

        Args:
            data: Data to cache as a csv.
            filename: Name of the csv file the data is saved to.

        Raises:
            If the data contains a column named 'index' a ValueError is raised.
        """
        if "index" in data.columns:
            raise ValueError("No column can be named 'index'.")

        def drop_index_column(data: pd.DataFrame) -> pd.DataFrame:
            return data.drop(columns="index") if "index" in data.columns else data

        if not os.path.isdir(self.data_folder):
            os.makedirs(self.data_folder)
        data.reset_index().pipe(drop_index_column).to_csv(
            f"{self.data_folder}/{filename}.{self.file_extension}", index=False
        )

    def get_data(self, filename: str, read_function: Callable) -> pd.DataFrame:
        """Reads data from csv file if possible.

        Args:
            filename: Name of the csv file for which to look for.
            read_function: Callable which consumes path to csv and outputs the data.

        Returns:
            Table containing the data in the csv.
        Raises:
            FileNotFoundError if the file is timed out or has not been cached before.
        """
        if self._file_already_exists(filename=filename):
            if self._is_timedout(filename=filename):
                self._archive_data(filename=filename)
                raise FileNotFoundError(f"File {filename} has timed out.")
            return read_function(f"{self.data_folder}/{filename}.{self.file_extension}")
        else:
            raise FileNotFoundError(
                f"This {filename} does not exist - please cache it first"
            )

    def _archive_data(self, filename: str) -> None:
        """Moves file from data- to archive folder and adds date of archiving."""
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

    def _file_already_exists(self, filename: str) -> bool:
        return os.path.isfile(f"{self.data_folder}/{filename}.{self.file_extension}")

    def _is_timedout(self, filename: str) -> bool:
        last_modified_date_of_file = datetime.datetime.fromtimestamp(
            os.stat(f"{self.data_folder}/{filename}.{self.file_extension}").st_mtime
        ).replace(tzinfo=datetime.timezone.utc)
        return (
            datetime.datetime.now(datetime.timezone.utc) - last_modified_date_of_file
        ) > (datetime.timedelta(hours=self.timeout_hours))
