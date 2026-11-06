"""
Lab 7 Module 1: Weather Tool Integration (Open-Meteo)
モジュール 1：外部気象ツール連携
"""
import json
import urllib.parse
import urllib.request
from typing import Any, Dict

USER_AGENT = "IPU-IntelligentSystems-2026/1.0"
TIMEOUT_S = 10
ATTRIBUTION = "Weather data by Open-Meteo.com (CC BY 4.0)"

# WMO weather interpretation codes used by Open-Meteo (provided)
WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Depositing rime fog",
    51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
    56: "Light freezing drizzle", 57: "Dense freezing drizzle",
    61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
    66: "Light freezing rain", 67: "Heavy freezing rain",
    71: "Slight snowfall", 73: "Moderate snowfall", 75: "Heavy snowfall", 77: "Snow grains",
    80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
    85: "Slight snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail",
}


def describe_weather_code(code: Any) -> str:
    """Provided: turn a WMO code into text ("Unknown" for anything unexpected)."""
    return WEATHER_CODES.get(code, "Unknown") if isinstance(code, int) else "Unknown"


def _get_json(url: str) -> Dict[str, Any]:
    """Provided: HTTP GET returning parsed JSON. Tests replace this function with a fake,
    so always call the APIs through _get_json (never urllib directly)."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_weather(city_name: str) -> Dict[str, Any]:
    """
    Geocode `city_name` and return current weather from Open-Meteo (no API key needed).
    Raises ValueError for empty input; returns {"found": False, "error": ...} for
    unknown cities, network failures and malformed responses (never raises for those).
    """
    clean_city = (city_name or "").strip()
    if not clean_city:
        raise ValueError("City name cannot be empty.")
    if len(clean_city) > 100:
        raise ValueError("City name is too long (max 100 characters).")

    # TODO [Task 1.1]: Geocode the city name with the Open-Meteo geocoding API
    # 1. Build the URL with urllib.parse.urlencode (name, count=1, language="en", format="json")
    #    for https://geocoding-api.open-meteo.com/v1/search and call _get_json(url).
    # 2. Network error            -> return {"found": False, "error": "Geocoding request failed: ..."}
    # 3. No results               -> return {"found": False, "error": f"City '{clean_city}' not found."}
    # 4. Missing latitude/longitude -> return {"found": False, "error": ...}
    # --- STUDENT IMPLEMENTATION START ---
    raise NotImplementedError("TODO: implement this block")
    # --- STUDENT IMPLEMENTATION END ---

    # TODO [Task 1.2]: Fetch current conditions from https://api.open-meteo.com/v1/forecast
    # 1. Parameters: latitude, longitude, current="temperature_2m,relative_humidity_2m,weather_code",
    #    timezone="auto". Call _get_json(url).
    # 2. Network error, or no "temperature_2m" in "current" -> return {"found": False, "error": ...}
    # 3. Return: found, city, country, latitude, longitude, observed_at, temperature_c,
    #    humidity_pct, weather_code, conditions (use describe_weather_code), attribution (ATTRIBUTION)
    # --- STUDENT IMPLEMENTATION START ---
    raise NotImplementedError("TODO: implement this block")
    # --- STUDENT IMPLEMENTATION END ---
