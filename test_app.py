"""Small synthetic-data checks. Run: python -m unittest -v test_app.py"""

import json
import re
import tempfile
import unittest
from pathlib import Path

import pandas as pd
from app import app, read_cached


class RetailWebsiteTests(unittest.TestCase):
    def setUp(self):
        self.previous_data_dir = app.config["DATA_DIR"]
        self.previous_testing = app.config["TESTING"]
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        app.config.update(TESTING=True, DATA_DIR=self.root)
        self.client = app.test_client()
        self.sales = pd.DataFrame(
            [
                ["1", "A", "Cup", 2, "2011-01-01 08:00:00", 10, "101.0", "UK", 20],
                ["1", "B", "Plate", 1, "2011-01-01 08:00:00", 5, "101.0", "UK", 5],
                ["2", "A", "Cup", 1, "2011-01-02 23:59:59", 10, "101.0", "UK", 10],
                [
                    "3",
                    "POST",
                    "Postage",
                    1,
                    "2011-02-02 12:00:00",
                    4,
                    None,
                    "France",
                    4,
                ],
                ["4", "B", "Plate", 2, "2011-02-03 12:00:00", 5, "102.0", "France", 10],
            ],
            columns=[
                "InvoiceNo",
                "StockCode",
                "Description",
                "Quantity",
                "InvoiceDate",
                "UnitPrice",
                "CustomerID",
                "Country",
                "SalesAmount",
            ],
        )
        self.write()

    def write(self):
        self.sales.to_csv(self.root / "cleaned_sales.csv", index=False)
        read_cached.cache_clear()

    def tearDown(self):
        read_cached.cache_clear()
        self.folder.cleanup()
        app.config.update(
            DATA_DIR=self.previous_data_dir, TESTING=self.previous_testing
        )

    def stats(self, url="/"):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        found = re.search(
            r'<script id="chart-data" type="application/json">(.*?)</script>',
            response.text,
            re.S,
        )
        self.assertIsNotNone(found)
        return json.loads(found.group(1))

    def test_totals_customer_definitions_and_exclusions(self):
        data = self.stats()
        self.assertEqual(
            (data["total"], data["quantity"], data["invoices"], data["customers"]),
            (49, 7, 4, 2),
        )
        self.assertEqual((data["once"], data["repeat"], data["repeat_pct"]), (1, 1, 50))
        self.assertEqual(data["monthly"]["values"], [35, 14])
        self.assertNotIn("POST", [r["label"] for r in data["products"]])
        self.assertEqual(data["top_customers"][0]["label"], "101")

    def test_filters_include_end_of_day_and_recompute_repeat(self):
        data = self.stats("/?start=2011-01-02&end=2011-01-02&country=UK")
        self.assertEqual(data["total"], 10)
        self.assertEqual(data["repeat"], 0)
        self.assertEqual(data["once"], 1)

    def test_empty_and_anonymous_only(self):
        data = self.stats("/?start=2011-01-01&end=2011-01-02&country=France")
        self.assertEqual(data["rows"], 0)
        self.assertIsNone(data["repeat_pct"])
        data = self.stats("/?start=2011-02-02&end=2011-02-02")
        self.assertEqual(data["total"], 4)
        self.assertEqual(data["customers"], 0)
        self.assertEqual(data["products"], [])

    def test_bad_filters(self):
        for query in [
            "start=2011-02-03&end=2011-01-01",
            "start=wrong",
            "country=Unknown",
            "start=2000-01-01",
            "start=NaT",
        ]:
            self.assertEqual(self.client.get("/?" + query).status_code, 400)

    def test_download_matches_selected_rows(self):
        response = self.client.get("/download?country=France")
        self.assertEqual(response.status_code, 200)
        from io import BytesIO

        data = pd.read_csv(BytesIO(response.data))
        self.assertEqual(len(data), 2)
        self.assertEqual(data.SalesAmount.sum(), 14)

    def test_credit_scope(self):
        credits = self.sales.iloc[:3].copy()
        credits["InvoiceNo"] = ["C10", "C10", "A10"]
        credits["Quantity"] = [-2, -1, -1]
        credits.to_csv(self.root / "cleaned_transactions.csv", index=False)
        response = self.client.get("/")
        self.assertIn("£25.00", response.text)
        self.assertIn("Unique credit invoices", response.text)
        self.assertEqual(self.stats()["total"], 49)

    def test_missing_and_invalid_data(self):
        (self.root / "cleaned_sales.csv").unlink()
        self.assertIn("Place cleaned_sales.csv", self.client.get("/").text)
        self.sales.loc[0, "SalesAmount"] = 999
        self.write()
        self.assertIn("SalesAmount must equal", self.client.get("/").text)


if __name__ == "__main__":
    unittest.main()
