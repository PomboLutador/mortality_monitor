from __future__ import annotations

import datetime as dt
from typing import Iterable

import pandas as pd
from pyjstat import pyjstat  # type: ignore

from mortality_monitor.constants import (
    AGE_COLUMN,
    COUNTRIES,
    DEATHS_COLUMN,
    GEO_COLUMN,
    PERIOD_COLUMN,
    POPULATION_COLUMN,
    SINCE_TIME_PERIOD,
)

_MORTALITY_TABLE = "demo_r_mweek3"
_POPULATION_TABLE = "demo_r_pjangrp3"
_BASE_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "{table}?format=JSON&lang=EN"
)
_PRECISION = "1"
_UNIT = "NR"
_SEX = "T"
_WEEKDAY = "0"

_UNIT_COLUMN = "Unit of measure"
_SEX_COLUMN = "Sex"
_TIME_COLUMN = "Time"
_VALUE_COLUMN = "value"

_1_MILLION = 1000000


def get_mortality_data(
    geos: tuple[str, ...],
    ages: Iterable[str],
) -> pd.DataFrame:
    """Gets weekly mortality data from EUROSTAT.

    Data comes from the demo_r_mweek3 table on Eurostat:
        https://ec.europa.eu/eurostat/data/database?node_code=demomwk

    The table contains weekly deaths per 5-year age group and region.
    For more information on the NUTS classification of regions, see here:
        https://ec.europa.eu/eurostat/web/nuts/background

    Args:
        ages: Ages for which to get data for.
        geo: At which region granularity to get data for.

    Returns:
        A table containing deaths per age group, geo and weekly period.
    """
    return (
        pyjstat.Dataset.read(_build_query(geos=geos, ages=ages, table=_MORTALITY_TABLE))
        .write("dataframe")
        .pipe(_preprocess_mortality_data)
    )


def _preprocess_mortality_data(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.pipe(_drop_week_99_rows)
        .drop(columns=[_UNIT_COLUMN, _SEX_COLUMN])
        .pipe(_create_weekly_period)
        .set_index([GEO_COLUMN, AGE_COLUMN], append=True)
        .dropna()
        .rename(columns={_VALUE_COLUMN: DEATHS_COLUMN})
    )


def _drop_week_99_rows(data: pd.DataFrame) -> pd.DataFrame:
    data = data.copy()
    data["week"] = data[_TIME_COLUMN].str.split("W", expand=True)[1]
    return data.loc[data["week"] != "99"]


def get_population_data(
    geos: tuple[str, ...],
    ages: Iterable[str],
) -> pd.DataFrame:
    """Gets population data from EUROSTAT.

    Data comes from the demo_r_pjangrp3 table on Eurostat:
        https://ec.europa.eu/eurostat/data/database?node_code=demo_r_pjangrp3

    The table contains population per age group and region on January 1st.
    For more information on the NUTS classification of regions, see here:
        https://ec.europa.eu/eurostat/web/nuts/background

    Args:
        ages: Ages for which to get data for.
        geo: At which region granularity to get data for.

    Returns:
        A table containing population in millions on January 1st per age group, geo
        and yearly period.
    """
    return (
        pyjstat.Dataset.read(
            _build_query(geos=geos, ages=ages, table=_POPULATION_TABLE)
        )
        .write("dataframe")
        .pipe(_preprocess_population_data)
    )


def _preprocess_population_data(data: pd.DataFrame) -> pd.DataFrame:
    return (
        data.drop(columns=[_UNIT_COLUMN, _SEX_COLUMN])
        .dropna()
        .pipe(_create_yearly_period)
        .set_index([GEO_COLUMN, AGE_COLUMN], append=True)
        .pipe(_propagate_values_to_current_year)
        .assign(**{POPULATION_COLUMN: lambda df: df[_VALUE_COLUMN] / _1_MILLION})
        .drop(columns=_VALUE_COLUMN)
    )


def _build_query(
    geos: tuple[str, ...],
    ages: Iterable[str],
    table: str,
    sex: str = _SEX,
    since_time_period: str = SINCE_TIME_PERIOD,
) -> str:
    age_string = "age=" + "age=".join([f"{age}&" for age in ages])
    geo_string = "geo=" + "geo=".join([f"{geo}&" for geo in geos])
    return (
        f"{_BASE_URL.format(table=table)}&sinceTimePeriod={since_time_period}"
        f"&{geo_string}{age_string}sex={sex}&unit={_UNIT}"
    )


def _propagate_values_to_current_year(data: pd.DataFrame) -> pd.DataFrame:
    """Makes sure every year up until the current year has a value.

    This implementation simply forward-fills NAs with the nearest value.
    """
    return (
        pd.merge(  # type: ignore
            left=data.reset_index().loc[:, [GEO_COLUMN, AGE_COLUMN]].drop_duplicates(),
            right=pd.DataFrame(
                {
                    PERIOD_COLUMN: pd.period_range(
                        start=data.reset_index()[PERIOD_COLUMN].min(),
                        end=pd.Period(dt.date.today().year, freq="Y"),
                    )
                }
            ),
            how="cross",
        )
        .set_index([PERIOD_COLUMN, AGE_COLUMN, GEO_COLUMN])
        .join(data)
        .groupby([AGE_COLUMN, GEO_COLUMN])
        .apply(pd.DataFrame.interpolate)
    )


def _create_weekly_period(
    data: pd.DataFrame, split_character: str = "-W", time_format: str = "%G-%V-%w"
) -> pd.DataFrame:
    """Turns 'time' column into a weekly period index."""
    return (
        data.assign(
            **{
                PERIOD_COLUMN: lambda df: pd.to_datetime(
                    df[_TIME_COLUMN].str.replace(split_character, "-") + f"-{_WEEKDAY}",
                    format=time_format,
                ).dt.to_period(freq="W")
            }
        )
        .set_index(PERIOD_COLUMN)
        .drop(columns=[_TIME_COLUMN])
    )


def _create_yearly_period(data: pd.DataFrame, time_format: str = "%Y") -> pd.DataFrame:
    """Turns 'time' column into a yearly period index."""
    return (
        data.assign(
            period=lambda df: pd.to_datetime(
                df[_TIME_COLUMN],
                format=time_format,
            ).dt.to_period(freq="Y")
        )
        .set_index(PERIOD_COLUMN)
        .drop(columns=[_TIME_COLUMN])
    )


if __name__ == "__main__":
    AGES = ["Y_LT5", "Y35-39", "Y_GE90"]
    mortality_data = get_mortality_data(geos=COUNTRIES, ages=AGES)
    print(mortality_data)
