import openmeteo_requests
import pandas as pd
from openmeteo_sdk.Variable import Variable


def find_hourly_variable(hourly_variables: list, variable, altitude=0):
    try:
        return next(
            filter(
                lambda v: v.Variable() == variable and v.Altitude() == altitude,
                hourly_variables,
            )
        )
    except StopIteration:
        available = ", ".join(
            f"{v.Variable()}@{v.Altitude()}" for v in hourly_variables
        )
        raise ValueError(
            f"No hourly variable found for {variable}@{altitude}. "
            f"Available hourly variables: {available}"
        )


def extract_hourly_variables(hourly_variables, specs):
    """Extract and validate multiple hourly variables at once."""
    result = {}
    for name, (variable, altitude) in specs.items():
        result[name] = find_hourly_variable(hourly_variables, variable, altitude)

    missing = [name for name, var in result.items() if var is None]
    if missing:
        raise ValueError(f"Missing required hourly variables: {', '.join(missing)}")

    return result


def get_weather_data(url, params: dict):
    openmeteo = openmeteo_requests.Client()
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

    hourly = response.Hourly()

    if hourly is None:
        raise TypeError("Not good")

    hourly_variables = list(
        map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength()))
    )

    HOURLY_VARIABLES_SPEC = {
        "temperature_2m": (Variable.temperature, 2),
        "wind_speed_100m": (Variable.wind_speed, 100),
        "direct_radiation": (Variable.direct_radiation, 0),nw
        "diffuse_radiation": (Variable.diffuse_radiation, 0),
        "cloud_cover": (Variable.cloud_cover, 0),
        "relative_humidity_2m": (Variable.relative_humidity, 2),
    }

    hourly_vars = extract_hourly_variables(hourly_variables, HOURLY_VARIABLES_SPEC)
    hourly_data = {name: var.ValuesAsNumpy() for name, var in hourly_vars.items()}
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe.insert(
        0,
        "date",
        pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left",
        ),
    )

    print("\nHourly data\n", hourly_dataframe)

    # export to parquet file


###

url = "https://historical-forecast-api.open-meteo.com/v1/forecast"

params = {
    "latitude": -56.0,
    "longitude": 9.5,
    "start_date": "2026-04-24",
    "end_date": "2026-04-25",
    "hourly": [
        "temperature_2m",
        "wind_speed_100m",
        "direct_radiation",
        "diffuse_radiation",
        "cloud_cover",
        "relative_humidity_2m",
    ],
}

get_weather_data(url, params)
