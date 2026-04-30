# build_olist_db.py
# SQLite db from Olist CSV files

import os
import sqlite3
import pandas as pd

CSV_FOLDER = "olist_csv"
DB_PATH = "tool_files/olist.db"

# File name to table name
FILES_TO_TABLES = {
    "olist_orders_dataset.csv": "orders",
    "olist_order_items_dataset.csv": "order_items",
    "olist_products_dataset.csv": "products",
    "olist_customers_dataset.csv": "customers",
    "olist_sellers_dataset.csv": "sellers",
    "olist_order_payments_dataset.csv": "payments",
    "olist_order_reviews_dataset.csv": "reviews"
}

print("Building Olist SQLite database...")

# Connect to SQLite
conn = sqlite3.connect(DB_PATH)

try:
    for filename, table_name in FILES_TO_TABLES.items():
        filepath = os.path.join(CSV_FOLDER, filename)

        if not os.path.exists(filepath):
            print(f"Skipping missing file: {filename}")
            continue

        print(f"Loading {filename} into table '{table_name}'...")

        df = pd.read_csv(filepath)

        # Save to SQLite
        df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"  Done: {len(df)} rows loaded into {table_name}")

    print(f"\nDone! SQLite database saved at: {DB_PATH}")

finally:
    conn.close()