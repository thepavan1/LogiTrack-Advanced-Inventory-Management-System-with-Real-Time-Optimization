
from typing import Dict, List, Union, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
import json
import csv
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_distance(
    origin: Tuple[float, float],
    destination: Tuple[float, float]
) -> float:
    # Earth's radius in miles
    R = 3959.87433
    
    lat1, lon1 = np.radians(origin)
    lat2, lon2 = np.radians(destination)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c

def validate_data(df: pd.DataFrame, required_columns: List[str]) -> bool:
    try:
        # Check for required columns
        missing_cols = set(required_columns) - set(df.columns)
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return False
            
        # Check for empty values in required columns
        for col in required_columns:
            if df[col].isna().any():
                logger.error(f"Column '{col}' contains empty values")
                return False
                
        return True
        
    except Exception as e:
        logger.error(f"Error validating data: {str(e)}")
        return False

def format_currency(amount: float, currency: str = "USD") -> str:
    try:
        if currency == "USD":
            return f"${amount:,.2f}"
        elif currency == "EUR":
            return f"€{amount:,.2f}"
        elif currency == "GBP":
            return f"£{amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except Exception as e:
        logger.error(f"Error formatting currency: {str(e)}")
        return str(amount)

def parse_date(date_str: str) -> datetime:
    date_formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%m-%d-%Y",
        "%m/%d/%Y",
        "%d-%m-%Y",
        "%d/%m/%Y"
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date string: {date_str}")

def export_results(
    results: Dict,
    output_format: str = "json",
    output_path: Union[str, Path] = None
) -> Union[str, bool]:
    try:
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"optimization_results_{timestamp}.{output_format}"
            
        output_path = Path(output_path)
        
        if output_format == "json":
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=4)
                
        elif output_format == "csv":
            # Flatten nested dictionary for CSV
            flat_results = pd.json_normalize(results)
            flat_results.to_csv(output_path, index=False)
            
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
            
        logger.info(f"Results exported to {output_path}")
        return str(output_path)
        
    except Exception as e:
        logger.error(f"Error exporting results: {str(e)}")
        return False