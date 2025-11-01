# -*- coding: utf-8 -*-
"""Create timeframe tables for stock OHLCV data.

Tables created if missing:
- stocks_1m, stocks_5m, stocks_15m, stocks_30m
- stocks_1h, stocks_1d, stocks_1wk, stocks_1mo

If legacy table `stocks_daily` exists, it will be renamed to `stocks_1d`
with related constraints and indexes renamed accordingly.

Usage:
    python app/migrations/create_timeframe_tables.py
"""

import logging
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.models import (
    Stocks1d,
    Stocks1h,
    Stocks1m,
    Stocks1mo,
    Stocks1wk,
    Stocks5m,
    Stocks15m,
    Stocks30m,
)


# Make project root importable
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def get_database_url() -> str:
    """Return database URL constructed from environment variables."""
    return (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )


def check_table_exists(engine, table_name: str) -> bool:
    """Return True if `table_name` exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_stocks_daily_to_stocks_1d(engine) -> None:
    """Rename legacy `stocks_daily` to `stocks_1d` and adjust names if needed."""
    try:
        with engine.connect() as conn:
            if check_table_exists(engine, "stocks_daily"):
                logger.info(
                    "Found legacy table stocks_daily. Migrating to stocks_1d ..."
                )

                # Create stocks_1d if not exists by renaming stocks_daily
                if not check_table_exists(engine, "stocks_1d"):
                    # Rename table
                    conn.execute(
                        text("ALTER TABLE stocks_daily RENAME TO stocks_1d;")
                    )

                    # Rename constraints
                    conn.execute(
                        text(
                            "ALTER TABLE stocks_1d RENAME CONSTRAINT uk_stocks_daily_symbol_date TO uk_stocks_1d_symbol_date;"
                        )
                    )
                    conn.execute(
                        text(
                            "ALTER TABLE stocks_1d RENAME CONSTRAINT ck_stocks_daily_prices TO ck_stocks_1d_prices;"
                        )
                    )
                    conn.execute(
                        text(
                            "ALTER TABLE stocks_1d RENAME CONSTRAINT ck_stocks_daily_volume TO ck_stocks_1d_volume;"
                        )
                    )
                    conn.execute(
                        text(
                            "ALTER TABLE stocks_1d RENAME CONSTRAINT ck_stocks_daily_price_logic TO ck_stocks_1d_price_logic;"
                        )
                    )

                    # Rename indexes
                    conn.execute(
                        text(
                            "ALTER INDEX idx_stocks_daily_symbol RENAME TO idx_stocks_1d_symbol;"
                        )
                    )
                    conn.execute(
                        text(
                            "ALTER INDEX idx_stocks_daily_date RENAME TO idx_stocks_1d_date;"
                        )
                    )
                    conn.execute(
                        text(
                            "ALTER INDEX idx_stocks_daily_symbol_date_desc RENAME TO idx_stocks_1d_symbol_date_desc;"
                        )
                    )

                    conn.commit()
                    logger.info(
                        "Renamed stocks_daily to stocks_1d and updated constraints/indexes."
                    )
                else:
                    logger.info(
                        "Table stocks_1d already exists. Skipping legacy migration."
                    )
            else:
                logger.info(
                    "Legacy table stocks_daily not found. Proceeding with table creation."
                )

    except SQLAlchemyError as e:
        logger.error(f"Error migrating stocks_daily to stocks_1d: {str(e)}")
        raise


def create_timeframe_tables(engine) -> None:
    """Create timeframe tables if they do not already exist."""
    try:
        tables_to_create = [
            ("stocks_1m", Stocks1m),
            ("stocks_5m", Stocks5m),
            ("stocks_15m", Stocks15m),
            ("stocks_30m", Stocks30m),
            ("stocks_1h", Stocks1h),
            ("stocks_1d", Stocks1d),
            ("stocks_1wk", Stocks1wk),
            ("stocks_1mo", Stocks1mo),
        ]

        for table_name, model_class in tables_to_create:
            if not check_table_exists(engine, table_name):
                logger.info(f"Creating table: {table_name} ...")
                model_class.__table__.create(engine)
                logger.info(f"Done: created {table_name}.")
            else:
                logger.info(f"Table exists: {table_name}. Skipping creation.")

    except SQLAlchemyError as e:
        logger.error(f"Error creating timeframe tables: {str(e)}")
        raise


def verify_tables(engine) -> None:
    """Log presence and basic metadata of expected timeframe tables."""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        expected_tables = [
            "stocks_1m",
            "stocks_5m",
            "stocks_15m",
            "stocks_30m",
            "stocks_1h",
            "stocks_1d",
            "stocks_1wk",
            "stocks_1mo",
        ]

        logger.info("Verification: expected timeframe tables")
        for table in expected_tables:
            if table in existing_tables:
                logger.info(f"OK: {table} exists")

                # Indexes
                indexes = inspector.get_indexes(table)
                logger.info(f"  Index count: {len(indexes)}")

                # Constraints (limited via SQLAlchemy's inspector)
                constraints = inspector.get_check_constraints(table)
                logger.info(f"  Check constraints: {len(constraints)}")
            else:
                logger.error(f"Missing: {table} table not found")

    except SQLAlchemyError as e:
        logger.error(f"Error verifying timeframe tables: {str(e)}")
        raise


def main() -> None:
    """Entry point for the timeframe table migration."""
    try:
        logger.info("Starting timeframe table migration")

        # Database setup
        database_url = get_database_url()
        engine = create_engine(database_url)
        logger.info("Connected to database")

        # 1. Migrate legacy daily table
        migrate_stocks_daily_to_stocks_1d(engine)

        # 2. Create timeframe tables
        create_timeframe_tables(engine)

        # 3. Verify tables
        verify_tables(engine)

        logger.info("Timeframe table migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        sys.exit(1)
    finally:
        if "engine" in locals():
            engine.dispose()


if __name__ == "__main__":
    main()
