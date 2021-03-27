from fastapi import FastAPI
from Forecaster import DataModel

app = FastAPI()
dm = DataModel()

@app.get("/")
async def root():
    return {"message": "Hello There"}

@app.get("/forecasts/{ticker_id}")
async def read_forecast(ticker_id):
    # Returns forecase for the specified ticker
    result, mape = dm.get_forecast(ticker_id)
    return {"ticker_id": ticker_id, "forecast": result, "mape": mape}