import pandas as pd

from get_energy_data import get_entsoe_data
from get_weather_data import get_weather_data


def main():
    start = "2022-01-01"
    end = "2026-05-01"

    # Get weather data
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

    df_weather = get_weather_data(url, params, "hourly")

    for item in df_weather:
        print(item)
        item.to_parquet("data/raw/weather.parquet")

    # Get energy data
    start_date = pd.Timestamp(start, tz="Europe/Copenhagen")
    end_date = pd.Timestamp(end, tz="Europe/Copenhagen")
    country_code = "DK_1"

    assert isinstance(start_date, pd.Timestamp)
    assert isinstance(end_date, pd.Timestamp)

    df_energy = get_entsoe_data(country_code, start_date, end_date)
    df_energy.to_parquet("data/raw/entsoe.parquet")

    pass


if __name__ == "__main__":
    main()
