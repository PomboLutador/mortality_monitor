import datetime
import os
from time import sleep

import pandas as pd
import pytest

from mortality_monitor.cache import DataFrameFileCache
from mortality_monitor.util import read_csv_with_weekly_period

PATH_TO_DATA = "tests/data/mortality_data.csv"
CACHE_TIMEOUT_TIME = 1 / (60 * 60 * 10)


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
    sleep(0.1)
    with pytest.raises(FileNotFoundError):
        cache.get_data(filename="cached_data_test", read_function=read_function)
    assert os.path.isfile(f"{archive_folder}/{today}_cached_data_test.csv")
    assert not os.path.isfile(f"{data_folder}/cached_data_test.csv")


def test_raises_error_if_data_contains_index_column(tmp_path):
    # given
    data_folder = str(tmp_path / "data")
    archive_folder = str(tmp_path / "archive")
    cache = DataFrameFileCache(
        data_folder=data_folder,
        archive_folder=archive_folder,
        timeout_hours=CACHE_TIMEOUT_TIME,
    )
    data = pd.DataFrame(
        [
            {"index": "abc", "value": 1},
            {"index": "cab", "value": 3},
            {"index": "bca", "value": 5},
        ]
    )

    # when and then
    with pytest.raises(ValueError):
        cache.put_data(data=data, filename="some-filename")


def test_raises_error_if_data_contains_index_named_index(tmp_path):
    # given
    data_folder = str(tmp_path / "data")
    archive_folder = str(tmp_path / "archive")
    cache = DataFrameFileCache(
        data_folder=data_folder,
        archive_folder=archive_folder,
        timeout_hours=CACHE_TIMEOUT_TIME,
    )
    data = pd.DataFrame(
        [
            {"index": "abc", "other_index_column": "def", "value": 1},
            {"index": "cab", "other_index_column": "def", "value": 3},
            {"index": "bca", "other_index_column": "def", "value": 5},
        ]
    ).set_index(["index", "other_index_column"])

    # when and then
    with pytest.raises(ValueError):
        cache.put_data(data=data, filename="some-filename")


def test_raises_error_if_data_contains_exactly_one_index_named_index(tmp_path):
    # given
    data_folder = str(tmp_path / "data")
    archive_folder = str(tmp_path / "archive")
    cache = DataFrameFileCache(
        data_folder=data_folder,
        archive_folder=archive_folder,
        timeout_hours=CACHE_TIMEOUT_TIME,
    )
    data = pd.DataFrame(
        [
            {"index": "abc", "value": 1},
            {"index": "cab", "value": 3},
            {"index": "bca", "value": 5},
        ]
    ).set_index("index")

    # when and then
    with pytest.raises(ValueError):
        cache.put_data(data=data, filename="some-filename")
