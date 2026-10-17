import csv
from functools import lru_cache
from math import isfinite
from pathlib import Path

from flask import Flask, render_template, request


app = Flask(__name__)
DATA_FILE = Path(__file__).resolve().with_name("cutoff_data.csv")
RESULT_COLUMNS = ("Institute", "Program", "Opening Rank", "Closing Rank")
FILTER_FIELDS = {
    "round": "Round",
    "quota": "Quota",
    "category": "Category",
    "gender": "Seat Gender",
}


def _parse_rank(value):
    try:
        number = float(str(value).strip().replace(",", ""))
    except (TypeError, ValueError):
        return None
    return number if isfinite(number) else None


def _display_rank(value):
    number = _parse_rank(value)
    if number is None:
        return "—"
    if number.is_integer():
        return f"{int(number):,}"
    return f"{number:,.2f}".rstrip("0").rstrip(".")


@lru_cache(maxsize=1)
def load_cutoff_rows():
    """Read and normalize the cutoff CSV once for the life of the app."""
    rows = []
    with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as data_file:
        for raw_row in csv.DictReader(data_file):
            row = {key: (raw_row.get(key) or "").strip() for key in RESULT_COLUMNS}
            for key in FILTER_FIELDS.values():
                row[key] = (raw_row.get(key) or "").strip()

            closing_rank = _parse_rank(raw_row.get("Closing Rank"))
            if closing_rank is None:
                continue

            row["_closing_rank"] = closing_rank
            row["Opening Rank"] = _display_rank(raw_row.get("Opening Rank"))
            row["Closing Rank"] = _display_rank(raw_row.get("Closing Rank"))
            rows.append(row)
    return rows


def get_filter_options(rows):
    options = {}
    for form_name, csv_name in FILTER_FIELDS.items():
        values = {row[csv_name] for row in rows if row[csv_name]}
        if form_name == "round":
            options[form_name] = sorted(values, key=lambda value: int(value.rsplit(" ", 1)[-1]))
        else:
            options[form_name] = sorted(values)
    return options


@app.route("/")
def index():
    rows = load_cutoff_rows()
    return render_template("index.html", options=get_filter_options(rows), form_data={})


@app.route("/predict", methods=["POST"])
def predict():
    rows = load_cutoff_rows()
    options = get_filter_options(rows)
    form_data = request.form

    raw_rank = (form_data.get("crl_rank") or "").strip()
    try:
        crl_rank = int(raw_rank.replace(",", ""))
        if crl_rank < 1:
            raise ValueError
    except ValueError:
        return render_template(
            "index.html",
            options=options,
            form_data=form_data,
            error="Enter a whole-number CRL rank greater than zero.",
        ), 400

    selected = {name: (form_data.get(name) or "").strip() for name in FILTER_FIELDS}
    if any(selected[name] not in options[name] for name in FILTER_FIELDS):
        return render_template(
            "index.html",
            options=options,
            form_data=form_data,
            error="Choose a round, quota, category, and seat type from the lists.",
        ), 400

    selected_csv_values = {
        FILTER_FIELDS[name]: selected[name]
        for name in FILTER_FIELDS
    }
    matching_rows = [
        row
        for row in rows
        if all(row[csv_name] == value for csv_name, value in selected_csv_values.items())
        and row["_closing_rank"] >= crl_rank
    ]
    matching_rows.sort(key=lambda row: row["_closing_rank"])

    result_rows = [
        {column: row[column] for column in RESULT_COLUMNS}
        for row in matching_rows
    ]
    criteria = {
        "rank": f"{crl_rank:,}",
        "round": selected["round"],
        "quota": selected["quota"],
        "category": selected["category"],
        "gender": selected["gender"],
    }
    return render_template(
        "result.html",
        rows=result_rows,
        columns=RESULT_COLUMNS,
        criteria=criteria,
        result_count=len(result_rows),
    )


if __name__ == "__main__":
    app.run()
