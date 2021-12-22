import pandas as pd

from mortality_monitor.constants import (
    AGE_COLUMN,
    DEATHS_COLUMN,
    GEO_COLUMN,
    PERIOD_COLUMN,
)
from mortality_monitor.util import read_csv_with_weekly_period


def test_read_csv_with_weekly_period():
    # when
    result = read_csv_with_weekly_period(path="tests/data/mortality_data.csv")

    # then
    expected = pd.DataFrame(
        [
            {
                PERIOD_COLUMN: pd.Period("2015-02-09/2015-02-15", freq="W"),
                GEO_COLUMN: "Albania",
                AGE_COLUMN: "From 10 to 14 years",
                DEATHS_COLUMN: 0.0,
            },
            {
                PERIOD_COLUMN: pd.Period("2021-12-06/2021-12-12", freq="W"),
                GEO_COLUMN: "Bulgaria",
                AGE_COLUMN: "From 10 to 14 years",
                DEATHS_COLUMN: 1.0,
            },
            {
                PERIOD_COLUMN: pd.Period("2000-01-31/2000-02-06", freq="W"),
                GEO_COLUMN: "Switzerland",
                AGE_COLUMN: "From 10 to 14 years",
                DEATHS_COLUMN: 3.0,
            },
        ]
    )
    pd.testing.assert_frame_equal(result, expected)
