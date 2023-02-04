from __future__ import annotations

from statistics import mean, stdev
from typing import Iterable

import numpy as np
import pandas as pd

from mortality_monitor.constants import COUNTRIES, GEO_COLUMN

_1_YEAR = 52
_STANDARD_DEVIATION_PRECISION = 1


def get_expected_deaths(deaths: pd.Series, lookback_years: int = 5) -> pd.Series:
    """Gets expected deaths based on prior actual deaths.

    A prediction for a given period is computed as follows:
        - Get observations 1 year prior, 2 years prior, etc. for each lookback year.
        - Remove all outliers in this set of observations. This is done by computing
            lower and upper bounds via mean +- standard deviation. All values outside
            the bounds are removed. The mean of the leftover values is the base of the
            prediction.
        - Compute the yearly aggregates between lookback period 1 and 2, lookback
            period 2 and 3, etc. for a maximum of lookback_years number of years. The
            minimum considered is 2 years.
        - The yearly aggregates are normalized with respect to the first observation.
            A linear regression is computed on the normalized values and used to
            predict growth for the year of the prediction.
        - The base and the growth are combined via base x growth to predict the value.

    Args:
        deaths: Data containing actual deaths. Must contain enough data for the number
            of lookback years.
        lookback_years: Number of years prior to each datapoint to consider for its
            prediction.

    Returns:
        Data containing expected deaths for each period in original data. The data used
        to bootstrap the first observation is left as is.
    """

    def _predict_datapoint(entry: pd.Series) -> float:
        period, _ = entry
        prior_periods = _get_lookback_periods(
            period=period, lookback_years=lookback_years
        )
        yearly_values = _get_prior_yearly_values(
            data=deaths, prior_periods=prior_periods
        )
        years = _get_prior_years(data=deaths, prior_periods=prior_periods)
        polyfit = np.polyfit(
            x=years,
            y=yearly_values,
            deg=1,
        )
        return (
            np.mean(_get_prior_weekly_values(data=deaths, prior_periods=prior_periods))
            * (np.polyval(p=polyfit, x=period.year))
            / yearly_values[0]
        )

    def _predict(data: pd.Series) -> pd.Series:
        data = data.copy()
        data.iloc[lookback_years * _1_YEAR :] = (
            data.iloc[lookback_years * _1_YEAR :]
            .reset_index()
            .apply(_predict_datapoint, axis=1)
        )
        return data

    return deaths.pipe(_predict)


def _get_lookback_periods(
    period: pd.Period,
    lookback_years: int,
    offset: int = _1_YEAR,
) -> tuple[pd.Period, ...]:
    return tuple(period - offset * (i + 1) for i in range(lookback_years))


def _get_prior_weekly_values(
    data: pd.Series, prior_periods: tuple[pd.Periods, ...]
) -> tuple[float, ...]:
    return _get_rid_of_outliers(values=(data.loc[(data.index.isin(prior_periods))]))


def _get_prior_yearly_values(
    data: pd.Series, prior_periods: tuple[pd.Period, ...]
) -> tuple[np.float64, ...]:
    return tuple(
        data.loc[(data.index >= start - _1_YEAR) & (data.index < (start))].sum()
        for start in prior_periods
        if ((start - _1_YEAR).year >= data.index.min().year)
    )


def _get_prior_years(
    data: pd.Series, prior_periods: tuple[pd.Period, ...]
) -> tuple[int, ...]:
    return tuple(
        (start - _1_YEAR).year
        for start in prior_periods
        if ((start - _1_YEAR).year >= data.index.min().year)
    )


def _get_rid_of_outliers(values: Iterable[float]) -> tuple[float, ...]:
    upper_range = mean(values) + 1.0 * stdev(values) + _STANDARD_DEVIATION_PRECISION
    lower_range = mean(values) - 1.0 * stdev(values) - _STANDARD_DEVIATION_PRECISION
    return tuple(
        weekly_value
        for weekly_value in values
        if (weekly_value < upper_range) & (weekly_value > lower_range)
    )


if __name__ == "__main__":
    import matplotlib.pyplot as plt  # type: ignore

    from mortality_monitor.deaths import get_deaths
    from mortality_monitor.eurostat import get_mortality_data
    from mortality_monitor.util import QUERY_AGE_TO_DATA_AGE

    below_65s = ("Y_LT5",) + tuple(
        f"Y{start}-{end}"
        for start, end in zip(
            tuple(i for i in range(5, 65, 5)), tuple(i + 4 for i in range(5, 65, 5))
        )
    )
    over_65s = tuple(
        f"Y{start}-{end}"
        for start, end in zip(
            tuple(i for i in range(65, 90, 5)), tuple(i + 4 for i in range(65, 90, 5))
        )
    ) + ("Y_GE90",)

    AVAILABLE_AGES = tuple(QUERY_AGE_TO_DATA_AGE.keys())
    mortality_data = get_mortality_data(geos=COUNTRIES, ages=AVAILABLE_AGES)
    for lookback_years in (3, 4, 5):
        for GEO in tuple(mortality_data.reset_index()[GEO_COLUMN].unique()):
            for AGE_GROUP in (below_65s, over_65s):

                deaths = get_deaths(
                    mortality_data=mortality_data,
                    geo=GEO,
                    ages=AGE_GROUP,
                )
                age_string = "65+" if AGE_GROUP == over_65s else "<65"
                print(f"Working on country {GEO} and age group {age_string}")
                expected_deaths = get_expected_deaths(
                    deaths=deaths, lookback_years=lookback_years
                )

                plt.plot(
                    [period.to_timestamp() for period in deaths.index],
                    deaths.values,
                    label=f"Actuals - {age_string}",
                    linestyle=":" if AGE_GROUP == over_65s else "--",
                    color="red",
                )
                plt.plot(
                    [period.to_timestamp() for period in expected_deaths.index],
                    expected_deaths.values,
                    label=f"Expected - {age_string}",
                    linestyle=":" if AGE_GROUP == over_65s else "--",
                    color="blue",
                )
                plt.title(f"{GEO}")
                plt.legend(loc="best")
            plt.savefig(f"plots/2023/{GEO}_LB_YEARS_{lookback_years}.png")
            plt.clf()
