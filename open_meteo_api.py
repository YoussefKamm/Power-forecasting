"""Fetch hourly weather data from the Open-Meteo API and save to CSV.

This script uses only Python's standard library.
"""

from __future__ import annotations

import csv
import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=52.52"
    "&longitude=13.41"
    "&hourly="
    "temperature_2m,wind_speed_10m,precipitation,apparent_temperature,"
    "dew_point_2m,relative_humidity_2m,cloud_cover"
    "&past_days=31"
)

OUTPUT_CSV = "weather_data.csv"


@dataclass
class HourlyWeatherRow:
    time: str
    temperature_2m: Any
    wind_speed_10m: Any
    precipitation: Any
    apparent_temperature: Any
    dew_point_2m: Any
    relative_humidity_2m: Any
    cloud_cover: Any

    def as_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "temperature_2m": self.temperature_2m,
            "wind_speed_10m": self.wind_speed_10m,
            "precipitation": self.precipitation,
            "apparent_temperature": self.apparent_temperature,
            "dew_point_2m": self.dew_point_2m,
            "relative_humidity_2m": self.relative_humidity_2m,
            "cloud_cover": self.cloud_cover,
        }


def fetch_weather_data(url: str = API_URL) -> Dict[str, Any]:
    """Fetch JSON data from the Open-Meteo API."""
    try:
        with urlopen(url) as response:
            if response.status != 200:
                raise RuntimeError(f"Unexpected status code {response.status}")
            data_bytes = response.read()
    except HTTPError as exc:
        raise RuntimeError(f"HTTP error while fetching data: {exc.code} {exc.reason}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error while fetching data: {exc.reason}") from exc
    except Exception as exc:  # pragma: no cover - safeguard
        raise RuntimeError(f"Unexpected error while fetching data: {exc}") from exc

    try:
        payload = json.loads(data_bytes.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to decode JSON response: {exc}") from exc

    return payload


def _extract_hourly_rows(payload: Dict[str, Any]) -> List[HourlyWeatherRow]:
    """Extract structured hourly rows from the API payload."""
    hourly = payload.get("hourly")
    if not isinstance(hourly, dict):
        raise RuntimeError("Response JSON does not contain 'hourly' object.")

    required_keys = [
        "time",
        "temperature_2m",
        "wind_speed_10m",
        "precipitation",
        "apparent_temperature",
        "dew_point_2m",
        "relative_humidity_2m",
        "cloud_cover",
    ]

    for key in required_keys:
        if key not in hourly:
            raise RuntimeError(f"Missing expected hourly field: '{key}'")
        if not isinstance(hourly[key], list):
            raise RuntimeError(f"Hourly field '{key}' is not a list.")

    lengths = {len(hourly[key]) for key in required_keys}
    if len(lengths) != 1:
        raise RuntimeError(f"Inconsistent hourly array lengths: {lengths}")

    count = lengths.pop()
    rows: List[HourlyWeatherRow] = []

    for i in range(count):
        rows.append(
            HourlyWeatherRow(
                time=str(hourly["time"][i]),
                temperature_2m=hourly["temperature_2m"][i],
                wind_speed_10m=hourly["wind_speed_10m"][i],
                precipitation=hourly["precipitation"][i],
                apparent_temperature=hourly["apparent_temperature"][i],
                dew_point_2m=hourly["dew_point_2m"][i],
                relative_humidity_2m=hourly["relative_humidity_2m"][i],
                cloud_cover=hourly["cloud_cover"][i],
            )
        )

    return rows


def save_hourly_data_to_csv(rows: List[HourlyWeatherRow], path: str = OUTPUT_CSV) -> int:
    """Save hourly rows to a CSV file and return the number of rows written."""
    if not rows:
        raise RuntimeError("No hourly data rows to save.")

    fieldnames = [
        "time",
        "temperature_2m",
        "wind_speed_10m",
        "precipitation",
        "apparent_temperature",
        "dew_point_2m",
        "relative_humidity_2m",
        "cloud_cover",
    ]

    with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())

    return len(rows)


def main() -> None:
    try:
        payload = fetch_weather_data()
        rows = _extract_hourly_rows(payload)
        count = save_hourly_data_to_csv(rows)
    except Exception as exc:  # pragma: no cover - top-level error reporting
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Successfully saved {count} hourly rows to {OUTPUT_CSV}.")


if __name__ == "__main__":
    main()

