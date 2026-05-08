import pandas as pd

from data_sources.energy import get_entsoe_data
from data_sources.weather import get_weather_data


def fetch_pipeline(start, end, country_code, timezone, url, params) -> None:
    # Single location in request and response for now
    df_weather = get_weather_data(url, params, "hourly")[0]
    df_weather.to_parquet("data/raw/weather.parquet")
    print("Weather data fetched and saved to data/raw/weather.parquet")

    start_date = pd.Timestamp(start, tz=timezone)
    end_date = pd.Timestamp(end, tz=timezone)

    assert isinstance(start_date, pd.Timestamp)
    assert isinstance(end_date, pd.Timestamp)

    df_energy = get_entsoe_data(country_code, start_date, end_date)
    df_energy.to_parquet("data/raw/entsoe.parquet")
    print("Energy data fetched and saved to data/raw/entsoe.parquet")

    df = df_energy.merge(df_weather, left_index=True, right_index=True)
    df.to_parquet("data/raw/merged.parquet")
    print("Merged data saved to data/raw/merged.parquet")


if __name__ == "__main__":
    start = "2022-01-01"
    end = "2026-05-01"
    timezone = "Europe/Copenhagen"
    country_code = "DK_1"

    url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

    lat = -56.0
    lon = 9.5

    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "hourly": [
            "temperature_2m",
            "wind_speed_100m",
            "direct_radiation",
            "diffuse_radiation",
            "cloud_cover",
            "relative_humidity_2m",
        ],
    }

    fetch_pipeline(start, end, country_code, timezone, url, params)
