# -*- coding: utf-8 -*-
"""Recreate stock_master table with the full JPX schema (Phase 2).

Updated: 2025-10-12
Description: Drop and recreate stock_master with consistent column definitions
and rebuild indexes as part of the migration.

Usage:
    python app/migrations/update_stock_master_full_schema.py
"""

import io
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# Ensure stdout/stderr use UTF-8 (Windows-safe)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Make project root importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Database URL
DATABASE_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


def update_stock_master_schema():
    """Drop and recreate stock_master table, then rebuild indexes."""
    print("=" * 80)
    print("Starting migration: recreate stock_master full schema")
    print("=" * 80)

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # 1. Drop existing stock_master
            print(
                "\n[1/3] Dropping existing table: stock_master (if exists) ..."
            )
            conn.execute(text("DROP TABLE IF EXISTS stock_master CASCADE"))
            print("Done: dropped stock_master (if existed)")

            # 2. Recreate stock_master with full schema
            print("\n[2/3] Creating table: stock_master with full schema ...")
            conn.execute(
                text(
                    """
                CREATE TABLE stock_master (
                    id SERIAL PRIMARY KEY,

                    -- Identification
                    stock_code VARCHAR(10) UNIQUE NOT NULL,
                    stock_name VARCHAR(100) NOT NULL,
                    market_category VARCHAR(50),

                    -- Sector info
                    sector_code_33 VARCHAR(10),
                    sector_name_33 VARCHAR(100),
                    sector_code_17 VARCHAR(10),
                    sector_name_17 VARCHAR(100),

                    -- Scale info
                    scale_code VARCHAR(10),
                    scale_category VARCHAR(50),

                    -- Data lifecycle
                    data_date VARCHAR(8),
                    is_active INTEGER DEFAULT 1 NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
                """
                )
            )
            print("Done: created stock_master")

            # 3. Create indexes
            print("\n[3/3] Creating indexes for stock_master ...")
            conn.execute(
                text(
                    "CREATE INDEX idx_stock_master_code ON stock_master(stock_code)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX idx_stock_master_active ON stock_master(is_active)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX idx_stock_master_market ON stock_master(market_category)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX idx_stock_master_sector_33 ON stock_master(sector_code_33)"
                )
            )
            print("Done: created indexes for stock_master")

            # 4. Show resulting column definitions
            print("\n[Column definitions] stock_master")
            result = conn.execute(
                text(
                    """
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'stock_master'
                ORDER BY ordinal_position
                """
                )
            )

            print(f"{'column':<25} {'type':<20} {'max_len':<10}")
            print("-" * 60)
            for row in result:
                max_len = row[2] if row[2] is not None else "-"
                print(f"{row[0]:<25} {row[1]:<20} {max_len:<10}")

        print("\n" + "=" * 80)
        print("Migration completed successfully")
        print("=" * 80)

        print("\nNotes: key columns")
        print("  - sector_code_33: JPX 33-sector code")
        print("  - sector_name_33: JPX 33-sector name")
        print("  - sector_code_17: JPX 17-sector code")
        print("  - sector_name_17: JPX 17-sector name")
        print("  - scale_code: JPX scale code")
        print("  - scale_category: JPX scale category or TOPIX classification")
        print("  - data_date: String date YYYYMMDD")

    except Exception as e:
        print("\n" + "=" * 80)
        print("Migration failed")
        print("=" * 80)
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        engine.dispose()


if __name__ == "__main__":
    print("\nRecreate stock_master full schema")
    print(f"Database: {os.getenv('DB_NAME')}")
    print(f"Host: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print("\nPrerequisite: any old stock_master will be dropped.")

    # Run migration
    update_stock_master_schema()

    print("\nAll done: migration finished successfully")
