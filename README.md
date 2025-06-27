LogiTrack : Inventory Management System

LogiTrack is a modern, web-based inventory management system built with Python and Streamlit. It provides real-time optimization of warehouse inventory distribution, order management, and supply chain analytics.

a) Features
1) Dashboard & Analytics
Real-time inventory tracking

Warehouse utilization metrics

Order fulfillment statistics

Supply chain performance indicators

Interactive data visualizations

🗺2) Inventory Distribution
Multi-warehouse optimization

Geographic distribution mapping

Cost-effective allocation algorithms

Real-time route visualization

3) Order Management
Order tracking and status updates

Priority-based fulfillment

Delivery deadline monitoring

Automated allocation suggestions

4) Warehouse Management
Capacity utilization tracking

Stock level monitoring

Storage cost optimization

Location-based analytics

5) Supplier Management
Supplier performance metrics

Reliability scoring

Lead time tracking

Quality assessment

b) Getting Started
Prerequisites
Python 3.9 or higher

pip package manager

Git (optional)

Installation

Create and activate virtual environment (optional but recommended):

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

bash
pip install -r requirements.txt
Run the application:

bash
streamlit run src/app.py
c) Project Structure
text
logitrack/
├── src/
│   ├── app.py              # Main Streamlit application
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── data_loader.py  # Data handling and processing
│   │   └── optimizer.py    # Optimization algorithms
│   └── utils/
│       └── helpers.py      # Utility functions
├── data/
│   ├── sample_warehouses.csv
│   ├── sample_sales.csv
│   └── other sample data...
├── tests/
│   └── test files...
├── docs/
│   └── documentation files...
├── requirements.txt
├── README.md
d) Design Analysis and Algorithms (DAA)
1) System Architecture
LogiTrack follows a modular architecture with these key components:

Frontend: Streamlit-based UI with interactive visualizations

Backend: Python-based processing engine

Data Layer: CSV/DB connectors for data persistence

Optimization Engine: Core algorithms for inventory distribution

2) Core Algorithms
a) Inventory Allocation Algorithm
Problem: Optimal distribution of inventory across warehouses

Algorithm: Modified Knapsack Problem solution with constraints

Complexity: O(nW) where n=items, W=warehouse capacity

Optimization: Minimizes storage costs while meeting demand

b) Order Fulfillment Algorithm
Problem: Selecting best warehouse for order fulfillment

Algorithm: Dijkstra's variant with multi-factor scoring:

Distance to destination

Warehouse stock levels

Shipping costs

Delivery deadlines

Complexity: O(E + V log V) for route calculation

c) Warehouse Optimization
Problem: Balancing stock levels across warehouses

Algorithm: Genetic Algorithm approach with:

Chromosomes representing stock distributions

Fitness function considering:

Transportation costs

Storage costs

Demand forecasts

Complexity: O(g*n) where g=generations, n=population size

d) Route Optimization
Problem: Delivery route planning for multiple orders

Algorithm: Hybrid of Nearest Neighbor and 2-opt optimization

Complexity: O(n^2) for route improvements

3) Performance Analysis
Algorithm	Best Case	Average Case	Worst Case	Space Complexity
Inventory Allocation	O(n)	O(nW)	O(nW)	O(W)
Order Fulfillment	O(V log V)	O(E + V log V)	O(V^2)	O(V)
Warehouse Optimization	O(n)	O(g*n)	O(g*n^2)	O(n)
Route Optimization	O(n)	O(n^2)	O(n^3)	O(n^2)
4) Data Structures
Priority Queues: For order prioritization

Graphs: For warehouse network representation

Hash Tables: For fast inventory lookups

Geospatial Indices: For location-based queries

e) Usage
Login: Enter your credentials to access the system.

Data Source: Choose between:

Sample data

Upload your data (CSV)

Database connection

Navigation: Use the sidebar to access different features:

Overview

Inventory Management

Order Management

Supplier Management

Optimization

User Guide

f) Data Format
Warehouse Data (CSV)
text
warehouse_id,name,capacity,current_stock,location,storage_cost,latitude,longitude
W001,Mumbai Central,10000,7500,Mumbai,1200,19.0760,72.8777
W002,Singapore Hub,15000,12000,Singapore,1500,1.3521,103.8198
Order Data (CSV)
text
order_id,date,product_id,quantity,delivery_deadline,status,delivery_latitude,delivery_longitude
ORD001,2025-03-24,P001,500,2025-03-26,Pending,19.0760,72.8777
ORD002,2025-03-24,P002,750,2025-03-25,Urgent,1.3521,103.8198
g) Configuration
The system supports various configuration options:

Database connections (MySQL, PostgreSQL, SQLite)

Optimization parameters

Visualization preferences

Time zone settings

The DAA section provides a comprehensive overview of the algorithmic foundations of LogiTrack, explaining the core problems, solutions, and their computational characteristics. This helps users understand the system's capabilities and limitations at a deeper level.
