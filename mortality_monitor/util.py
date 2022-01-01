from __future__ import annotations

from collections import OrderedDict

import pandas as pd

FROM, TO = (tuple(i for i in range(5, 90, 5)), tuple(i + 4 for i in range(5, 90, 5)))

QUERY_AGES = (
    ("Y_LT5",) + tuple(f"Y{start}-{end}" for start, end in zip(FROM, TO)) + ("Y_GE90",)
)
DATA_AGES = (
    ("Less than 5 years",)
    + tuple(f"From {start} to {end} years" for start, end in zip(FROM, TO))
    + ("90 years or over",)
)
QUERY_AGE_TO_DATA_AGE = OrderedDict(zip(QUERY_AGES, DATA_AGES))


def get_all_age_groups_for_query() -> tuple[str, ...]:
    return tuple(QUERY_AGES)


def get_data_age(query_age: str) -> str:
    """Converts ages as sent in the query to ages as seen in the returned data.

    E.g.: "Y35-39" -> "From 35 to 39 years"
    """
    return QUERY_AGE_TO_DATA_AGE[query_age]


def read_csv_with_weekly_period(path: str) -> pd.DataFrame:
    return pd.read_csv(path).assign(
        period=lambda df: pd.to_datetime(
            df["period"].str.split("/", expand=True)[1]
        ).dt.to_period(freq="W")
    )
