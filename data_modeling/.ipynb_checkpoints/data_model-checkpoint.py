import os
from dotenv import load_dotenv
load_dotenv()
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from pylab import rcParams
import glob
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')
from pylab import rcParams
rcParams['figure.figsize'] = 10, 6
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima_model import ARIMA
from pmdarima.arima import auto_arima
import alpaca_trade_api as tradeapi
from sklearn.metrics import mean_squared_error, mean_absolute_error
import math
import requests

class data_model:
    
    
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.api = tradeapi.REST(
            api_key,
            secret_key,
            api_version = "v2"
        )
    
    def create_dataset(ticker):
        timeframe = "1D"
        max_iter=1000
        barset = api.get_barset(
            ticker,
            timeframe,
            limit=max_iter
        ).df
        return barset
    def stock_close(barset):
        close_df = barset['close']
        return close_df
        


    #Test for staionarity
    def test_stationarity(close_df):
    #Determing rolling statistics
        rolmean = close_df.rolling(12).mean()
        rolstd = close_df.rolling(12).std()
        print("Results of dickey fuller test")
        adft = adfuller(close_df,autolag='AIC')
        # output for dft will give us without defining what the values are.
        #hence we manually write what values does it explains using a for loop
        output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
        for key,values in adft[4].items():
            output['critical value (%s)'%key] =  values
        p_value = adft[1]
        return p_value
        
        def p_value_test(p_value):
            if p_value < .05:
                train_data, test_data = df_log[3:int(len(df_log)*0.9)], df_log[int(len(df_log)*0.9):]
                
                model_autoARIMA = auto_arima(train_data, start_p=0, start_q=0, test='adf', max_p=3, max_q=3, m=1, d=None, seasonal=False, start_P=0, D=0, trace=True, error_action='ignore', suppress_warnings=True, stepwise=True)
                
                model = ARIMA(train_data, order=(model_autoARIMA.order[0], model_autoARIMA.order[1], model_autoARIMA.order[2]))  
                fitted = model.fit(disp=-1)
                       
                #forecast
                fc, se, conf = fitted.forecast(100, alpha=0.05)  # 95% confidence
                fc_series = pd.Series(fc, index=test_data.index)
      
                mape = np.mean(np.abs(fc - test_data)/np.abs(test_data))
            else:
                result = seasonal_decompose(stock_close, model='multiplicative', freq = 30)
                rcParams['figure.figsize'] = 10, 6
                df_log = np.log(stock_close)
                
                train_data, test_data = df_log[3:int(len(df_log)*0.9)], df_log[int(len(df_log)*0.9):]
                
                model_autoARIMA = auto_arima(train_data, start_p=0, start_q=0, test='adf', max_p=3, max_q=3, m=1, d=None, seasonal=False, start_P=0, D=0, trace=True, error_action='ignore', suppress_warnings=True, stepwise=True)
                
                model = ARIMA(train_data, order=(model_autoARIMA.order[0], model_autoARIMA.order[1], model_autoARIMA.order[2]))  
                fitted = model.fit(disp=-1)

                #forecast
                fc, se, conf = fitted.forecast(100, alpha=0.05)  # 95% confidence
                fc_series = pd.Series(fc, index=test_data.index)
                mape = np.mean(np.abs(fc - test_data)/np.abs(test_data))
            return mape, fc_series

        def up_or_down(fc_series):
            if fc_series[-1] > fc_series[0]:
                up = 'This stock is forecasted going up based on the last 1000 trading days'
                return up
            else:
                down = 'This stock is forecasted going down based on the last 1000 trading days'
                return down

                       
                      
                
