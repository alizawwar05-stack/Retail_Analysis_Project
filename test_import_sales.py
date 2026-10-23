"""Import behavior checks using temporary SQLite storage, not your MySQL database."""

from contextlib import redirect_stdout
from io import StringIO
import unittest

import pandas as pd
from sqlalchemy import create_engine, text

from import_sales import import_dataframe


class ImportSalesTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        self.sales = pd.DataFrame(
            {
                "InvoiceNo": ["1", "2"],
                "StockCode": ["A", "B"],
                "Description": ["Cup", "Plate"],
                "Quantity": [2, 1],
                "InvoiceDate": pd.to_datetime(["2011-01-01", "2011-01-02"]),
                "UnitPrice": [5.0, 4.0],
                "CustomerID": pd.array([101, None], dtype="Int64"),
                "Country": ["UK", "UK"],
                "SalesAmount": [10.0, 4.0],
            }
        )

    def tearDown(self):
        self.engine.dispose()

    def run_import(self, frame, replace=False):
        with redirect_stdout(StringIO()):
            import_dataframe(frame, self.engine, replace=replace)

    def test_preserves_existing_table_and_missing_customer(self):
        self.run_import(self.sales)
        with self.assertRaises(ValueError):
            self.run_import(self.sales.iloc[:1])
        with self.engine.connect() as connection:
            count, total, known = connection.execute(
                text(
                    "SELECT COUNT(*), SUM(SalesAmount), COUNT(CustomerID) FROM salessales"
                )
            ).one()
        self.assertEqual((count, total, known), (2, 14, 1))

    def test_explicit_replace_rebuilds_table(self):
        self.run_import(self.sales)
        self.run_import(self.sales.iloc[:1], replace=True)
        with self.engine.connect() as connection:
            count = connection.execute(
                text("SELECT COUNT(*) FROM salessales")
            ).scalar_one()
        self.assertEqual(count, 1)


if __name__ == "__main__":
    unittest.main()
