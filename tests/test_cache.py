import datetime
import os
from time import sleep

import pandas as pd
import pytest

from mortality_monitor.cache import DataFrameFileCache
from mortality_monitor.util import read_csv_with_weekly_period

PATH_TO_DATA = "tests/data/mortality_data.csv"
CACHE_TIMEOUT_TIME = 1 / (60 * 60 * 24)


def test_put_data(tmp_path):
    # given
    data_folder = str(tmp_path / "data")
    archive_folder = str(tmp_path / "archive")
    cache = DataFrameFileCache(data_folder=data_folder, archive_folder=archive_folder)
    data = read_csv_with_weekly_period(path=PATH_TO_DATA)

    # when
    cache.put_data(data=data, filename="cached_data_test")

    # then
    assert os.path.isfile(f"{data_folder}/cached_data_test.csv")


@pytest.mark.parametrize(("read_function"), [pd.read_csv, read_csv_with_weekly_period])
def test_get_data(read_function, tmp_path):
    # given
    data_folder = str(tmp_path / "data")
    archive_folder = str(tmp_path / "archive")
    cache = DataFrameFileCache(data_folder=data_folder, archive_folder=archive_folder)
    data = read_function(PATH_TO_DATA)
    cache.put_data(data=data, filename="cached_data_test")

    # when
    result = cache.get_data(filename="cached_data_test", read_function=read_function)

    # then
    pd.testing.assert_frame_equal(result, data)


@pytest.mark.parametrize(("read_function"), [pd.read_csv, read_csv_with_weekly_period])
def test_cache_timeout(read_function, tmp_path):
    # given
    data_folder = str(tmp_path / "data")
    archive_folder = str(tmp_path / "archive")
    cache = DataFrameFileCache(
        data_folder=data_folder,
        archive_folder=archive_folder,
        timeout_hours=CACHE_TIMEOUT_TIME,
    )
    data = read_csv_with_weekly_period(path=PATH_TO_DATA)
    cache.put_data(data=data, filename="cached_data_test")
    today = datetime.datetime.now().strftime("%d_%m_%Y")

    # when and then
    sleep(3600 * CACHE_TIMEOUT_TIME)  # CACHE_TIMEOUT_TIME is in hours
    with pytest.raises(OSError):
        cache.get_data(filename="cached_data_test", read_function=read_function)
    assert os.path.isfile(f"{archive_folder}/{today}_cached_data_test.csv")
    assert not os.path.isfile(f"{data_folder}/cached_data_test.csv")
