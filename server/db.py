import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, Column, String, Boolean, DateTime, Integer, Text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging

Base = declarative_base()

class Link(Base):
    __tablename__ = "links"
    
    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    status = Column(Boolean, default=False)
    last_checked = Column(DateTime, default=lambda: datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")))
    headers = Column(Text, default="{}")  # Store headers as JSON string


def get_database_url():
    """Get database URL from environment or config file"""
    database_url = os.environ.get("CRON_DATABASE_URL")
    if not database_url:
        # Try to load from .env file
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if line.startswith('CRON_DATABASE_URL='):
                        database_url = line.strip().split('=', 1)[1]
                        break
    
    # If still not found, use default
    if not database_url:
        database_url = "sqlite:///./cron_manager.db"
    
    return database_url


def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def backup_old_table(engine, old_table_name, new_table_name):
    """Backup old table with timestamp suffix"""
    from sqlalchemy import text
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_table_name = f"{old_table_name}_backup_{timestamp}"
    
    try:
        with engine.connect() as conn:
            # Rename old table to backup name
            conn.execute(text(f"ALTER TABLE {old_table_name} RENAME TO {backup_table_name}"))
            conn.commit()
            logging.info(f"Backed up {old_table_name} to {backup_table_name}")
        return backup_table_name
    except Exception as e:
        logging.error(f"Failed to backup table {old_table_name}: {str(e)}")
        return None


def merge_old_table_data(engine, old_table_name, new_table_name):
    """Merge data from old table to new table based on common columns"""
    from sqlalchemy import MetaData, Table, select, text
    from sqlalchemy.exc import NoSuchTableError
    
    metadata = MetaData()
    
    try:
        # Reflect the old table
        old_table = Table(old_table_name, metadata, autoload_with=engine)
        new_table = Table(new_table_name, metadata, autoload_with=engine)
        
        # Find common columns between old and new table
        common_columns = []
        for old_col in old_table.columns:
            for new_col in new_table.columns:
                if old_col.name == new_col.name:
                    common_columns.append(old_col.name)
                    break
        
        if not common_columns:
            logging.warning(f"No common columns found between {old_table_name} and {new_table_name}")
            return False
            
        # Build INSERT ... SELECT query to migrate data
        columns_str = ', '.join(common_columns)
        query = text(f"""
            INSERT INTO {new_table_name} ({columns_str})
            SELECT {columns_str} FROM {old_table_name}
            WHERE NOT EXISTS (
                SELECT 1 FROM {new_table_name} n
                WHERE n.id = {old_table_name}.id
            )
        """)
        
        with engine.connect() as conn:
            result = conn.execute(query)
            conn.commit()
            logging.info(f"Migrated {result.rowcount} rows from {old_table_name} to {new_table_name}")
            return True
            
    except NoSuchTableError as e:
        logging.error(f"Table does not exist: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Error merging table data: {str(e)}")
        return False


def migrate_schema_if_needed(engine):
    """Check and migrate schema if needed"""
    logging.basicConfig(level=logging.INFO)
    
    # Check if the links table exists and has the expected structure
    if not check_table_exists(engine, "links"):
        # If table doesn't exist, create all tables
        Base.metadata.create_all(engine)
        logging.info("Created new tables")
        return
    
    # Check for old table structures that might need migration
    inspector = inspect(engine)
    columns = inspector.get_columns('links')
    column_names = [col['name'] for col in columns]
    
    # Define expected columns based on our model
    expected_columns = {'id', 'url', 'status', 'last_checked', 'headers'}
    current_columns = set(column_names)
    
    # If there are missing columns, we might need to recreate or alter the table
    missing_columns = expected_columns - current_columns
    extra_columns = current_columns - expected_columns
    
    if missing_columns or extra_columns:
        logging.info(f"Schema mismatch detected:")
        logging.info(f"Missing columns: {missing_columns}")
        logging.info(f"Extra columns: {extra_columns}")
        
        # Backup the old table
        backup_name = backup_old_table(engine, "links", "links")
        if backup_name:
            # Recreate the table with new schema
            Base.metadata.tables['links'].drop(engine)
            Base.metadata.create_all(engine)
            
            # Try to merge data from backup
            merge_old_table_data(engine, backup_name, "links")


def create_db_and_tables():
    """Create database tables with migration support"""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=True, pool_pre_ping=True)
    
    try:
        # Perform migration if needed
        migrate_schema_if_needed(engine)
    except Exception as e:
        logging.error(f"Migration failed: {str(e)}")
        # Fallback: create tables normally
        Base.metadata.create_all(engine)
    
    return engine


def get_session():
    engine = create_db_and_tables()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
