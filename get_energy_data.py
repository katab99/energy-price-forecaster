import os
from dotenv import load_dotenv
from entsoe.entsoe import EntsoePandasClient
import pandas as pd

load_dotenv()

client = EntsoePandasClient(api_key=f"{os.getenv("ENTSOE_KEY")}")
start = pd.Timestamp("20260423", tz="Europe/Berlin")
end = pd.Timestamp("20260424", tz="Europe/Berlin")

country_code = "DK1"

prices = client.query_day_ahead_prices(country_code=country_code, start=start, end=end)
load = client.query_load(country_code=country_code, start=start, end=end)
print(prices)
print(load)
