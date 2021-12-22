import datetime
import os
from time import sleep

import pandas as pd
import pytest

from mortality_monitor.cache import DataFrameFileCache
from mortality_monitor.util import read_csv_with_weekly_period
from tests.util import CleanUpManager

DATA_FOLDER = "tests/cache/data"
ARCHIVE_FOLDER = "tests/cache/archive"
CACHE_TIMEOUT_TIME = 0.1 / (60 * 60 * 24)


def test_put_data():
    # given
    cache = DataFrameFileCache(data_folder=DATA_FOLDER, archive_folder=ARCHIVE_FOLDER)
    data = read_csv_with_weekly_period(path="tests/data/mortality_data.csv")

    # when
    cache.put_data(data=data, filename="cached_data_test")

    # then
    with CleanUpManager(
        files_to_delete=(f"{DATA_FOLDER}/cached_data_test.csv",),
        dirs_to_delete=(DATA_FOLDER,),
    ):
        assert os.path.isfile(f"{DATA_FOLDER}/cached_data_test.csv")


@pytest.mark.parametrize(("read_function"), [pd.read_csv, read_csv_with_weekly_period])
def test_get_data(read_function):
    # given
    cache = DataFrameFileCache(data_folder=DATA_FOLDER, archive_folder=ARCHIVE_FOLDER)
    data = read_function("tests/data/mortality_data.csv")
    cache.put_data(data=data, filename="cached_data_test")

    # when
    result = cache.get_data(filename="cached_data_test", read_function=read_function)

    # then
    with CleanUpManager(
        files_to_delete=(f"{DATA_FOLDER}/cached_data_test.csv",),
        dirs_to_delete=(DATA_FOLDER,),
    ):
        pd.testing.assert_frame_equal(result, data)


@pytest.mark.parametrize(("read_function"), [pd.read_csv, read_csv_with_weekly_period])
def test_cache_timeout(read_function):
    # given
    cache = DataFrameFileCache(
        data_folder=DATA_FOLDER,
        archive_folder=ARCHIVE_FOLDER,
        timeout_hours=CACHE_TIMEOUT_TIME,
    )
    data = read_csv_with_weekly_period(path="tests/data/mortality_data.csv")
    cache.put_data(data=data, filename="cached_data_test")

    # when and then

    with CleanUpManager(
        files_to_delete=(
            f"{ARCHIVE_FOLDER}/{datetime.datetime.now().strftime('%d_%m_%Y')}_cached_data_test.csv",
        ),
        dirs_to_delete=(DATA_FOLDER, ARCHIVE_FOLDER),
    ):
        sleep(CACHE_TIMEOUT_TIME)
        with pytest.raises(OSError):
            cache.get_data(filename="cached_data_test", read_function=read_function)

        assert os.path.isfile(
            f"{ARCHIVE_FOLDER}/{datetime.datetime.now().strftime('%d_%m_%Y')}_cached_data_test.csv"
        )
