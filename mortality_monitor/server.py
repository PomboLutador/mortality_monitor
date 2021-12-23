import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS  # type: ignore

from mortality_monitor.cache import DataFrameFileCache
from mortality_monitor.constants import (
    AGE_COLUMN,
    DEATHS_COLUMN,
    GEO_COLUMN,
    PERIOD_COLUMN,
)
from mortality_monitor.deaths import get_deaths
from mortality_monitor.eurostat import get_mortality_data
from mortality_monitor.expected_deaths import get_expected_deaths
from mortality_monitor.util import (
    QUERY_AGE_TO_DATA_AGE,
    get_all_age_groups_for_query,
    read_csv_with_weekly_period,
)

app = Flask(__name__)
CORS(app)

DATA_FOLDER = "data"
ARCHIVE_FOLDER = "archive"
MORTALITY_DATA_FILENAME = "mortality_data"


def _get_mortality_data(
    cache: DataFrameFileCache, filename: str = MORTALITY_DATA_FILENAME
) -> pd.DataFrame:
    try:
        mortality_data = cache.get_data(
            filename, read_function=read_csv_with_weekly_period
        )
    except OSError:
        mortality_data = get_mortality_data(
            geo="country", ages=get_all_age_groups_for_query()
        )
        cache.put_data(data=mortality_data, filename=filename)
    finally:
        return mortality_data


cache = DataFrameFileCache(data_folder=DATA_FOLDER, archive_folder=ARCHIVE_FOLDER)
mortality_data = _get_mortality_data(cache=cache)


@app.route("/available_geos")
def available_geos():
    return jsonify(list(mortality_data.reset_index()[GEO_COLUMN].unique()))


@app.route("/available_ages")
def available_ages():
    return jsonify(QUERY_AGE_TO_DATA_AGE)


@app.route("/available_years")
def available_years():
    available_years = (
        mortality_data.reset_index()[PERIOD_COLUMN]
        .map(lambda period: int(period.year))
        .drop_duplicates()
        .values.tolist()
    )
    available_years.sort(reverse=True)
    return jsonify(available_years)


@app.route("/excess_deaths", methods=["POST"])
def excess_deaths():
    if request.method == "POST":
        user_input = request.json
        deaths = get_deaths(
            mortality_data=mortality_data,
            geo=user_input[GEO_COLUMN],
            ages=user_input[AGE_COLUMN],
        )
        expected_deaths = get_expected_deaths(deaths=deaths).pipe(
            _filter_on_year, year=user_input["year"]
        )
        deaths = deaths.pipe(_filter_on_year, year=user_input["year"])

        excess_deaths = deaths - expected_deaths
        periods = deaths.index

        above_expectation_deaths = [
            -np.abs(value) if (value > 0) else 0
            for value in excess_deaths.values.round().tolist()
        ]
        below_expectation_deaths = [
            -np.abs(value) if (value <= 0) else 0
            for value in excess_deaths.values.round().tolist()
        ]

        return jsonify(
            {
                "weekly_data": {
                    "deaths": deaths.values.round().tolist(),
                    "label": [f"{period.year}/{period.week}" for period in periods],
                    "excess_deaths": excess_deaths.values.round().tolist(),
                    "expected_deaths": expected_deaths.values.round().tolist(),
                    "above_expectation_deaths": above_expectation_deaths,
                    "below_expectation_deaths": below_expectation_deaths,
                }
            }
        )


@app.route("/yearly_deaths", methods=["POST"])
def yearly_deaths():
    if request.method == "POST":
        user_input = request.json
        max_week = user_input["max_week"]
        deaths_per_year = (
            get_deaths(
                mortality_data=mortality_data,
                geo=user_input[GEO_COLUMN],
                ages=user_input[AGE_COLUMN],
            )
            .reset_index()
            .assign(
                year=lambda df: df["period"].map(lambda period: period.year),
                week=lambda df: df["period"].map(lambda period: period.week),
            )
            .query("week <= @max_week")
            .groupby(by=["year"], as_index=False)[DEATHS_COLUMN]
            .sum()
        )
        return jsonify(
            {
                "yearly_deaths": {
                    "years": deaths_per_year["year"].values.tolist(),
                    "actual_deaths": deaths_per_year[DEATHS_COLUMN].values.tolist(),
                    "max_week": max_week,
                }
            }
        )


def _filter_on_year(data: pd.Series, year: int) -> pd.Series:
    column_name = data.name
    return (
        data.reset_index()  # type: ignore
        .assign(year=lambda df: df[PERIOD_COLUMN].map(lambda period: period.year))
        .query("year >= @year")
        .drop(columns=["year"])
        .set_index(PERIOD_COLUMN)[column_name]
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)