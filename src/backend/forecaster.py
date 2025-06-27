import pandas as pd
from prophet import Prophet
from typing import Dict, Optional, List
import logging
from datetime import datetime, timedelta
# No relative imports needed here

class DemandForecaster:
    def __init__(self, seasonality_mode: str = 'multiplicative'):
        """
        Initialize the demand forecaster.
        
        Args:
            seasonality_mode (str): Seasonality mode for Prophet ('multiplicative' or 'additive')
        """
        self.model = Prophet(
            seasonality_mode=seasonality_mode,
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        self.is_fitted = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def prepare_data(self, 
                    sales_data: pd.DataFrame, 
                    date_column: str = 'date',
                    value_column: str = 'quantity') -> pd.DataFrame:
        """
        Prepare data for Prophet forecasting.
        
        Args:
            sales_data (pd.DataFrame): Historical sales data
            date_column (str): Name of the date column
            value_column (str): Name of the value column to forecast
            
        Returns:
            pd.DataFrame: Prepared data in Prophet format (ds, y)
        """
        # Prophet requires columns named 'ds' and 'y'
        prophet_data = sales_data.copy()
        prophet_data['ds'] = pd.to_datetime(prophet_data[date_column])
        prophet_data['y'] = prophet_data[value_column]
        
        return prophet_data[['ds', 'y']]

    def fit(self, 
            sales_data: pd.DataFrame, 
            date_column: str = 'date',
            value_column: str = 'quantity') -> None:
        """
        Fit the Prophet model to historical sales data.
        
        Args:
            sales_data (pd.DataFrame): Historical sales data
            date_column (str): Name of the date column
            value_column (str): Name of the value column to forecast
        """
        try:
            prophet_data = self.prepare_data(sales_data, date_column, value_column)
            self.model.fit(prophet_data)
            self.is_fitted = True
            self.logger.info("Model successfully fitted to the data")
        except Exception as e:
            self.logger.error(f"Error fitting model: {str(e)}")
            raise

    def forecast(self, 
                periods: int = 90, 
                freq: str = 'D', 
                return_components: bool = False) -> Dict:
        """
        Generate demand forecast for specified period.
        
        Args:
            periods (int): Number of periods to forecast
            freq (str): Frequency of forecast ('D' for daily, 'W' for weekly, 'M' for monthly)
            return_components (bool): Whether to return seasonal components
            
        Returns:
            Dict: Forecast results including:
                - forecast: DataFrame with forecast
                - components: Seasonal components if requested
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before forecasting")

        try:
            # Create future dataframe
            future = self.model.make_future_dataframe(
                periods=periods,
                freq=freq
            )
            
            # Generate forecast
            forecast = self.model.predict(future)
            
            result = {
                'forecast': forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']],
                'components': self.model.plot_components(forecast) if return_components else None
            }
            
            self.logger.info(f"Generated forecast for {periods} periods")
            return result
        
        except Exception as e:
            self.logger.error(f"Error generating forecast: {str(e)}")
            raise

    def get_seasonal_patterns(self) -> Dict:
        """
        Extract seasonal patterns from the fitted model.
        
        Returns:
            Dict: Seasonal patterns including:
                - yearly
                - weekly
                - holidays (if configured)
        """
        if not self.is_fitted:
            raise ValueError("Model must be fitted before extracting patterns")

        patterns = {}
        
        # Extract yearly seasonality
        if self.model.yearly_seasonality:
            yearly = pd.DataFrame(
                self.model.seasonalities['yearly'],
                columns=['ds', 'yearly']
            )
            patterns['yearly'] = yearly
            
        # Extract weekly seasonality
        if self.model.weekly_seasonality:
            weekly = pd.DataFrame(
                self.model.seasonalities['weekly'],
                columns=['ds', 'weekly']
            )
            patterns['weekly'] = weekly
            
        return patterns

    def evaluate_forecast(self, 
                         actual_data: pd.DataFrame, 
                         forecast_data: pd.DataFrame) -> Dict:
        """
        Evaluate forecast accuracy using multiple metrics.
        
        Args:
            actual_data (pd.DataFrame): Actual historical data
            forecast_data (pd.DataFrame): Forecasted data
            
        Returns:
            Dict: Evaluation metrics including:
                - MAPE (Mean Absolute Percentage Error)
                - MAE (Mean Absolute Error)
                - RMSE (Root Mean Square Error)
        """
        from sklearn.metrics import mean_absolute_error, mean_squared_error
        import numpy as np
        
        # Merge actual and forecast data
        evaluation_df = actual_data.merge(
            forecast_data[['ds', 'yhat']],
            on='ds',
            how='inner'
        )
        
        # Calculate metrics
        mape = np.mean(np.abs((evaluation_df['y'] - evaluation_df['yhat']) / evaluation_df['y'])) * 100
        mae = mean_absolute_error(evaluation_df['y'], evaluation_df['yhat'])
        rmse = np.sqrt(mean_squared_error(evaluation_df['y'], evaluation_df['yhat']))
        
        return {
            'mape': mape,
            'mae': mae,
            'rmse': rmse
        }