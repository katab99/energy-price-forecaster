import openmeteo_requests
import pandas as pd
from openmeteo_sdk.Variable import Variable


openmeteo = openmeteo_requests.Client()

# historical forecast
url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

params = {
    "latitude": -49.33310728230237,
    "longitude": -72.88448040260131,
    "start_date": "2026-04-24",
    "end_date": "2026-04-25",
    "hourly": [
        "temperature_2m",  # Biggest driver of heating/cooling demand
        "wind_speed_100m",  # Better for turbine-height generation
        "direct_radiation",  # Solar generation proxy
        "diffuse_radiation",
        "cloud_cover",
        "relative_humidity_2m",  # Secondary demand driver
    ],
}

responses = openmeteo.weather_api(url, params=params)


# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()

for i in range(0, hourly.VariablesLength()):
    print(hourly.Variables(i).ValuesAsNumpy())

hourly_variables = list(
    map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength()))
)


def find_hourly_variable(hourly_variables, variable, altitude):
    try:
        return next(
            v
            for v in hourly_variables
            if v.Variable() == variable and v.Altitude() == altitude
        )
    except StopIteration:
        available = ", ".join(
            f"{v.Variable()}@{v.Altitude()}" for v in hourly_variables
        )
        raise ValueError(
            f"No hourly variable found for {variable}@{altitude}. "
            f"Available hourly variables: {available}"
        )


hourly_temperature_2m = find_hourly_variable(hourly_variables, Variable.temperature, 2)
hourly_wind_speed_100m = find_hourly_variable(
    hourly_variables, Variable.wind_speed, 100
)

# hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
# wind_speed_10m = hourly.Variables().ValuesAsNumpy()

hourly_data = {
    "date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left",
    )
}

hourly_data["temperature_2m"] = hourly_temperature_2m.ValuesAsNumpy()
hourly_data["wind_speed_100m"] = hourly_wind_speed_100m.ValuesAsNumpy()

hourly_dataframe = pd.DataFrame(data=hourly_data)
print("\nHourly data\n", hourly_dataframe)
