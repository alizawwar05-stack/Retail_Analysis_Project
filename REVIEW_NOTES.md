# Project cleanup review

Reviewed on 24 October 2026. The scope was code readability, consistency,
reproducibility and obvious correctness issues, not a new analysis project.

## Changes

| File or folder | Change and reason |
| --- | --- |
| `notebooks/01_Data_Exploration.ipynb` | Removed unused NumPy import and empty cell; moved imports and paths to the top; replaced `c` with `is_cancelled`; fixed a Raw cell that should execute; added short sections; made product exclusions consistent with SQL and the website; displayed customer count; checked credit signs before computing credit magnitude; refreshed outputs |
| `notebooks/02_Visualization.ipynb` | Replaced hard-coded customer counts with calculations; put highest country sales at the top; formatted full currency-axis numbers; removed repeated directory creation; reserved space for the monthly coverage note; closed figures after use; refreshed outputs |
| `reports/figures/` | Regenerated all four charts from the corrected notebook and inspected them |
| `app.py` | Formatted long expressions and dictionaries; ignored empty product descriptions when choosing a label; retained existing calculations and routes |
| `static/`, `templates/` | Expanded compressed CSS, JavaScript and HTML into readable formatting; kept layout and interactions |
| `import_sales.py` | Added a main entry point so importing the module does not prompt or connect; separated CSV loading and batch import; hid password input; always disposed of connections; made mismatched counts raise an error; defaulted to refusing an existing table; kept explicit rebuilding available through `--replace` |
| `requirements.txt` | Included Excel, plotting, Jupyter and MySQL dependencies missing from the website-only list |
| `sql/sales_analysis.sql` | Moved from `SQL File` to `sql`; retained all five SQL queries |
| `test_app.py` | Restored original app settings after each test and formatted source |
| `test_import_sales.py` | Added two meaningful checks for missing CustomerIDs and existing-table behavior using SQLite |
| `README.md`, `README_WEBSITE.md` | Documented the whole project, current bundled data, startup steps and actual verification |
| `.gitignore` | Added notebook/editor caches and raw data patterns for future commits |

Removed generated `.virtual_documents`, `anaconda_projects` metadata and notebook/
figure checkpoint copies from the returned package. Removed the obsolete
`PUT_YOUR_CSV_HERE.txt`, since the CSVs are included. Kept the original editor
settings. The original upload remained untouched in the local review workspace.

## Preserved

The original Excel file and both CSV files are byte-for-byte identical to the
upload. Every original data row remains available. Notebook sales-cleaning rules,
overall totals, the database/table names, the five SQL queries and website design
are preserved. The exploration notebook's product ranking now deliberately uses
the same DOT/POST/M exclusion already used elsewhere.

## Verification and limits

- Nine automated tests passed: seven Flask checks and two importer checks.
- All 33 exploration and six visualization code cells executed without errors in
  clean IPython namespaces. This environment blocked kernel sockets, so a full
  external Jupyter kernel was not used for the review run.
- Both CSVs regenerated from the Excel notebook matched all original rows/columns;
  numeric comparisons allowed only a 1e-9 tolerance for CSV float round trips.
  Original CSV bytes were then retained in the delivered project.
- Checked real totals, cancellation credits, top product, Germany totals/export,
  final-day filtering, Plotly serving and importer CSV preparation.
- Chromium showed four charts, working Germany filtering, no JavaScript errors,
  and no horizontal overflow at 375px. Requests used Flask's test client.
- SQL was read and checked for consistency. No live MySQL connection or query
  execution was possible here. The two import tests use SQLite only.
- Existing Markdown findings describe the supplied dataset. Review them manually
  if you replace it with different transactions.

## Using the returned project

Extract this reviewed ZIP into a separate folder first and open its README.md.
If copying changes into the old project, preserve your working data and use the
new `sql` folder instead of maintaining duplicate query files in `SQL File`.
Do not rerun the MySQL import just to launch the website.
