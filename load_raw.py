import csv
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATA_DIR = Path(__file__).parent / "data" / "raw"

FILES = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "product_category_translation": "product_category_name_translation.csv",
}

def create_raw_table(cur, table, path):
    with open(path, encoding='utf-8') as f:
        header = next(csv.reader(f))
    cols = ", ".join(f'"{c}" TEXT' for c in header)
    cur.execute(f"CREATE TABLE IF NOT EXISTS raw.{table} ({cols})")

def load_table(conn, table, path):
    with conn:
        with conn.cursor() as cur:
            create_raw_table(cur=cur, table=table, path=path)
            cur.execute(f"TRUNCATE raw.{table}")
            with open(path, encoding="utf-8") as f:
                cur.copy_expert(
                    f"COPY raw.{table} FROM STDIN WITH (FORMAT csv, HEADER true)", f)
                cur.execute(f"SELECT count(*) FROM raw.{table}")
                print(f"raw.{table}:{cur.fetchone()[0]} rows")

def main():
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )
    with conn, conn.cursor() as cur:
        cur.execute("CREATE SCHEMA IF NOT EXISTS raw")
    for table, filename in FILES.items():
        load_table(conn, table, DATA_DIR / filename)
    conn.close()

if __name__ == "__main__":
    main()
