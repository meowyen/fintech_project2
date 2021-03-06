import os
import alpaca_trade_api as tradeapi
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pmdarima.arima import auto_arima
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA
import warnings

warnings.filterwarnings("ignore")


class DataModel:

    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ALPACA_API_KEY")
        secret_key = os.getenv("ALPACA_SECRET_KEY")
        self.api = tradeapi.REST(
            api_key,
            secret_key,
            api_version="v2"
        )

    def get_ticker_data(self, ticker):
        timeframe = "1D"
        max_iter = 1000
        barset = self.api.get_barset(
            ticker,
            timeframe,
            limit=max_iter
        ).df

        return barset[ticker]["close"]

    def test_stationarity(self, data):
        """
        Test for stationary data and return p-value.
        """
        adft = adfuller(data, autolag="AIC")
        p_value = adft[1]

        return p_value

    def p_value_test(self, data, p_value):
        data_df = data

        if p_value >= 0.05:
            data_df = np.log(data)

        train_data, test_data = data_df[3:int(
            len(data_df)*0.9)], data_df[int(len(data_df)*0.9):]

        model_autoARIMA = auto_arima(train_data, start_p=0, start_q=0, test='adf', max_p=3, max_q=3, m=1, d=None,
                                     seasonal=False, start_P=0, D=0, trace=True, error_action='ignore', suppress_warnings=True, stepwise=True)

        model = ARIMA(train_data, order=(
            model_autoARIMA.order[0], model_autoARIMA.order[1], model_autoARIMA.order[2]))
        fitted = model.fit(disp=-1)

        # forecast
        fc, se, conf = fitted.forecast(100, alpha=0.05)  # 95% confidence
        fc_series = pd.Series(fc, index=test_data.index)

        mape = np.mean(np.abs(fc - test_data)/np.abs(test_data))

        return mape, fc_series

    def up_or_down(self, fc_series):
        if fc_series[-1] > fc_series[0]:
            return "UP"
        else:
            return "DOWN"

    def get_forecast(self, ticker):
        data_df = self.get_ticker_data(ticker)
        p_value = self.test_stationarity(data_df)
        mape, fc_series = self.p_value_test(data_df, p_value)
        result = self.up_or_down(fc_series)

        return result, mape
