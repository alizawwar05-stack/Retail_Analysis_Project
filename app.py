"""Retail Lens: a local Flask website for the cleaned Online Retail project."""

from functools import lru_cache
from io import BytesIO
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request, send_file, Response
from plotly.offline import get_plotlyjs

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
app.config["DATA_DIR"] = BASE_DIR / "data" / "processed"
REQUIRED = [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "UnitPrice",
    "CustomerID",
    "Country",
]


class DataProblem(Exception):
    pass


@lru_cache(maxsize=4)
def read_cached(path, modified, size, sales):
    """Read again only when a CSV changes; never change the source file."""
    try:
        df = pd.read_csv(
            path,
            dtype={
                "InvoiceNo": "string",
                "StockCode": "string",
                "CustomerID": "string",
                "Country": "string",
            },
        )
    except (ValueError, OSError, pd.errors.ParserError) as error:
        raise DataProblem(
            "The CSV could not be read. Export it again from your notebook."
        ) from error
    missing = set(REQUIRED) - set(df.columns)
    if sales and "SalesAmount" not in df:
        missing.add("SalesAmount")
    if missing:
        raise DataProblem("Missing columns: " + ", ".join(sorted(missing)))
    if df.empty:
        raise DataProblem("The CSV is empty. Add your cleaned transaction data.")
    try:
        df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="raise")
        numeric = ["Quantity", "UnitPrice"] + (["SalesAmount"] if sales else [])
        for column in numeric:
            df[column] = pd.to_numeric(df[column], errors="raise")
            if not np.isfinite(df[column].to_numpy(dtype=float)).all():
                raise ValueError("Missing or non-finite numbers")
        if df["InvoiceDate"].isna().any():
            raise ValueError("Missing dates")
        if (df["Quantity"] % 1 != 0).any():
            raise ValueError("Fractional quantity")
    except (ValueError, TypeError) as error:
        raise DataProblem(
            "Check InvoiceDate, Quantity, UnitPrice and SalesAmount in the CSV."
        ) from error
    for column in ["InvoiceNo", "StockCode", "Country"]:
        if df[column].isna().any() or df[column].str.strip().eq("").any():
            raise DataProblem(
                f"{column} contains missing values. Check your cleaned CSV."
            )
    # 17850.0 and 17850 represent the same customer. Missing IDs stay missing.
    df["CustomerID"] = (
        df["CustomerID"].str.strip().str.replace(r"\.0+$", "", regex=True)
    )
    df["CustomerID"] = df["CustomerID"].replace("", pd.NA)
    if sales:
        invalid = (
            (df["Quantity"] <= 0)
            | (df["UnitPrice"] <= 0)
            | df["InvoiceNo"].str.startswith("C")
        )
        if invalid.any():
            raise DataProblem(
                "Use cleaned_sales.csv: positive Quantity and UnitPrice, excluding C invoices."
            )
        if not np.allclose(
            df["SalesAmount"], df["Quantity"] * df["UnitPrice"], rtol=0, atol=0.0001
        ):
            raise DataProblem(
                "SalesAmount must equal Quantity × UnitPrice. Re-export your cleaned sales."
            )
    return df


def load_data(filename, sales=True):
    path = Path(app.config["DATA_DIR"]) / filename
    if not path.exists():
        raise DataProblem(
            f"Place {filename} in data/processed, then refresh this page."
        )
    info = path.stat()
    return read_cached(str(path), info.st_mtime_ns, info.st_size, sales)


def filter_data(df, start, end, country):
    mask = (df["InvoiceDate"] >= pd.Timestamp(start)) & (
        df["InvoiceDate"] < pd.Timestamp(end) + pd.Timedelta(days=1)
    )
    if country:
        mask &= df["Country"].eq(country)
    return df.loc[mask]


def selection(df):
    minimum = df["InvoiceDate"].min().date()
    maximum = df["InvoiceDate"].max().date()
    try:
        start = pd.Timestamp(request.args.get("start") or minimum).date()
        end = pd.Timestamp(request.args.get("end") or maximum).date()
        if (
            pd.isna(start)
            or pd.isna(end)
            or start > end
            or start < minimum
            or end > maximum
        ):
            raise ValueError()
    except (ValueError, TypeError, OverflowError):
        raise DataProblem(
            "Choose a valid date range within the dataset, with the start before the end."
        )
    country = request.args.get("country", "")
    countries = sorted(df["Country"].dropna().unique().tolist())
    if country and country not in countries:
        raise DataProblem("Choose a country from the list.")
    return start, end, country, minimum, maximum, countries


def top_rows(frame, column):
    amounts = (
        frame.groupby(column)["SalesAmount"].sum().sort_values(ascending=False).head(10)
    )
    return [
        {"label": str(label), "amount": float(amount)}
        for label, amount in amounts.items()
    ]


def analyse(df, start, end):
    total = float(df["SalesAmount"].sum())
    invoice_count = int(df["InvoiceNo"].nunique())
    known = df.dropna(subset=["CustomerID"])
    invoices = known.groupby("CustomerID")["InvoiceNo"].nunique()
    once = int(invoices.eq(1).sum())
    repeat = int(invoices.gt(1).sum())
    customer_count = once + repeat
    months = pd.period_range(start, end, freq="M")
    monthly = (
        df.groupby(df["InvoiceDate"].dt.to_period("M"))["SalesAmount"]
        .sum()
        .reindex(months, fill_value=0)
    )
    products = df.loc[~df["StockCode"].isin(["DOT", "POST", "M"])]
    product_rows = top_rows(products, "StockCode")
    # Descriptions can change; use the most frequent non-empty label per product.
    descriptions = products.dropna(subset=["Description"])
    descriptions = descriptions.loc[
        descriptions["Description"].astype(str).str.strip().ne("")
    ]
    if not descriptions.empty:
        counts = (
            descriptions.groupby(["StockCode", "Description"])
            .size()
            .reset_index(name="count")
        )
        names = (
            counts.sort_values("count", ascending=False)
            .drop_duplicates("StockCode")
            .set_index("StockCode")["Description"]
        )
        for row in product_rows:
            row["description"] = str(names.get(row["label"], "Description unavailable"))
    for row in product_rows:
        row.setdefault("description", "Description unavailable")
    country_rows = top_rows(df, "Country")
    customer_rows = top_rows(known, "CustomerID")
    for row in customer_rows:
        row["invoices"] = int(invoices.loc[row["label"]])
    insights = []
    if total:
        leader = country_rows[0]
        insights.append(
            {
                "title": "Leading market",
                "text": f"{leader['label']} contributes {leader['amount'] / total * 100:.1f}% of sales in this selection.",
            }
        )
        insights.append(
            {
                "title": "Highest monthly total",
                "text": f"{monthly.idxmax().strftime('%B %Y')} leads with £{monthly.max():,.2f}. Boundary months may cover fewer days.",
            }
        )
    if customer_count:
        insights.append(
            {
                "title": "Repeat purchasing",
                "text": f"{repeat / customer_count * 100:.2f}% of identified customers placed more than one invoice in this selection.",
            }
        )
    return dict(
        total=total,
        quantity=int(df["Quantity"].sum()),
        invoices=invoice_count,
        customers=customer_count,
        once=once,
        repeat=repeat,
        repeat_pct=repeat / customer_count * 100 if customer_count else None,
        average=total / invoice_count if invoice_count else 0,
        known_share=len(known) / len(df) * 100 if len(df) else 0,
        rows=len(df),
        monthly={
            "labels": [str(m) for m in months],
            "values": monthly.astype(float).tolist(),
        },
        countries=country_rows,
        products=product_rows,
        top_customers=customer_rows,
        insights=insights,
    )


def credits(start, end, country):
    path = Path(app.config["DATA_DIR"]) / "cleaned_transactions.csv"
    if not path.exists():
        return None, None
    try:
        data = filter_data(
            load_data("cleaned_transactions.csv", sales=False), start, end, country
        )
        data = data.loc[
            data["InvoiceNo"].str.startswith("C")
            & (data["Quantity"] < 0)
            & (data["UnitPrice"] > 0)
        ]
        return {
            "rows": len(data),
            "invoices": int(data["InvoiceNo"].nunique()),
            "amount": float(-(data["Quantity"] * data["UnitPrice"]).sum()),
        }, None
    except DataProblem as error:
        return None, str(error)


@app.template_filter("money")
def money(value):
    return f"£{value:,.2f}"


@app.template_filter("number")
def number(value):
    return f"{value:,}"


@app.get("/")
def dashboard():
    try:
        source = load_data("cleaned_sales.csv")
    except DataProblem as error:
        return render_template("setup.html", message=str(error)), 200
    try:
        start, end, country, minimum, maximum, countries = selection(source)
    except DataProblem as error:
        return render_template("setup.html", message=str(error), invalid=True), 400
    filtered = filter_data(source, start, end, country)
    stats = analyse(filtered, start, end)
    cancellation, credit_error = credits(start, end, country)
    return render_template(
        "dashboard.html",
        stats=stats,
        start=start,
        end=end,
        country=country,
        countries=countries,
        minimum=minimum,
        maximum=maximum,
        cancellation=cancellation,
        credit_error=credit_error,
        coverage=f"{minimum:%d %b %Y} – {maximum:%d %b %Y}",
    )


@app.get("/download")
def download():
    try:
        df = load_data("cleaned_sales.csv")
        start, end, country, *_ = selection(df)
    except DataProblem as error:
        return jsonify(error=str(error)), 400
    filtered = filter_data(df, start, end, country).copy()
    # Protect spreadsheet exports against formula interpretation of text values.
    for column in filtered.select_dtypes(include=["object", "string"]).columns:
        filtered[column] = filtered[column].map(
            lambda value: (
                "'" + value
                if isinstance(value, str)
                and value.lstrip().startswith(("=", "+", "-", "@"))
                else value
            )
        )
    content = BytesIO(filtered.to_csv(index=False).encode("utf-8-sig"))
    return send_file(
        content,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"retail_sales_{start}_{end}.csv",
    )


@app.get("/assets/plotly.js")
def plotly_library():
    # Served locally: charts do not depend on an external CDN.
    response = Response(get_plotlyjs(), mimetype="application/javascript")
    response.headers["Cache-Control"] = "public, max-age=86400"
    return response


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
