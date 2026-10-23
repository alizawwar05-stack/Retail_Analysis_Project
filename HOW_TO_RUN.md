Steps to Run This Project
This project runs locally on your computer. It is not publicly deployed.

1. Download the Project
On GitHub, click Code → Download ZIP and extract the ZIP file.

Open PowerShell or a terminal in the project folder. This is the folder containing app.py and requirements.txt.

2. Install the Required Libraries
Run this command:

python -m pip install Flask pandas numpy plotly openpyxl matplotlib jupyterlab SQLAlchemy "PyMySQL[rsa]"

These libraries are used for the Flask website, data analysis notebooks, Excel files, charts, and optional MySQL import.

3. Prepare the Dataset
If data/processed/cleaned_sales.csv already exists, skip to Step 4.

Otherwise:

Download the UCI Online Retail dataset.

Extract the downloaded ZIP file and locate Online Retail.xlsx.

Place the Excel file in the project's data/raw/ folder. Create the folders if they do not exist.

Start JupyterLab from the project folder:

python -m jupyterlab

Open notebooks/01_Data_Exploration.ipynb.

Select Kernel → Restart Kernel and Run All Cells.

This creates the processed CSV files used by the website.

To regenerate the charts, open notebooks/02_Visualization.ipynb and select Kernel → Restart Kernel and Run All Cells.

4. Start the Website
From the project folder, run:

python app.py

5. Open the Website
Open this address in your browser:

http://127.0.0.1:5000

Keep the terminal open while using the website. Press Ctrl+C in the terminal to stop it.

Optional: MySQL
MySQL is not required to run the website.

To run the SQL queries, open sql/sales_analysis.sql in MySQL Workbench. The database name is retail_analysis, and the table name is salessales.

The import_sales.py script imports the CSV data into MySQL. You do not need to run it to start the website.

Important Notes
Run terminal commands from the project folder.
The Excel and CSV data files are excluded from GitHub by .gitignore.
The address 127.0.0.1 opens the website only on the computer running the app.
Dataset Credit
Daqing Chen (2015). Online Retail. UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33

The dataset and its details are available from the UCI Machine Learning Repository. 