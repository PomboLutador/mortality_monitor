from __future__ import annotations

import pandas as pd

FROM, TO = (tuple(i for i in range(5, 90, 5)), tuple(i + 4 for i in range(5, 90, 5)))

QUERY_AGE_TO_DATA_AGE = {
    "Y_LT5": "Less than 5 years",
    **{
        f"Y{start}-{end}": f"From {start} to {end} years"
        for start, end in zip(FROM, TO)
    },
    "Y_GE90": "90 years or over",
}


def get_all_age_groups_for_query() -> tuple[str, ...]:
    return tuple(QUERY_AGE_TO_DATA_AGE.keys())


def get_data_age(query_age: str) -> str:
    """Converts ages as sent in the query to ages as seen in the returned data.

    E.g.: "Y35-39" -> "From 35 to 39 years"
    """
    return QUERY_AGE_TO_DATA_AGE[query_age]


def read_csv_with_weekly_period(path: str) -> pd.DataFrame:
    return pd.read_csv(path).assign(
        period=lambda df: pd.to_datetime(
            df["period"].str.split("/", expand=True)[1]
        ).dt.to_period(freq="W-MON")
    )
