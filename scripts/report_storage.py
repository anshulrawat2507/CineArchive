"""Report storage usage for tables in a MySQL schema."""
from __future__ import annotations

import argparse

from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show table sizes for a MySQL schema.")
    parser.add_argument(
        "--db-url",
        required=True,
        help="SQLAlchemy database URL, e.g. mysql+pymysql://user:password@localhost/BollywoodLens",
    )
    parser.add_argument(
        "--schema",
        required=True,
        help="Database/schema name to inspect.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    engine = create_engine(args.db_url)
    query = text(
        """
        SELECT
            table_name,
            table_rows,
            ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
        FROM information_schema.TABLES
        WHERE table_schema = :schema
        ORDER BY size_mb DESC;
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(query, {"schema": args.schema}).fetchall()

    if not rows:
        print(f"No tables found for schema '{args.schema}'.")
        return

    print(f"Table sizes for schema '{args.schema}':")
    for table_name, table_rows, size_mb in rows:
        size = size_mb if size_mb is not None else 0.0
        rows_display = table_rows if table_rows is not None else "N/A"
        print(f"- {table_name}: {rows_display} rows, {size:.2f} MB")


if __name__ == "__main__":
    main()
