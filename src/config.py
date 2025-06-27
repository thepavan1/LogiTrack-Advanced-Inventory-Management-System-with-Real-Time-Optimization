import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directory
DATA_DIR = os.path.join(BASE_DIR, "data")

# Database settings
DB_PATH = os.path.join(DATA_DIR, "logitrack.db")

# Optimization parameters
OPTIMIZATION_PARAMS = {
    "MAX_SOLVER_TIME": 10,  # maximum time in seconds for solver
    "MIN_UTILIZATION": 0.3,  # minimum warehouse utilization threshold
    "MAX_UTILIZATION": 0.9,  # maximum warehouse utilization threshold
}

# Visualization settings
VIS_SETTINGS = {
    "MAP_CENTER": [39.8283, -98.5795],  # USA center coordinates
    "MAP_ZOOM": 4,
    "COLORS": {
        "primary": "#1f77b4",
        "secondary": "#ff7f0e",
        "success": "#2ca02c",
        "warning": "#d62728",
    }
}