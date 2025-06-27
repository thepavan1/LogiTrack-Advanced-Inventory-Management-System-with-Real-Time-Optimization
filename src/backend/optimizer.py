import logging
import time
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class InventoryOptimizer:
    def __init__(self):
        """Initialize the optimizer with default parameters"""
        self.logger = logging.getLogger(__name__)
        self.solver_time = 20  # Default solver time limit in seconds
        self.current_datetime = "2025-03-24 21:07:26"  # Updated timestamp
        self.current_user = "tanishpoddar"

    def calculate_distance(self, warehouse_row: pd.Series, order_row: pd.Series) -> float:
        """Calculate distance between warehouse and delivery location using Haversine formula"""
        try:
            # Extract coordinates
            lat1, lon1 = warehouse_row['latitude'], warehouse_row['longitude']
            lat2, lon2 = order_row['delivery_latitude'], order_row['delivery_longitude']
            
            # Convert to radians
            lat1, lon1 = map(radians, [float(lat1), float(lon1)])
            lat2, lon2 = map(radians, [float(lat2), float(lon2)])
            
            # Haversine formula
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            r = 6371  # Earth's radius in kilometers
            
            return c * r
        except Exception as e:
            self.logger.error(f"Error calculating distance: {str(e)}")
            return float('inf')

    def optimize(self, warehouses: pd.DataFrame, orders: pd.DataFrame) -> Dict[str, Any]:
        """Optimize inventory distribution"""
        try:
            optimization_start_time = time.time()
            
            # Initialize results dictionary
            results = {
                'allocation_plan': {},
                'warehouse_utilization': {},
                'unfulfilled_orders': [],
                'total_cost': 0,
                'solving_time': 0,
                'status': 'In Progress',
                'optimization_timestamp': self.current_datetime,
                'optimization_user': self.current_user
            }

            # Create a copy of warehouses to track inventory changes
            warehouse_inventory = warehouses.copy()
            
            # Sort orders by priority (urgent first) and size
            orders = orders.sort_values(
                by=['status', 'quantity'], 
                ascending=[True, False]
            )

            # Process each order
            for _, order in orders.iterrows():
                best_allocation = {
                    'warehouse_id': None,
                    'cost': float('inf'),
                    'distance': float('inf')
                }

                # Find best warehouse for this order
                for _, warehouse in warehouse_inventory.iterrows():
                    if warehouse['current_stock'] >= order['quantity']:
                        # Calculate transportation cost based on distance
                        distance = self.calculate_distance(warehouse, order)
                        cost = distance * 10  # Base cost per km
                        
                        # Add storage cost factor
                        cost += warehouse['storage_cost'] * order['quantity'] * 0.01
                        
                        if cost < best_allocation['cost']:
                            best_allocation.update({
                                'warehouse_id': warehouse['warehouse_id'],
                                'cost': cost,
                                'distance': distance
                            })

                # Allocate order if possible
                if best_allocation['warehouse_id'] is not None:
                    warehouse_id = best_allocation['warehouse_id']
                    
                    # Initialize warehouse in allocation plan if not exists
                    if warehouse_id not in results['allocation_plan']:
                        results['allocation_plan'][warehouse_id] = []
                    
                    # Add allocation
                    results['allocation_plan'][warehouse_id].append({
                        'order_id': order['order_id'],
                        'quantity': order['quantity'],
                        'cost': best_allocation['cost'],
                        'distance': best_allocation['distance']
                    })
                    
                    # Update warehouse inventory
                    mask = warehouse_inventory['warehouse_id'] == warehouse_id
                    warehouse_inventory.loc[mask, 'current_stock'] -= order['quantity']
                    
                    # Update warehouse utilization
                    warehouse_row = warehouses[warehouses['warehouse_id'] == warehouse_id].iloc[0]
                    results['warehouse_utilization'][warehouse_id] = {
                        'warehouse_name': warehouse_row['name'],
                        'initial_stock': warehouse_row['current_stock'],
                        'used_capacity': order['quantity'],
                        'remaining_stock': warehouse_inventory.loc[mask, 'current_stock'].iloc[0],
                        'total_capacity': warehouse_row['capacity'],
                        'utilization_percentage': (
                            (warehouse_row['current_stock'] - order['quantity']) / 
                            warehouse_row['capacity'] * 100
                        )
                    }
                    
                    # Update total cost
                    results['total_cost'] += best_allocation['cost']
                else:
                    # Add to unfulfilled orders
                    results['unfulfilled_orders'].append({
                        'order_id': order['order_id'],
                        'quantity': order['quantity'],
                        'reason': 'Insufficient stock across all warehouses'
                    })

            # Calculate solving time and update status
            results['solving_time'] = time.time() - optimization_start_time
            results['status'] = 'Completed'
            
            # Add performance metrics
            results['performance_metrics'] = {
                'total_orders': len(orders),
                'fulfilled_orders': len(orders) - len(results['unfulfilled_orders']),
                'fulfillment_rate': (
                    (len(orders) - len(results['unfulfilled_orders'])) / 
                    len(orders) * 100
                ),
                'average_cost_per_order': (
                    results['total_cost'] / 
                    (len(orders) - len(results['unfulfilled_orders']))
                    if (len(orders) - len(results['unfulfilled_orders'])) > 0 
                    else 0
                )
            }

            return results

        except Exception as e:
            self.logger.error(f"Optimization error: {str(e)}")
            raise ValueError(f"Optimization error: {str(e)}")

    def get_optimization_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of optimization results"""
        try:
            return {
                'total_cost': round(results['total_cost'], 2),
                'total_orders': results['performance_metrics']['total_orders'],
                'fulfilled_orders': results['performance_metrics']['fulfilled_orders'],
                'fulfillment_rate': round(results['performance_metrics']['fulfillment_rate'], 1),
                'average_cost_per_order': round(results['performance_metrics']['average_cost_per_order'], 2),
                'solving_time': round(results['solving_time'], 2),
                'status': results['status'],
                'timestamp': results['optimization_timestamp']
            }
        except Exception as e:
            self.logger.error(f"Error generating optimization summary: {str(e)}")
            return {}