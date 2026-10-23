# Retail Lens — Flask website

A responsive retail analytics website for Ali Zawwar's Online Retail portfolio project.
It reads the cleaned CSV files produced by the existing notebooks. It does not require
MySQL credentials or rerun your import program. Your SQL work remains a separate part
of the portfolio.

## Project location

This reviewed project includes app.py, templates/, static/, the original Excel
and both cleaned CSVs. Extract the whole project and run from the directory that
contains app.py. See README.md for the notebook/SQL workflow and REVIEW_NOTES.md
for the cleanup details.

The website expects data/processed/cleaned_sales.csv. Cancellation credits use
data/processed/cleaned_transactions.csv when present. Without a sales CSV, a
setup screen explains which file is needed.

## Run on your Windows computer

Open PowerShell in your project folder. Use the same Python installation that worked
for your import script:

```powershell
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.12-64\python.exe" -m pip install -r requirements.txt
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.12-64\python.exe" app.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the terminal running. Press
Ctrl+C to stop the website. Do not run `import_sales.py` to launch the website.

On a computer where `python` works, use `python -m pip install -r requirements.txt`
and `python app.py` instead. Python 3.10 or newer is recommended for this package.

This is a local website, not a public deployment. Flask debug mode is disabled.
For public hosting, use a production WSGI server and configure the hosting platform.

## Features

- Date and country filters, including the complete selected end date.
- Sales, quantity, distinct invoices and identified customer cards.
- Monthly sales, top countries and top products with interactive hover values.
- One-time versus repeat customers and the top ten customers.
- Findings calculated for the active filter selection.
- Optional cancellation-credit totals from cleaned_transactions.csv.
- Download the active sales selection as CSV.
- Mobile layout, keyboard focus states and empty-result handling.
- Plotly is served locally; charts do not need a CDN or internet after installation.

## Data definitions

`cleaned_sales.csv` must contain InvoiceNo, StockCode, Description, Quantity,
InvoiceDate, UnitPrice, CustomerID, Country and SalesAmount. Extra columns such as
Year, Month and YearMonth are allowed. Dates should use the original pandas CSV
format, such as `2011-12-09 12:50:00`.

Use your existing deduplicated, positive-sales dataset. This website checks that
Quantity and UnitPrice are positive, C invoices are absent, and SalesAmount equals
Quantity × UnitPrice. It does not silently clean or overwrite your files.

Sales are positive invoiced amounts before credits. They are not net revenue or
profit. Postage and manual entries remain in overall sales. DOT, POST and M are
excluded only from product rankings. This is not an exhaustive classification of
all possible non-product codes. Product descriptions are the most frequent non-empty
descriptions for each code in the active selection.

Known customers have a non-missing CustomerID. A repeat customer has more than one
distinct positive-sales invoice within the active dates and country. This metric
is not a cohort retention rate. Missing IDs are not invented. Anonymous sales remain
in the overall totals. Numeric-looking IDs exported as `17850.0` are normalized to
`17850` for display and grouping.

For optional cancellation data, the website selects C-prefixed invoices with
negative quantity and positive UnitPrice from cleaned_transactions.csv. Credit
amount is the positive magnitude of Quantity × UnitPrice. Credits are filtered by
their own record dates and country; they are not linked to original purchases.
Do not call their ratio to sales invoices an order cancellation probability.

Source coverage reported in the existing project is 1 December 2010 to 9 December
2011. December 2011 is incomplete. Date filters can create additional partial
months. Do not interpret partial-month totals as a full-month decline.

Exports preserve the selected rows and neutralize formula-like text when opening
the CSV in spreadsheet software. Original CSV files remain unchanged.

## Checks

Run `python -m unittest -v test_app.py`. The included tests use tiny synthetic
records in temporary folders. They check totals, repeat definitions, end-of-day
filtering, empty results, anonymous sales, product exclusions, credits, validation
and downloads. No test records are added to your data.

Validation during this review: all seven website tests passed, plus two
importer tests described in README.md. The real uploaded CSVs were checked:
524,878 sales rows, £10,642,110.80 sales, 5,572,420 quantity, 19,960 invoices and
4,338 known customers. Chromium verified all four charts, Germany filtering and
a 375px mobile layout without horizontal overflow or JavaScript errors. Flask's
test client served browser requests. CSV export was checked against Germany totals.

## File guide

- `app.py`: CSV loading, filtering, calculations and Flask routes.
- `templates/base.html`: shared navigation and page structure.
- `templates/dashboard.html`: analysis page.
- `templates/setup.html`: missing-data and invalid-selection page.
- `static/style.css`: responsive layout and styling.
- `static/dashboard.js`: interactive charts and filter validation.
- `requirements.txt`: website dependencies.
- `test_app.py`: focused calculation and route checks.

## Documentation

- Flask: https://flask.palletsprojects.com/en/stable/quickstart/
- Plotly: https://plotly.com/javascript/configuration-options/

Portfolio presentation: describe your business questions, preprocessing assumptions,
analysis, SQL queries and limitations. The Flask interface presents that work; it
does not make predictions.
