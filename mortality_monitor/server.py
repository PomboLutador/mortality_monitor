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
app.config["JSON_SORT_KEYS"] = False
CORS(app)

YEAR = "year"
DATA_FOLDER = "data"
ARCHIVE_FOLDER = "archive"
MORTALITY_DATA_FILENAME = "mortality_data"
CACHE = DataFrameFileCache(data_folder=DATA_FOLDER, archive_folder=ARCHIVE_FOLDER)


try:
    mortality_data = CACHE.get_data(
        MORTALITY_DATA_FILENAME, read_function=read_csv_with_weekly_period
    )
except OSError:
    mortality_data = get_mortality_data(
        geo="country", ages=get_all_age_groups_for_query()
    )
    CACHE.put_data(data=mortality_data, filename=MORTALITY_DATA_FILENAME)


@app.route("/available_geos", methods=["GET"])
def available_geos():
    if request.method == "GET":
        return jsonify(list(mortality_data.reset_index()[GEO_COLUMN].unique()))


@app.route("/available_ages", methods=["GET"])
def available_ages():
    if request.method == "GET":
        return jsonify(QUERY_AGE_TO_DATA_AGE)


@app.route("/available_years", methods=["GET"])
def available_years():
    if request.method == "GET":
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
        expected_deaths = (
            get_expected_deaths(deaths=deaths)
            .rolling(window=4)
            .mean()
            .pipe(_filter_on_year, year=user_input[YEAR])
        )
        deaths = deaths.pipe(_filter_on_year, year=user_input[YEAR])
        periods = deaths.index

        above_expectation_deaths = np.where(
            deaths > expected_deaths, deaths - expected_deaths, 0
        )
        below_expectation_deaths = np.where(
            deaths <= expected_deaths, expected_deaths - deaths, 0
        )
        deaths = np.where(deaths < expected_deaths, deaths, expected_deaths)

        return jsonify(
            {
                "deaths": deaths.round().tolist(),
                "label": [_get_period_representation(period) for period in periods],
                "expected_deaths": expected_deaths.round().tolist(),
                "above_expectation_deaths": above_expectation_deaths.round().tolist(),
                "below_expectation_deaths": below_expectation_deaths.round().tolist(),
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
                year=lambda df: df[PERIOD_COLUMN].map(lambda period: period.year),
                week=lambda df: df[PERIOD_COLUMN].map(lambda period: period.week),
            )
            .query("week <= @max_week")
            .groupby(by=[YEAR], as_index=False)[DEATHS_COLUMN]
            .sum()
        )
        return jsonify(
            {
                "yearly_deaths": {
                    "years": deaths_per_year[YEAR].values.tolist(),
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
        .drop(columns=[YEAR])
        .set_index(PERIOD_COLUMN)[column_name]
    )


def _get_period_representation(p: pd.Period) -> str:
    if p.start_time.year == p.end_time.year:
        return f"{p.start_time.year}/{p.week}"
    elif p.week == 1:
        return f"{p.end_time.year}/{p.week}"
    elif p.week >= 52:
        return f"{p.start_time.year}/{p.week}"
    raise ValueError(
        f"Period {p} has unequal start/end time years and is not in week 1, 52 or 53."
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
