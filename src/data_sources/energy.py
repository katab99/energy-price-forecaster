import os

import pandas as pd
from dotenv import load_dotenv
from entsoe.entsoe import EntsoePandasClient

load_dotenv()


def get_entsoe_data(
    country_code: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    client = EntsoePandasClient(api_key=f"{os.getenv('ENTSOE_KEY')}")

    prices = client.query_day_ahead_prices(
        country_code=country_code, start=start, end=end
    )
    load = client.query_load(country_code=country_code, start=start, end=end)

    df = pd.merge(
        prices.rename("price_eur_mwh"),
        load.rename(columns={"Actual Load": "load_mw"}),
        left_index=True,
        right_index=True,
    )

    df.index = df.index.tz_convert("UTC")

    return df
