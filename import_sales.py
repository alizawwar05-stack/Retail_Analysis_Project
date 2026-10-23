"""Import cleaned sales into MySQL. Existing tables are kept unless --replace is used."""

import argparse
from getpass import getpass
from pathlib import Path

import pandas as pd
from sqlalchemy import URL, create_engine, text
from sqlalchemy.types import DateTime, Integer, Numeric, String

BASE_DIR = Path(__file__).resolve().parent
TABLE_NAME = "salessales"
BATCH_SIZE = 5000
COLUMN_TYPES = {
    "InvoiceNo": String(30),
    "StockCode": String(30),
    "Description": String(500),
    "Quantity": Integer(),
    "InvoiceDate": DateTime(),
    "UnitPrice": Numeric(18, 4),
    "CustomerID": Integer(),
    "Country": String(100),
    "SalesAmount": Numeric(18, 4),
}


def load_sales(file_path):
    """Load the cleaned CSV and preserve missing customer IDs as SQL NULL."""
    sales_df = pd.read_csv(
        file_path,
        dtype={"InvoiceNo": str, "StockCode": str},
        parse_dates=["InvoiceDate"],
    )
    missing = set(COLUMN_TYPES) - set(sales_df.columns)
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))
    if sales_df.empty:
        raise ValueError("The sales CSV is empty.")
    sales_df["InvoiceDate"] = pd.to_datetime(sales_df["InvoiceDate"], errors="raise")
    sales_df["CustomerID"] = sales_df["CustomerID"].astype("Int64")
    return sales_df


def import_dataframe(sales_df, engine, replace=False):
    """Import batches and verify the row count. Refuse an existing table by default."""
    # Explicit replacement drops the previous table. A failed import can leave
    # a partial new table, so use --replace only when you intend to rebuild it.
    sales_df.head(0).to_sql(
        name=TABLE_NAME,
        con=engine,
        if_exists="replace" if replace else "fail",
        index=False,
        dtype=COLUMN_TYPES,
    )

    total_rows = len(sales_df)
    for start in range(0, total_rows, BATCH_SIZE):
        batch = sales_df.iloc[start : start + BATCH_SIZE]
        with engine.begin() as connection:
            batch.to_sql(
                name=TABLE_NAME,
                con=connection,
                if_exists="append",
                index=False,
                chunksize=1000,
            )
        print(f"Imported: {start + len(batch):,} / {total_rows:,}", flush=True)

    with engine.connect() as connection:
        database_rows = connection.execute(
            text("SELECT COUNT(*) FROM salessales")
        ).scalar_one()

    print("CSV rows:", total_rows)
    print("MySQL rows:", database_rows)
    if database_rows != total_rows:
        raise RuntimeError("Import verification failed: row counts do not match.")
    print("Import completed. Row counts match!")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Drop and rebuild salessales, including any existing imported rows.",
    )
    args = parser.parse_args()
    sales_df = load_sales(BASE_DIR / "data/processed/cleaned_sales.csv")

    username = input("MySQL username: ").strip()
    password = getpass("MySQL password (typing is hidden): ")
    connection_url = URL.create(
        "mysql+pymysql",
        username=username,
        password=password,
        host="localhost",
        port=3306,
        database="retail_analysis",
        query={"charset": "utf8mb4"},
    )
    engine = create_engine(connection_url)
    try:
        import_dataframe(sales_df, engine, replace=args.replace)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
