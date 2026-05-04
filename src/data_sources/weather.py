import openmeteo_requests
import pandas as pd
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from typing_extensions import List

VariableSpec = List[str]


def extract_response(response: WeatherApiResponse, specs: VariableSpec) -> pd.DataFrame:
    hourly = response.Hourly()
    assert hourly is not None

    hourly_data = {
        key: var.ValuesAsNumpy()
        for i, key in enumerate(specs)
        if (var := hourly.Variables(i)) is not None
    }

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

    return hourly_dataframe


def get_weather_data(url, params: dict, attribute: str) -> list:
    openmeteo = openmeteo_requests.Client()
    responses = openmeteo.weather_api(url, params=params)

    # is this an attribute? maybe I should give a better name
    specs = params[attribute]
    return [extract_response(response, specs) for response in responses]
