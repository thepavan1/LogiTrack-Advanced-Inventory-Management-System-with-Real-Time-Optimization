import streamlit as st
import pandas as pd
from datetime import datetime
import os
import base64
from src.backend.data_loader import DataLoader
from src.backend.optimizer import InventoryOptimizer
from src.utils.helpers import format_currency, calculate_distance
import plotly.graph_objects as go

class LogiTrackApp:
    def __init__(self):
        """Initialize the LogiTrack application"""
        st.set_page_config(
            page_title="LogiTrack: Inventory Management System",
            page_icon="🏭",
            layout="wide"
        )
        
        # Initialize session state for login
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
            st.session_state.username = ''
        
        # Initialize data loader and optimizer
        self.data_loader = None
        self.optimizer = InventoryOptimizer()

    def get_file_download_link(self, filename):
        """Generate a download link for a file"""
        filepath = os.path.join('data', filename)
        try:
            with open(filepath, 'rb') as f:
                bytes = f.read()
            b64 = base64.b64encode(bytes).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download {filename}</a>'
            return href
        except FileNotFoundError:
            return f"File not found: {filename}"

    def login_page(self):
        """Display login page"""
        st.title("LogiTrack : Inventory Management")
        st.write("Welcome! Please enter your name to get started.")
        
        username = st.text_input("What should we call you?")
        
        if st.button("Enter"):
            if username.strip():
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.warning("Please enter a name")

    def show_user_context(self):
        """Display user context information"""
        with st.sidebar:
            st.write("---")
            st.subheader("👤 User Context")
            st.info(f"User: {st.session_state.username}")
            # Get real-time current datetime
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.info(f"UTC Time: {current_datetime}")

    def select_data_source(self):
        """Allow user to select data source and load appropriate data"""
        st.sidebar.title("📊 Data Source")
        data_source = st.sidebar.radio(
            "Select Data Source:",
            ["Sample Data", "Upload Data", "Database Connection"]
        )

        if data_source == "Sample Data":
            self.data_loader = DataLoader()
            st.sidebar.success("✅ Sample data loaded successfully!")
            return True
            
        elif data_source == "Upload Data":
            st.sidebar.info("📤 Upload your data files:")
            
            # File uploaders for each data type
            uploaded_files = {}
            required_files = {
                'warehouses': 'sample_warehouses.csv',
                'sales': 'sample_sales.csv',
                'products': 'product_inventory.csv',
                'suppliers': 'supplier_info.csv',
                'transport': 'transportation_costs.csv'
            }

            # Show template downloads
            st.sidebar.markdown("📑 **Templates:**")
            for file_type, filename in required_files.items():
                download_link = self.get_file_download_link(filename)
                st.sidebar.markdown(download_link, unsafe_allow_html=True)

            # File uploaders
            uploaded_files['warehouses'] = st.sidebar.file_uploader("Upload Warehouses Data", type=['csv'])
            uploaded_files['sales'] = st.sidebar.file_uploader("Upload Sales Data", type=['csv'])
            uploaded_files['products'] = st.sidebar.file_uploader("Upload Product Inventory", type=['csv'])
            uploaded_files['suppliers'] = st.sidebar.file_uploader("Upload Supplier Info", type=['csv'])
            uploaded_files['transport'] = st.sidebar.file_uploader("Upload Transport Costs", type=['csv'])

            if all(uploaded_files.values()):
                try:
                    self.data_loader = DataLoader(uploaded_files=uploaded_files)
                    st.sidebar.success("✅ Custom data loaded successfully!")
                    return True
                except Exception as e:
                    st.sidebar.error(f"Error loading data: {str(e)}")
                    st.sidebar.error("Please ensure your files match the template format")
                    return False
            else:
                st.sidebar.warning("⚠️ Please upload all required files")
                return False

        elif data_source == "Database Connection":
            st.sidebar.info("🔌 Database Connection")
            
            db_type = st.sidebar.selectbox("Database Type", ["PostgreSQL", "MySQL", "SQLite"])
            if db_type in ["PostgreSQL", "MySQL"]:
                host = st.sidebar.text_input("Host")
                port = st.sidebar.text_input("Port")
                database = st.sidebar.text_input("Database Name")
                username = st.sidebar.text_input("Username")
                password = st.sidebar.text_input("Password", type="password")
                
                if st.sidebar.button("Connect"):
                    try:
                        self.data_loader = DataLoader(
                            db_config={
                                'type': db_type,
                                'host': host,
                                'port': port,
                                'database': database,
                                'username': username,
                                'password': password
                            }
                        )
                        st.sidebar.success("✅ Connected to database successfully!")
                        return True
                    except Exception as e:
                        st.sidebar.error(f"Database connection failed: {str(e)}")
                        return False
            else:  # SQLite
                db_file = st.sidebar.file_uploader("Upload SQLite Database", type=['db', 'sqlite'])
                if db_file:
                    try:
                        self.data_loader = DataLoader(sqlite_file=db_file)
                        st.sidebar.success("✅ Connected to SQLite database successfully!")
                        return True
                    except Exception as e:
                        st.sidebar.error(f"Database connection failed: {str(e)}")
                        return False

        return False
    def show_guide(self):
        """Display the user guide/documentation"""
        st.title("📚 LogiTrack User Guide")
        
        # Introduction
        st.markdown("""
        Welcome to LogiTrack - Your Comprehensive Inventory Management System! 
        This guide will help you understand how to use all the features effectively.
        """)
        
        # Navigation using tabs
        tab_main, tab_features, tab_data, tab_optimize, tab_troubleshoot = st.tabs([
            "Getting Started", "Features", "Data Management", "Optimization Guide", "Troubleshooting"
        ])
        
        with tab_main:
            st.subheader("🚀 Getting Started")
            st.markdown("""
            ### Welcome to LogiTrack
            Current System Time: `2025-03-24 21:13:19 UTC`
            
            #### Quick Start
            1. **Login**: Enter your username to access the system
            2. **Select Data Source**: Choose from:
            - Sample Data (for testing)
            - Upload Your Data
            - Database Connection
            3. **Navigate**: Use the sidebar to access different features
            
            #### Basic Navigation
            - **Sidebar**: Contains main navigation and controls
            - **Top Bar**: Shows current user and system time
            - **Main Area**: Displays selected feature content
            """)
            
            st.info("💡 Tip: Start with the Overview page to get a snapshot of your inventory system!")

        with tab_features:
            st.subheader("🎯 Features Guide")
            
            # Overview Section
            st.markdown("### 📊 Overview")
            st.markdown("""
            The Overview dashboard provides:
            - Total Inventory Status
            - Pending Orders Count
            - Urgent Orders Alert
            - Products Needing Reorder
            - Warehouse Utilization Charts
            """)
            
            # Inventory Management
            st.markdown("### 📦 Inventory Management")
            st.markdown("""
            Track and manage your inventory:
            - View current stock levels
            - Monitor warehouse capacity
            - Check storage costs
            - Track last update times
            """)
            
            # Order Management
            st.markdown("### 📋 Order Management")
            st.markdown("""
            Handle all order-related tasks:
            - View pending orders
            - Track urgent orders
            - Check order history
            - Monitor delivery deadlines
            """)
            
            # Supplier Management
            st.markdown("### 🤝 Supplier Management")
            st.markdown("""
            Manage supplier relationships:
            - View supplier performance metrics
            - Track reliability scores
            - Monitor lead times
            - Check quality scores
            """)
            
            # Optimization
            st.markdown("### 🔄 Optimization")
            st.markdown("""
            Optimize your inventory distribution:
            - Run distribution optimization
            - View cost analysis
            - Check warehouse utilization
            - Monitor unfulfilled orders
            """)

        with tab_data:
            st.subheader("💾 Data Management Guide")
            
            # Sample Data Format
            st.markdown("### Sample Data Format")
            
            with st.expander("Warehouse Data Format"):
                st.code("""
    warehouse_id,name,capacity,current_stock,location,storage_cost,latitude,longitude
    W001,Mumbai Central,10000,7500,Mumbai,1200,19.0760,72.8777
    W002,Singapore Hub,15000,12000,Singapore,1500,1.3521,103.8198
                """)
                
            with st.expander("Sales/Orders Data Format"):
                st.code("""
    order_id,date,product_id,quantity,delivery_deadline,status,delivery_latitude,delivery_longitude
    ORD001,2025-03-24,P001,500,2025-03-26,Pending,19.0760,72.8777
    ORD002,2025-03-24,P002,750,2025-03-25,Urgent,1.3521,103.8198
                """)
            
            # File Upload Guide
            st.markdown("### 📤 Uploading Your Data")
            st.markdown("""
            1. Prepare your CSV files following the sample format
            2. Select "Upload Data" as your data source
            3. Upload your files using the provided interface
            4. System will validate your data format
            5. Confirm successful data loading
            """)

        with tab_optimize:
            st.subheader("⚙️ Optimization Guide")
            st.markdown("""
            ### Running Optimization
            
            1. **Preparation**
            - Ensure all warehouse data is up-to-date
            - Check pending orders
            - Verify delivery locations
            
            2. **Configuration**
            - Set solver time limit
            - Choose priority weights
            - Review optimization parameters
            
            3. **Execution**
            - Click "Run Optimization"
            - Wait for results
            - Review allocation plan
            
            4. **Results Analysis**
            - Check fulfillment rate
            - Review cost analysis
            - Monitor warehouse utilization
            - Address unfulfilled orders
            """)

        with tab_troubleshoot:
            st.subheader("❓ Troubleshooting")
            
            # Common Issues
            st.markdown("### Common Issues and Solutions")
            
            issues = {
                "Data Loading Errors": """
                - Verify CSV file format
                - Check required columns
                - Ensure valid coordinates
                - Confirm date formats
                """,
                "Optimization Issues": """
                - Check warehouse capacity
                - Verify order quantities
                - Confirm delivery locations
                - Review cost parameters
                """,
                "Display Problems": """
                - Refresh the page
                - Clear browser cache
                - Check data source
                - Verify timestamps
                """
            }
            
            for issue, solution in issues.items():
                with st.expander(issue):
                    st.markdown(solution)


    def show_overview_metrics(self):
        """Display key metrics in the overview section"""
        col1, col2, col3, col4 = st.columns(4)
        
        total_inventory = self.data_loader.warehouses_df['current_stock'].sum()
        total_capacity = self.data_loader.warehouses_df['capacity'].sum()
        
        with col1:
            st.metric(
                "Total Inventory",
                f"{total_inventory:,} units",
                f"{(total_inventory/total_capacity)*100:.1f}% of capacity"
            )
        
        pending_orders = len(self.data_loader.get_pending_orders(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        with col2:
            st.metric("Pending Orders", pending_orders)
        
        urgent_orders = len(self.data_loader.get_urgent_orders())
        with col3:
            st.metric("Urgent Orders", urgent_orders)
        
        reorder_needs = len(self.data_loader.calculate_reorder_needs())
        with col4:
            st.metric("Products to Reorder", reorder_needs)

    def show_inventory_status(self):
        """Display current inventory status"""
        st.subheader("📦 Inventory Status")
        
        warehouse_util = pd.DataFrame(self.data_loader.get_warehouse_utilization()).T
        st.bar_chart(warehouse_util['utilization'])
        
        st.dataframe(self.data_loader.get_current_inventory_status())

    def show_order_management(self):
        """Display order management section"""
        st.subheader("📋 Order Management")
        
        tabs = st.tabs(["Pending Orders", "Urgent Orders", "Order History"])
        
        with tabs[0]:
            pending_orders = self.data_loader.get_pending_orders(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.dataframe(pending_orders)
            
        with tabs[1]:
            urgent_orders = self.data_loader.get_urgent_orders()
            st.dataframe(urgent_orders)
            
        with tabs[2]:
            history = self.data_loader.get_order_history(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.dataframe(history)

    def show_supplier_info(self):
        """Display supplier information"""
        st.subheader("🤝 Supplier Performance")
        supplier_perf = self.data_loader.get_supplier_performance()
        
        st.bar_chart(supplier_perf.set_index('supplier_name')[['reliability_score', 'lead_time_reliability']])
        st.dataframe(supplier_perf)
    def show_distribution_map(self, warehouses, orders, allocation_results):
        """Display the distribution map visualization"""
        try:
            import plotly.graph_objects as go
            import numpy as np

            # Check if coordinates exist in the data
            required_columns = {
                'warehouses': ['latitude', 'longitude'],
                'orders': ['delivery_latitude', 'delivery_longitude']
            }

            missing_columns = {
                'warehouses': [col for col in required_columns['warehouses'] 
                            if col not in warehouses.columns],
                'orders': [col for col in required_columns['orders'] 
                        if col not in orders.columns]
            }

            if any(missing_columns.values()):
                st.warning("⚠️ Location data is incomplete. Map visualization requires latitude and longitude coordinates.")
                st.info("""
                To use the map visualization, please ensure your data includes:
                - For warehouses: 'latitude' and 'longitude' columns
                - For orders: 'delivery_latitude' and 'delivery_longitude' columns
                """)
                return

            # Create figure
            fig = go.Figure()

            # Add warehouses to the map
            fig.add_trace(go.Scattergeo(
                lon=warehouses['longitude'],
                lat=warehouses['latitude'],
                text=warehouses.apply(
                    lambda x: f"Name: {x['name']}<br>Stock: {x['current_stock']:,} units", 
                    axis=1
                ),
                mode='markers',
                name='Warehouses',
                marker=dict(
                    size=12,
                    symbol='square',
                    color='blue',
                    line=dict(
                        width=1,
                        color='white'
                    )
                ),
                hovertemplate=(
                    "<b>Warehouse</b><br>" +
                    "%{text}<br>" +
                    "Location: (%{lat:.4f}, %{lon:.4f})<br>" +
                    "<extra></extra>"
                )
            ))

            # Add delivery locations (orders) to the map
            fig.add_trace(go.Scattergeo(
                lon=orders['delivery_longitude'],
                lat=orders['delivery_latitude'],
                text=orders.apply(
                    lambda x: f"Order ID: {x['order_id']}<br>Quantity: {x['quantity']:,} units", 
                    axis=1
                ),
                mode='markers',
                name='Delivery Locations',
                marker=dict(
                    size=8,
                    symbol='circle',
                    color='red',
                    line=dict(
                        width=1,
                        color='white'
                    )
                ),
                hovertemplate=(
                    "<b>Delivery Location</b><br>" +
                    "%{text}<br>" +
                    "Location: (%{lat:.4f}, %{lon:.4f})<br>" +
                    "<extra></extra>"
                )
            ))

            # Add allocation lines with curved paths
            for warehouse_id, allocations in allocation_results['allocation_plan'].items():
                warehouse = warehouses[warehouses['warehouse_id'] == warehouse_id].iloc[0]
                
                for allocation in allocations:
                    order = orders[orders['order_id'] == allocation['order_id']].iloc[0]
                    
                    # Create curved path
                    lons = [warehouse['longitude'], order['delivery_longitude']]
                    lats = [warehouse['latitude'], order['delivery_latitude']]
                    
                    # Calculate path points
                    center_lon = np.mean(lons)
                    center_lat = np.mean(lats)
                    
                    # Add curved path
                    fig.add_trace(go.Scattergeo(
                        lon=[lons[0], center_lon, lons[1]],
                        lat=[lats[0], center_lat + 1, lats[1]],
                        mode='lines',
                        line=dict(
                            width=1,
                            color='rgba(0,150,0,0.3)'
                        ),
                        name=f'Route: {warehouse_id} → {allocation["order_id"]}',
                        showlegend=False,
                        hovertemplate=(
                            f"<b>Allocation Route</b><br>" +
                            f"From: {warehouse['name']}<br>" +
                            f"To: Order {allocation['order_id']}<br>" +
                            f"Quantity: {allocation['quantity']:,} units<br>" +
                            "<extra></extra>"
                        )
                    ))

            # Calculate map bounds
            all_lons = warehouses['longitude'].tolist() + orders['delivery_longitude'].tolist()
            all_lats = warehouses['latitude'].tolist() + orders['delivery_latitude'].tolist()
            
            lon_range = max(all_lons) - min(all_lons)
            lat_range = max(all_lats) - min(all_lats)
            
            center_lon = np.mean(all_lons)
            center_lat = np.mean(all_lats)

            # Update layout with dynamic bounds
            fig.update_layout(
                title={
                    'text': 'Global Distribution Map',
                    'y':0.95,
                    'x':0.5,
                    'xanchor': 'center',
                    'yanchor': 'top'
                },
                showlegend=True,
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01,
                    bgcolor="rgba(255, 255, 255, 0.8)"
                ),
                geo=dict(
                    projection_type='equirectangular',
                    showland=True,
                    showcountries=True,
                    showocean=True,
                    countrywidth=0.5,
                    landcolor='rgb(243, 243, 243)',
                    oceancolor='rgb(230, 230, 250)',
                    countrycolor='rgb(204, 204, 204)',
                    coastlinecolor='rgb(204, 204, 204)',
                    # Dynamic center and zoom
                    center=dict(
                        lon=center_lon,
                        lat=center_lat
                    ),
                    # Dynamic zoom based on data points
                    lonaxis=dict(
                        range=[min(all_lons) - lon_range*0.1, max(all_lons) + lon_range*0.1]
                    ),
                    lataxis=dict(
                        range=[min(all_lats) - lat_range*0.1, max(all_lats) + lat_range*0.1]
                    )
                ),
                height=600,
            )

            # Display the map
            st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error generating distribution map: {str(e)}")
            st.info("""
            To use the map visualization, please ensure your data includes location coordinates.
            Required columns:
            - Warehouses: latitude, longitude
            - Orders: delivery_latitude, delivery_longitude
            """)

    def run(self):
        """Run the Streamlit application"""
        if not st.session_state.logged_in:
            self.login_page()
            return

        st.title("🏭 LogiTrack: Inventory Management System")
        st.caption(f"Welcome back, {st.session_state.username}!")
        
        self.show_user_context()
        
        if not self.select_data_source():
            st.warning("Please select and configure a data source to continue")
            return

        # Updated sidebar navigation with Guide
        st.sidebar.title("⚙️ Controls")
        action = st.sidebar.selectbox(
            "Select Action",
            ["Overview", "Inventory Management", "Order Management", 
            "Supplier Management", "Optimization", "📚 User Guide"]  # Added Guide option
        )
        
        # Handle navigation including new Guide page
        if action == "📚 User Guide":
            self.show_guide()
        elif action == "Overview":
            self.show_overview_metrics()
            col1, col2 = st.columns(2)
            with col1:
                self.show_inventory_status()
            with col2:
                st.subheader("📊 Quick Stats")
                st.write(f"Last updated: {self.data_loader.current_datetime}")
        
        elif action == "Inventory Management":
            self.show_inventory_status()
            
        elif action == "Order Management":
            self.show_order_management()
            
        elif action == "Supplier Management":
            self.show_supplier_info()
            
        elif action == "Optimization":
            st.subheader("🔄 Inventory Optimization")
            
            st.sidebar.subheader("Optimization Parameters")
            st.sidebar.info(f"Current DateTime (UTC): {self.data_loader.current_datetime}")
            
            solver_time = st.sidebar.slider(
                "Solver Time Limit (seconds)",
                min_value=5,
                max_value=60,
                value=20
            )
            
            priority_weight = st.sidebar.select_slider(
                "Order Priority Weight",
                options=["Low", "Medium", "High"],
                value="Medium"
            )
            
            self.optimizer.solver_time = solver_time
            
            if st.button("🚀 Run Optimization"):
                try:
                    with st.spinner("Optimizing inventory distribution..."):
                        warehouses = self.data_loader.warehouses_df
                        orders = self.data_loader.get_pending_orders(self.data_loader.current_datetime)
                        
                        st.info("📊 Optimization Overview")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("Warehouses in scope:", len(warehouses))
                            st.write("Total warehouse capacity:", f"{warehouses['capacity'].sum():,} units")
                            st.write("Current total stock:", f"{warehouses['current_stock'].sum():,} units")
                        with col2:
                            st.write("Pending orders:", len(orders))
                            st.write("Total order quantity:", f"{orders['quantity'].sum():,} units")
                            st.write("Unique delivery regions:", len(orders['region'].unique()))
                        
                        results = self.optimizer.optimize(warehouses, orders)
                        
                        st.success("✅ Optimization complete!")
                        
                        # Show results in columns
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                "Total Cost", 
                                f"${results['total_cost']:,.2f}",
                                delta="-10%"
                            )
                        with col2:
                            st.metric(
                                "Solving Time", 
                                f"{results['solving_time']:.2f}s"
                            )
                        with col3:
                            st.metric(
                                "Status", 
                                results['status']
                            )
                        with col4:
                            fulfilled_percent = 100 - (len(results['unfulfilled_orders']) / len(orders) * 100)
                            st.metric(
                                "Order Fulfillment",
                                f"{fulfilled_percent:.1f}%"
                            )
                        
                        # Show detailed results in tabs
                        tabs = st.tabs(["Allocation Plan", "Warehouse Utilization", "Unfulfilled Orders", "Visualization"])
                        
                        with tabs[0]:
                            st.subheader("📦 Allocation Plan")
                            allocation_df = pd.DataFrame([
                                {
                                    'Warehouse': w,
                                    'Order ID': item['order_id'],
                                    'Quantity': item['quantity']
                                }
                                for w, orders in results['allocation_plan'].items()
                                for item in orders
                            ])
                            if not allocation_df.empty:
                                st.dataframe(allocation_df)
                            else:
                                st.warning("No allocations generated")
                        
                        with tabs[1]:
                            st.subheader("🏭 Warehouse Utilization")
                            util_df = pd.DataFrame([
                                {
                                    'Warehouse': w,
                                    'Used Capacity': data['used_capacity'],
                                    'Total Capacity': data['total_capacity'],
                                    'Utilization %': data['utilization_percentage']
                                }
                                for w, data in results['warehouse_utilization'].items()
                            ])
                            st.dataframe(util_df)
                            st.bar_chart(util_df.set_index('Warehouse')['Utilization %'])
                        
                        with tabs[2]:
                            if results['unfulfilled_orders']:
                                st.warning("⚠️ Some orders could not be fulfilled completely")
                                st.dataframe(pd.DataFrame(results['unfulfilled_orders']))
                            else:
                                st.success("✅ All orders can be fulfilled!")
                        
                        with tabs[3]:
                            st.subheader("🗺️ Distribution Map")
                            if all(col in warehouses.columns for col in ['latitude', 'longitude']) and \
                            all(col in orders.columns for col in ['delivery_latitude', 'delivery_longitude']):
                                self.show_distribution_map(warehouses, orders, results)
                            else:
                                st.info("""
                                Map visualization is available when location coordinates are provided.
                                Required data:
                                - Warehouse locations (latitude, longitude)
                                - Delivery locations (delivery_latitude, delivery_longitude)
                                """)

                except Exception as e:
                    st.error(f"Optimization error: {str(e)}")
                    st.error("Please check your data and try again")

        # Footer
        st.markdown("---")
        st.markdown(
            "<p style='text-align: center;'>© 2025 | Made with ♥ by "
            "<a href='https://github.com/tanishpoddar' target='_blank' "
            "style='color: inherit; text-decoration: none;'>Tanish Poddar</a></p>", 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    app = LogiTrackApp()
    app.run()