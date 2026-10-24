import os
import requests
import logging
from dotenv import load_dotenv
from livekit.agents import function_tool

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def detect_city_by_ip():
    try:
        ip_info = requests.get("https://ipapi.co/json/").json()
        city = ip_info.get("city")
        return city if city else "Delhi"
    except:
        return "Delhi"


@function_tool
async def weather_tool(city: str = "") -> str:
    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "❌ Weather API key missing."

    if not city or city.strip() == "":
        city = detect_city_by_ip()

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return f"❌ Weather error: {response.status_code}"

        data = response.json()
        desc = data["weather"][0]["description"].title()
        temp = data["main"]["temp"]
        hum = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        return (
            f"🌤 Weather in {city}:\n"
            f"• Condition: {desc}\n"
            f"• Temperature: {temp}°C\n"
            f"• Humidity: {hum}%\n"
            f"• Wind Speed: {wind} m/s"
        )

    except Exception as e:
        return f"❌ Error fetching weather: {e}"
