# -*- coding: utf-8 -*-
"""Create stock_master and stock_master_updates tables (Phase 2).

Updated: 2025-10-12
Description: Create base tables for JPX stock master and update log.

Usage:
    python app/migrations/create_stock_master_tables.py
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


def create_stock_master_tables():
    """Create stock_master and stock_master_updates tables and related indexes."""
    print("=" * 80)
    print("Starting migration: create stock_master and stock_master_updates")
    print("=" * 80)

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # 1. Create stock_master table
            print("\n[1/4] Creating table: stock_master ...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS stock_master (
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
            print("Done: created table stock_master")

            # 2. Create indexes for stock_master
            print("\n[2/4] Creating indexes for stock_master ...")
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_stock_master_code ON stock_master(stock_code)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_stock_master_active ON stock_master(is_active)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_stock_master_market ON stock_master(market_category)"
                )
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_stock_master_sector_33 ON stock_master(sector_code_33)"
                )
            )
            print("Done: created indexes for stock_master")

            # 3. Create stock_master_updates table
            print("\n[3/4] Creating table: stock_master_updates ...")
            conn.execute(
                text(
                    """
                CREATE TABLE IF NOT EXISTS stock_master_updates (
                    id SERIAL PRIMARY KEY,
                    update_type VARCHAR(20) NOT NULL,
                    total_stocks INTEGER NOT NULL,
                    added_stocks INTEGER DEFAULT 0,
                    updated_stocks INTEGER DEFAULT 0,
                    removed_stocks INTEGER DEFAULT 0,
                    status VARCHAR(20) NOT NULL,
                    error_message TEXT,
                    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP WITH TIME ZONE
                )
                """
                )
            )
            print("Done: created table stock_master_updates")

            # 4. Verify created tables
            print("\n[4/4] Verifying created tables ...")
            result = conn.execute(
                text(
                    """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('stock_master', 'stock_master_updates')
                ORDER BY table_name
                """
                )
            )

            created_tables = [row[0] for row in result]
            print(f"Created tables: {', '.join(created_tables)}")

            # Verify indexes
            print(
                "\n[Index verification] Listing indexes for created tables ..."
            )
            result = conn.execute(
                text(
                    """
                SELECT tablename, indexname
                FROM pg_indexes
                WHERE schemaname = 'public'
                AND tablename IN ('stock_master', 'stock_master_updates')
                ORDER BY tablename, indexname
                """
                )
            )

            for row in result:
                print(f"  - {row[0]}.{row[1]}")

        print("\n" + "=" * 80)
        print("Migration completed successfully")
        print("=" * 80)

    except Exception as e:
        print("\n" + "=" * 80)
        print("Migration failed")
        print("=" * 80)
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        engine.dispose()


def verify_tables():
    """Print column definitions for stock_master and stock_master_updates."""
    print("\n" + "=" * 80)
    print("Verifying table columns")
    print("=" * 80)

    engine = create_engine(DATABASE_URL)

    try:
        with engine.begin() as conn:
            # stock_master columns
            print("\n[stock_master columns]")
            result = conn.execute(
                text(
                    """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'stock_master'
                ORDER BY ordinal_position
                """
                )
            )

            print(
                f"{'column':<20} {'type':<20} {'nullable':<10} {'default':<30}"
            )
            print("-" * 80)
            for row in result:
                print(
                    f"{row[0]:<20} {row[1]:<20} {row[2]:<10} {str(row[3])[:30]:<30}"
                )

            # stock_master_updates columns
            print("\n[stock_master_updates columns]")
            result = conn.execute(
                text(
                    """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'stock_master_updates'
                ORDER BY ordinal_position
                """
                )
            )

            print(
                f"{'column':<20} {'type':<20} {'nullable':<10} {'default':<30}"
            )
            print("-" * 80)
            for row in result:
                print(
                    f"{row[0]:<20} {row[1]:<20} {row[2]:<10} {str(row[3])[:30]:<30}"
                )

        print("\nVerification completed")

    except Exception as e:
        print(f"\nVerification failed: {e}")
        sys.exit(1)

    finally:
        engine.dispose()


if __name__ == "__main__":
    print("\nStock Master migration")
    print(f"Database: {os.getenv('DB_NAME')}")
    print(f"Host: {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")

    # Run migration
    create_stock_master_tables()

    # Verify tables
    verify_tables()
