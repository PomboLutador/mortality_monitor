from __future__ import annotations

import pandas as pd

from constants import (
    AGE_COLUMN,
    DEATHS_COLUMN,
    DEATHS_PER_MILLION_COLUMN,
    GEO_COLUMN,
    PERIOD_COLUMN,
    POPULATION_COLUMN,
)
from eurostat import get_mortality_data, get_population_data
from util import get_data_age

_YEAR_COLUMN = "year"


def get_deaths(
    mortality_data: pd.DataFrame,
    geo: str,
    ages: tuple[str, ...],
) -> pd.Series:
    """Gets aggregated deaths.

    Args:
        mortality_data: Table containing deaths per geo, age and weekly period.
        geo: Region for which to get aggregated deaths per million.
        ages: Ages for which to get aggregated deaths per million. Of the form
            'Y35-39', 'Y-40-44', etc. with the exception of 'Y_LT5' and 'Y_GT90'.

    Returns:
        Table containing deaths for each period for the chosen geo and age groups.
    """
    return (
        mortality_data.reset_index()
        .pipe(_filter_geo, geo=geo)
        .pipe(_aggregate_across_ages, ages=ages)
    ).set_index(PERIOD_COLUMN)[DEATHS_COLUMN]


def get_deaths_per_million(
    mortality_data: pd.DataFrame,
    population_data: pd.DataFrame,
    geo: str,
    ages: tuple[str, ...],
) -> pd.Series:
    """Gets aggregated deaths per million.

    Args:
        mortality_data: Table containing deaths per geo, age and weekly period.
        population_data: Table containing population on January 1st per geo, age and
            yearly period.
        geo: Region for which to get aggregated deaths per million.
        ages: Ages for which to get aggregated deaths per million. Of the form
            'Y35-39', 'Y-40-44', etc. with the exception of 'Y_LT5' and 'Y_GT90'.

    Returns:
        Table containing deaths per million for each period for the chosen geo and age
        groups.
    """
    return (
        pd.merge(
            left=(
                mortality_data.reset_index()
                .pipe(_get_year_column)
                .pipe(_filter_geo, geo=geo)
                .pipe(_aggregate_across_ages, ages=ages)
            ),
            right=(
                population_data.reset_index()
                .pipe(_get_year_column)
                .pipe(_filter_geo, geo=geo)
                .pipe(_aggregate_across_ages, ages=ages)
                .drop(columns=PERIOD_COLUMN)
            ),
            on=[GEO_COLUMN, _YEAR_COLUMN],
            how="left",
        )
        .assign(deaths_per_million=lambda df: df[DEATHS_COLUMN] / df[POPULATION_COLUMN])
        .set_index(PERIOD_COLUMN)[DEATHS_PER_MILLION_COLUMN]
    )


def _get_year_column(data: pd.DataFrame) -> pd.DataFrame:
    return data.assign(
        year=lambda df: df[PERIOD_COLUMN].map(lambda period: period.year)
    )


def _filter_geo(data: pd.DataFrame, geo: str) -> pd.DataFrame:
    return data.loc[data[GEO_COLUMN] == geo, :]


def _aggregate_across_ages(data: pd.DataFrame, ages: tuple[str]) -> pd.DataFrame:
    return (
        data.loc[
            data[AGE_COLUMN].isin([get_data_age(query_age=age) for age in ages]), :
        ]
        .groupby([GEO_COLUMN, PERIOD_COLUMN], as_index=False)
        .sum()
    )


if __name__ == "__main__":
    AVAILABLE_AGES = ("Y35-39", "Y_LT5", "Y_GE90")
    REQUESTED_AGES = ("Y35-39", "Y_GE90")
    mortality_data = get_mortality_data(geo="country", ages=AVAILABLE_AGES)
    population_data = get_population_data(geo="country", ages=AVAILABLE_AGES)
    deaths = get_deaths_per_million(
        mortality_data=mortality_data,
        population_data=population_data,
        geo="Finland",
        ages=REQUESTED_AGES,
    )
