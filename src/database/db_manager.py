import sqlite3
import pandas as pd
from typing import Optional, Union, List
import logging
from pathlib import Path
from src.config import DB_PATH  # Updated import

class DatabaseManager:
    def __init__(self, db_path: Union[str, Path] = DB_PATH):
        """
        Initialize database manager.
        
        Args:
            db_path (Union[str, Path]): Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize database if it doesn't exist
        self._initialize_database()

    def _initialize_database(self) -> None:
        """Create database and tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create warehouses table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS warehouses (
                        warehouse_id TEXT PRIMARY KEY,
                        location TEXT NOT NULL,
                        capacity INTEGER NOT NULL,
                        storage_cost REAL NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create sales table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sales (
                        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE NOT NULL,
                        region TEXT NOT NULL,
                        product_id TEXT NOT NULL,
                        quantity INTEGER NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create index on sales date
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_sales_date
                    ON sales(date)
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            self.logger.error(f"Error initializing database: {str(e)}")
            raise

    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.logger.info("Database connection established")
        except sqlite3.Error as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise

    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            self.logger.info("Database connection closed")

    def import_csv_data(self, 
                       file_path: Union[str, Path], 
                       table_name: str) -> None:
        """
        Import data from CSV file into database.
        
        Args:
            file_path (Union[str, Path]): Path to CSV file
            table_name (str): Name of the target table
        """
        try:
            df = pd.read_csv(file_path)
            
            with sqlite3.connect(self.db_path) as conn:
                df.to_sql(
                    name=table_name,
                    con=conn,
                    if_exists='append',
                    index=False
                )
            
            self.logger.info(f"Successfully imported data to {table_name}")
            
        except Exception as e:
            self.logger.error(f"Error importing CSV data: {str(e)}")
            raise

    def get_warehouse_data(self) -> pd.DataFrame:
        """
        Retrieve warehouse data from database.
        
        Returns:
            pd.DataFrame: Warehouse data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM warehouses"
                df = pd.read_sql_query(query, conn)
                return df
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving warehouse data: {str(e)}")
            raise

    def get_sales_data(self, 
                      start_date: Optional[str] = None, 
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Retrieve sales data from database.
        
        Args:
            start_date (Optional[str]): Start date for filtering (YYYY-MM-DD)
            end_date (Optional[str]): End date for filtering (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Sales data
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = "SELECT * FROM sales"
                if start_date and end_date:
                    query += f" WHERE date BETWEEN '{start_date}' AND '{end_date}'"
                elif start_date:
                    query += f" WHERE date >= '{start_date}'"
                elif end_date:
                    query += f" WHERE date <= '{end_date}'"
                
                df = pd.read_sql_query(query, conn)
                return df
        except sqlite3.Error as e:
            self.logger.error(f"Error retrieving sales data: {str(e)}")
            raise

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()