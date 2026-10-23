# Retail Customer Analysis

A learning and portfolio project by Ali Zawwar: cleaning retail transaction data,
answering sales and customer questions with pandas and SQL, and presenting the
results in a Flask website.

## Questions answered

- How much was sold, and how does sales amount vary by month?
- Which countries and products contribute the most sales?
- Which customers spend the most, and how many purchase more than once?
- How much cancellation credit is recorded?

Sales means positive invoiced amounts before credits. It does not mean profit
or net revenue. This project describes historical data; it does not predict sales.

## Files and order of work

| Location | Purpose |
| --- | --- |
| `data/raw/Online Retail.xlsx` | Original dataset; preserved unchanged |
| `notebooks/01_Data_Exploration.ipynb` | Inspect, clean, analyse, export CSV files |
| `notebooks/02_Visualization.ipynb` | Calculate chart data and save figures |
| `data/processed/cleaned_sales.csv` | Positive sales, including unknown customers |
| `data/processed/cleaned_transactions.csv` | Deduplicated transactions, including credits and adjustments |
| `reports/figures/` | Four regenerated PNG charts |
| `sql/sales_analysis.sql` | Five MySQL analysis queries |
| `import_sales.py` | Optional CSV-to-MySQL import |
| `app.py`, `templates/`, `static/` | Flask website, HTML, CSS, JavaScript |
| `test_app.py`, `test_import_sales.py` | Focused automated checks |
| `README_WEBSITE.md` | Website operation and metric definitions |
| `REVIEW_NOTES.md` | What changed and what was verified |

The original Excel and both original CSV files are included in this reviewed
ZIP. Editor caches and temporary notebook copies are excluded. `.gitignore`
keeps large data files and generated editor state out of future Git commits.

## Run the website

Extract the ZIP to a separate location first. Open PowerShell in the extracted
project folder, the folder containing `app.py` and `requirements.txt`.
The directory name may differ if Windows adds a second enclosing folder.

```powershell
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.12-64\python.exe" -m pip install -r requirements.txt
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.12-64\python.exe" app.py
```

Open http://127.0.0.1:5000 and keep the terminal open. Stop with Ctrl+C.
MySQL is not required for the website. You do not need to rerun the import.

## Run the notebooks

From the project folder, launch Jupyter:

```powershell
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.12-64\python.exe" -m jupyterlab
```

Open notebook 01, select Restart Kernel and Run All Cells, then do the same for
notebook 02. These notebooks work when the kernel starts in either the project
folder or its `notebooks` folder. Notebook 01 rewrites processed CSVs; notebook
02 rewrites the four figure files. Both keep the original Excel file unchanged.

## Optional MySQL analysis

The existing database name is `retail_analysis` and table name is `salessales`.
Open `sql/sales_analysis.sql` in MySQL Workbench and run its queries against your
existing import. The folder was previously named `SQL File`.

For a new import, the database must already exist. Run `python import_sales.py`
using the same Python executable shown above. The password is entered with
hidden typing; no characters appear on screen. Press Enter after typing it.

An existing table is now refused by default. Only if you intend to drop and
rebuild it, run `python import_sales.py --replace`. Replacement is not an atomic
swap: an interrupted import can leave a partial new table. Your working MySQL
import has not been changed or accessed during this review.

## Data decisions

- Remove 5,268 exact duplicate rows, leaving 536,641 transactions.
- Keep positive Quantity and UnitPrice and exclude C-prefixed invoices for sales.
- Calculate SalesAmount as Quantity multiplied by UnitPrice.
- Preserve missing CustomerIDs for total sales, but exclude them from customer metrics.
- Keep postage and manual entries in overall sales; exclude DOT, POST and M only
  from the product ranking. This is not a complete classification of every stock code.
- Count distinct InvoiceNo values, not transaction rows, when measuring purchases.
- A repeat customer has more than one sales invoice within the analysed selection.
- Keep cancellation credits separate; they are not matched to original purchases.
- Data ends on 9 December 2011. December 2011 is not a complete month.

## Verified results for the supplied dataset

| Metric | Result |
| --- | ---: |
| Positive sales rows | 524,878 |
| Sales amount | £10,642,110.80 |
| Quantity sold | 5,572,420 |
| Sales invoices | 19,960 |
| Known customers | 4,338 |
| One-time customers | 1,493 |
| Repeat customers | 2,845 |
| Repeat customer share | 65.58% |
| Cancellation rows | 9,251 |
| Cancellation invoices | 3,836 |
| Cancellation credit amount | £893,979.73 |

## Validation

```powershell
& "C:\Users\HP\AppData\Local\Python\pythoncore-3.12-64\python.exe" -m unittest -v test_app.py test_import_sales.py
```

All nine tests passed. The importer tests use temporary SQLite storage; they do
not certify MySQL connectivity, permissions or driver behavior. All 39 notebook
code cells were executed in order in fresh IPython namespaces against the supplied
data. Regenerated CSV contents matched every original row and column. Original
Excel/CSV bytes were retained in the final package after verification.

Flask responses and Chromium rendering were checked with the real CSVs, including
Germany filtering, charts, CSV export and a 375px mobile layout. Browser requests
were served through Flask's test client; no public website was deployed.
