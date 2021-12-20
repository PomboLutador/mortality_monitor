FROM, TO = (tuple(i for i in range(5, 90, 5)), tuple(i + 4 for i in range(5, 90, 5)))

QUERY_AGE_TO_DATA_AGE = {
    "Y_LT5": "Less than 5 years",
    **{
        f"Y{start}-{end}": f"From {start} to {end} years"
        for start, end in zip(FROM, TO)
    },
    "Y_GE90": "90 years or over",
}


def get_data_age(query_age: str) -> str:
    """Converts ages as sent in the query to ages as seen in the returned data.

    E.g.: "Y35-39" -> "From 35 to 39 years"
    """
    return QUERY_AGE_TO_DATA_AGE[query_age]
