# build_olist_db.py
# SQLite db from Olist CSV files

# Imports
import os # To work with file paths
import sqlite3 # Create and connect to the SQLite database
import pandas as pd # To read the csv files

# Folder and database paths
# Multiple olist dataset CSV files stores in a folder
# Output of this script is a SQLite db saved as olist.db
CSV_FOLDER = "olist_csv"
DB_PATH = "tool_files/olist.db"

# File name to table name
# Maps each CSV file to the name of the table it will become
FILES_TO_TABLES = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_products_dataset.csv": "products",
    "olist_customers_dataset.csv": "customers",
    "olist_sellers_dataset.csv": "sellers",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews"
}

# Verify that all expected source files are available before rebuilding the database
missing_files = [
    filename
    for filename in FILES_TO_TABLES
    if not os.path.exists(os.path.join(CSV_FOLDER, filename))
]

if missing_files:
    raise FileNotFoundError(
        "Missing required Olist CSV files: " + ", ".join(missing_files)
    )


print("Building Olist SQLite database...")

# Connect to SQLite db
conn = sqlite3.connect(DB_PATH)

# Loop goes through every CSV file listed in the dictionary and builds the full file path for each one
try:
    for filename, table_name in FILES_TO_TABLES.items():
        filepath = os.path.join(CSV_FOLDER, filename)

        print(f"Loading {filename} into table '{table_name}'...")
        # Loads each CSV into a pandas DataFrame
        df = pd.read_csv(filepath)

        # Save to SQLite
        # Key line saving the pandas df into the SQLite db as a table
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        # How many rows were inserted, helped verify the data loaded correctly
        print(f"  Done: {len(df)} rows loaded into {table_name}")

    print(f"\nDone! SQLite database saved at: {DB_PATH}")
# Connection closure to avoid locking the db file or leaving resources open
finally:
    conn.close()