import os
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

from dotenv import load_dotenv
from mcp.server import MCPServer


# --------------------------------------------------
# 1. LOAD ENVIRONMENT VARIABLES
# --------------------------------------------------

load_dotenv(Path(__file__).resolve().parent / ".env")

API_KEY = os.getenv("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5"


# --------------------------------------------------
# 2. CREATE MCP SERVER
# --------------------------------------------------

mcp = MCPServer("Weather MCP Server")


# --------------------------------------------------
# 3. COMMON API REQUEST FUNCTION
# --------------------------------------------------

def make_api_request(url: str, params: dict) -> dict:
    """Send a request to an API and return JSON data."""

    query_string = urlencode(params)
    full_url = f"{url}?{query_string}"

    with urlopen(full_url, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def validate_api_key():
    """Check whether the API key is configured."""

    if not API_KEY:
        raise ValueError("API key is missing. Check your .env file.")


# --------------------------------------------------
# TOOL 1: CURRENT WEATHER
# --------------------------------------------------

@mcp.tool()
def get_weather(city: str) -> str:
    """Get current temperature, humidity, wind and weather condition."""

    try:
        validate_api_key()

        data = make_api_request(
            f"{BASE_URL}/weather",
            {
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            }
        )

        return (
            f"Current Weather: {data['name']}, "
            f"{data['sys']['country']}\n"
            f"Temperature: {data['main']['temp']}°C\n"
            f"Feels like: {data['main']['feels_like']}°C\n"
            f"Condition: {data['weather'][0]['description']}\n"
            f"Humidity: {data['main']['humidity']}%\n"
            f"Wind speed: {data['wind']['speed']} m/s"
        )

    except HTTPError as error:
        if error.code == 404:
            return f"City '{city}' was not found."
        return f"Weather API error: HTTP {error.code}"

    except (URLError, TimeoutError):
        return "Unable to connect to the weather service."

    except (ValueError, KeyError, TypeError) as error:
        return f"Error: {error}"


# --------------------------------------------------
# TOOL 2: FIVE-DAY WEATHER FORECAST
# --------------------------------------------------

@mcp.tool()
def get_weather_forecast(city: str) -> str:
    """Get a five-day weather forecast with rain probability."""

    try:
        validate_api_key()

        data = make_api_request(
            f"{BASE_URL}/forecast",
            {
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            }
        )

        forecast_results = []

        for item in data["list"]:
            forecast_time = item["dt_txt"]
            temperature = item["main"]["temp"]
            condition = item["weather"][0]["description"]
            rain_probability = round(item["pop"] * 100)

            forecast_results.append(
                f"Time (UTC): {forecast_time}\n"
                f"Temperature: {temperature}°C\n"
                f"Condition: {condition}\n"
                f"Rain probability: {rain_probability}%"
            )

        return (
            f"Five-Day Forecast for {data['city']['name']}\n\n"
            + "\n\n".join(forecast_results)
        )

    except HTTPError as error:
        if error.code == 404:
            return f"City '{city}' was not found."
        return f"Forecast API error: HTTP {error.code}"

    except (URLError, TimeoutError):
        return "Unable to connect to the forecast service."

    except (ValueError, KeyError, TypeError) as error:
        return f"Error: {error}"


# --------------------------------------------------
# 4. START MCP SERVER
# --------------------------------------------------

if __name__ == "__main__":
    mcp.run()
