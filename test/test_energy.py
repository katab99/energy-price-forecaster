import os

import pandas as pd
import pytest

from data_sources.energy import get_entsoe_data


@pytest.fixture
def mock_entsoe_client(mocker):
    # Mock the EntsoePandasClient and its methods
    mock_client = mocker.MagicMock()
    mocker.patch("data_sources.energy.EntsoePandasClient", return_value=mock_client)
    return mock_client


def test_get_entsoe_data_success(mock_entsoe_client, mocker):
    mocker.patch.dict(os.environ, {"ENTSOE_KEY": "fake_api_key"})

    start = pd.Timestamp("2023-01-01", tz="Europe/Berlin")
    end = pd.Timestamp("2023-01-02", tz="Europe/Berlin")

    mock_prices_df = pd.Series(
        {"price_eur_mwh": [100, 110]},
        index=pd.date_range(start, periods=2, freq="h", tz="Europe/Berlin"),
    )

    mock_load_df = pd.DataFrame(
        {"Actual Load": [2000, 2100]},
        index=pd.date_range(start, periods=2, freq="h", tz="Europe/Berlin"),
    )

    mock_entsoe_client.query_day_ahead_prices.return_value = mock_prices_df
    mock_entsoe_client.query_load.return_value = mock_load_df

    result = get_entsoe_data("DE", start, end)

    assert isinstance(result, pd.DataFrame)
    assert "price_eur_mwh" in result.columns
    assert "load_mw" in result.columns
    assert str(result.index.tz) == "UTC"
    assert len(result) == 2


def get_entsoe_data_empty(mock_entsoe_client, mocker):
    mocker.patch.dict(os.environ, {"ENTSOE_KEY": "fake_api_key"})

    start = pd.Timestamp("2023-01-01", tz="Europe/Berlin")
    end = pd.Timestamp("2023-01-02", tz="Europe/Berlin")

    # Mock empty DataFrames
    mock_entsoe_client.query_day_ahead_prices.return_value = pd.Series()
    mock_entsoe_client.query_load.return_value = pd.DataFrame()

    result = get_entsoe_data("DE", start, end)

    assert isinstance(result, pd.DataFrame)
    assert result.empty
