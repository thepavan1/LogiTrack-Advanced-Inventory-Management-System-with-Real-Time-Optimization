import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging
import sqlite3

class DataLoader:
    def __init__(self, uploaded_files=None, db_config=None, sqlite_file=None):
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Set current context with the specific time you provided
        self.current_user = "tanishpoddar"
        self.current_datetime = "2025-03-24 20:47:08"  # Updated timestamp
        
        # Initialize data frames
        self.warehouses_df = None
        self.sales_df = None
        self.products_df = None
        self.suppliers_df = None
        self.transport_df = None
        
        # Load data based on source
        if uploaded_files:
            self.load_uploaded_files(uploaded_files)
        elif db_config:
            self.load_from_database(db_config)
        elif sqlite_file:
            self.load_from_sqlite(sqlite_file)
        else:
            self.load_sample_data()

        # Validate data after loading
        if not self.validate_data():
            raise ValueError("Data validation failed")

    def load_sample_data(self):
        """Load sample data from CSV files"""
        try:
            self.warehouses_df = pd.read_csv('data/sample_warehouses.csv')
            self.sales_df = pd.read_csv('data/sample_sales.csv')
            self.products_df = pd.read_csv('data/product_inventory.csv')
            self.suppliers_df = pd.read_csv('data/supplier_info.csv')
            self.transport_df = pd.read_csv('data/transportation_costs.csv')
            self.process_data()
            self.logger.info("Sample data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading sample data: {str(e)}")
            raise

    def process_data(self):
        """Process loaded data (common for all data sources)"""
        try:
            # Convert date columns
            date_columns = {
                'sales_df': ['date', 'delivery_deadline'],
                'warehouses_df': ['last_updated']
            }
            
            for df_name, columns in date_columns.items():
                df = getattr(self, df_name)
                for col in columns:
                    if col in df.columns:
                        df[col] = pd.to_datetime(df[col])
            
            # Ensure coordinates and numeric columns are properly typed
            numeric_columns = {
                'warehouses_df': {
                    'float': ['latitude', 'longitude', 'storage_cost'],
                    'int': ['capacity', 'current_stock']
                },
                'sales_df': {
                    'float': ['delivery_latitude', 'delivery_longitude'],
                    'int': ['quantity']
                }
            }
            
            for df_name, type_dict in numeric_columns.items():
                df = getattr(self, df_name)
                for dtype, columns in type_dict.items():
                    for col in columns:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')
                            if dtype == 'int':
                                df[col] = df[col].fillna(0).astype(int)
                            else:
                                df[col] = df[col].fillna(0.0).astype(float)
            
            # Sort sales data
            self.sales_df = self.sales_df.sort_values('date', ascending=False)
            
            # Add audit columns
            self.add_audit_columns()
            
            self.logger.info("Data processed successfully")
        except Exception as e:
            self.logger.error(f"Error processing data: {str(e)}")
            raise

    def validate_data(self) -> bool:
        """Validate loaded data for required columns and data types"""
        try:
            # Required columns for each dataframe
            required_columns = {
                'warehouses_df': [
                    'warehouse_id', 'name', 'capacity', 'current_stock', 
                    'location', 'storage_cost', 'latitude', 'longitude'
                ],
                'sales_df': [
                    'order_id', 'date', 'product_id', 'quantity',
                    'delivery_deadline', 'status', 'delivery_latitude', 'delivery_longitude'
                ],
                'products_df': [
                    'product_id', 'product_name', 'reorder_point', 
                    'min_order_qty', 'supplier_id'
                ],
                'suppliers_df': [
                    'supplier_id', 'supplier_name', 'reliability_score',
                    'lead_time_reliability', 'quality_score'
                ],
                'transport_df': [
                    'origin_region', 'destination_region', 'cost_per_mile'
                ]
            }
            
            # Check each dataframe for required columns
            for df_name, columns in required_columns.items():
                df = getattr(self, df_name)
                if df is None:
                    self.logger.error(f"DataFrame {df_name} is not loaded")
                    return False
                    
                missing_cols = [col for col in columns if col not in df.columns]
                if missing_cols:
                    self.logger.error(f"Missing columns in {df_name}: {missing_cols}")
                    return False

            # Validate coordinate ranges
            if 'latitude' in self.warehouses_df.columns:
                invalid_lat = self.warehouses_df[
                    (self.warehouses_df['latitude'] < -90) | 
                    (self.warehouses_df['latitude'] > 90)
                ]
                if not invalid_lat.empty:
                    self.logger.error("Invalid warehouse latitudes found")
                    return False

            if 'longitude' in self.warehouses_df.columns:
                invalid_lon = self.warehouses_df[
                    (self.warehouses_df['longitude'] < -180) | 
                    (self.warehouses_df['longitude'] > 180)
                ]
                if not invalid_lon.empty:
                    self.logger.error("Invalid warehouse longitudes found")
                    return False

            # Similar checks for sales coordinates
            if 'delivery_latitude' in self.sales_df.columns:
                invalid_lat = self.sales_df[
                    (self.sales_df['delivery_latitude'] < -90) | 
                    (self.sales_df['delivery_latitude'] > 90)
                ]
                if not invalid_lat.empty:
                    self.logger.error("Invalid delivery latitudes found")
                    return False

            if 'delivery_longitude' in self.sales_df.columns:
                invalid_lon = self.sales_df[
                    (self.sales_df['delivery_longitude'] < -180) | 
                    (self.sales_df['delivery_longitude'] > 180)
                ]
                if not invalid_lon.empty:
                    self.logger.error("Invalid delivery longitudes found")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Data validation error: {str(e)}")
            return False

    def load_uploaded_files(self, uploaded_files):
        """Load data from uploaded files"""
        try:
            self.warehouses_df = pd.read_csv(uploaded_files['warehouses'])
            self.sales_df = pd.read_csv(uploaded_files['sales'])
            self.products_df = pd.read_csv(uploaded_files['products'])
            self.suppliers_df = pd.read_csv(uploaded_files['suppliers'])
            self.transport_df = pd.read_csv(uploaded_files['transport'])
            self.process_data()
            self.logger.info("Uploaded files loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading uploaded files: {str(e)}")
            raise

    def load_from_database(self, db_config):
        """Load data from database"""
        try:
            # Create database connection string
            if db_config['type'] == 'PostgreSQL':
                conn_string = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            elif db_config['type'] == 'MySQL':
                conn_string = f"mysql+pymysql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
            
            # Load data from database
            self.warehouses_df = pd.read_sql("SELECT * FROM warehouses", conn_string)
            self.sales_df = pd.read_sql("SELECT * FROM sales", conn_string)
            self.products_df = pd.read_sql("SELECT * FROM products", conn_string)
            self.suppliers_df = pd.read_sql("SELECT * FROM suppliers", conn_string)
            self.transport_df = pd.read_sql("SELECT * FROM transport", conn_string)
            self.process_data()
            self.logger.info("Database data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading from database: {str(e)}")
            raise

    def load_from_sqlite(self, sqlite_file):
        """Load data from SQLite database"""
        try:
            conn = sqlite3.connect(sqlite_file.name)
            self.warehouses_df = pd.read_sql("SELECT * FROM warehouses", conn)
            self.sales_df = pd.read_sql("SELECT * FROM sales", conn)
            self.products_df = pd.read_sql("SELECT * FROM products", conn)
            self.suppliers_df = pd.read_sql("SELECT * FROM suppliers", conn)
            self.transport_df = pd.read_sql("SELECT * FROM transport", conn)
            conn.close()
            self.process_data()
            self.logger.info("SQLite data loaded successfully")
        except Exception as e:
            self.logger.error(f"Error loading from SQLite: {str(e)}")
            raise

    

    def add_audit_columns(self):
        """Add audit columns to dataframes"""
        for df in [self.warehouses_df, self.sales_df, self.products_df, self.suppliers_df, self.transport_df]:
            df['last_modified_by'] = self.current_user
            df['last_modified_at'] = self.current_datetime

    def get_current_inventory_status(self) -> pd.DataFrame:
        """Get current inventory levels across all warehouses"""
        return self.warehouses_df[[
            'warehouse_id', 'name', 'capacity', 'current_stock', 
            'storage_cost', 'last_updated'
        ]]

    def get_pending_orders(self, current_date: str) -> pd.DataFrame:
        """Get pending orders that need to be fulfilled"""
        current_date = pd.to_datetime(current_date)
        return self.sales_df[
            (self.sales_df['delivery_deadline'] >= current_date) &
            (self.sales_df['date'] <= current_date)
        ]

    def get_urgent_orders(self, days_threshold: int = 2) -> pd.DataFrame:
        """Get orders that need urgent attention based on delivery deadline"""
        current_date = pd.to_datetime(self.current_datetime)
        urgent_mask = (self.sales_df['delivery_deadline'] - current_date).dt.days <= days_threshold
        return self.sales_df[urgent_mask].sort_values('delivery_deadline')

    def get_order_history(self, current_date: str, days_back: int = 7) -> pd.DataFrame:
        current_date = pd.to_datetime(current_date)
        start_date = current_date - pd.Timedelta(days=days_back)
        
        history = self.sales_df[
            (self.sales_df['date'] >= start_date) &
            (self.sales_df['date'] <= current_date)
        ].copy()
        
        # Add status and time since order
        history['status'] = np.where(
            history['date'] < current_date, 
            'Delivered', 
            'In Progress'
        )
        
        # Calculate time difference in hours
        time_diff_hours = (current_date - history['date']).dt.total_seconds() / 3600
        
        # Convert time difference to human-readable format
        history['time_since_order'] = np.where(
            time_diff_hours < 24,
            time_diff_hours.astype(int).astype(str) + ' hours ago',
            (time_diff_hours / 24).astype(int).astype(str) + ' days ago'
        )
        
        return history.sort_values('date', ascending=False)

    def get_warehouse_utilization(self) -> Dict:
        """Calculate current utilization for each warehouse"""
        utilization = {}
        for _, warehouse in self.warehouses_df.iterrows():
            util_percent = (warehouse['current_stock'] / warehouse['capacity']) * 100
            utilization[warehouse['warehouse_id']] = {
                'name': warehouse['name'],
                'utilization': util_percent,
                'available_capacity': warehouse['capacity'] - warehouse['current_stock'],
                'location': warehouse['location']
            }
        return utilization

    def get_supplier_performance(self) -> pd.DataFrame:
        """Get supplier performance metrics"""
        return self.suppliers_df[[
            'supplier_id', 'supplier_name', 'reliability_score',
            'lead_time_reliability', 'quality_score'
        ]]

    def calculate_reorder_needs(self) -> pd.DataFrame:
        """Calculate which products need reordering"""
        reorder_needs = []
        for _, product in self.products_df.iterrows():
            total_stock = sum(
                warehouse['current_stock'] 
                for _, warehouse in self.warehouses_df.iterrows()
            )
            if total_stock <= product['reorder_point']:
                reorder_needs.append({
                    'product_id': product['product_id'],
                    'product_name': product['product_name'],
                    'current_stock': total_stock,
                    'reorder_point': product['reorder_point'],
                    'min_order_qty': product['min_order_qty'],
                    'supplier_id': product['supplier_id']
                })
        return pd.DataFrame(reorder_needs)

    def get_transport_costs(self, origin: str, destination: str) -> float:
        """Get transportation cost between two locations"""
        route = self.transport_df[
            (self.transport_df['origin_region'] == origin) &
            (self.transport_df['destination_region'] == destination)
        ]
        return route['cost_per_mile'].iloc[0] if not route.empty else None
