import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class WeatherAgent2:

    def __init__(self):
        self.name = "Weather Agent 2"
        self.description = (
            "Retrieves weather information, forecasts, "
            "and provides useful recommendations."
        )

    def give_recommendation(self, weather_text):

        weather = weather_text.lower()

        print("\n========== WEATHER RECOMMENDATIONS ==========")

        if "rain" in weather or "drizzle" in weather:
            print("- Carry an umbrella.")
            print("- Avoid outdoor activities during heavy rain.")

        elif "clear" in weather or "sun" in weather:
            print("- Good weather for outdoor activities.")
            print("- Stay hydrated.")

        elif "cloud" in weather:
            print("- The sky is cloudy.")
            print("- Check the forecast before going out.")

        if "temperature:" in weather:
            try:
                temp_line = next(
                    line for line in weather_text.splitlines()
                    if "temperature:" in line.lower()
                )

                temperature = float(
                    temp_line.split(":")[1]
                    .replace("°C", "")
                    .strip()
                )

                if temperature >= 30:
                    print("- Wear light clothes.")
                    print("- Drink enough water.")

                elif temperature <= 18:
                    print("- Consider carrying a jacket.")

                else:
                    print("- The temperature is moderate.")

            except (ValueError, StopIteration, IndexError):
                print("- Check the temperature before planning your day.")

        print("==============================================")

    async def run(self, city):

        server_params = StdioServerParameters(
            command="python",
            args=[
                "weather-mcp-server/server.py"
            ]
        )

        async with stdio_client(server_params) as (read, write):

            async with ClientSession(read, write) as session:

                await session.initialize()

                # Get current weather
                print(f"\nGetting current weather for {city}...")

                weather_result = await session.call_tool(
                    "get_weather",
                    {"city": city}
                )

                weather_text = "\n".join(
                    item.text
                    for item in weather_result.content
                    if hasattr(item, "text")
                )

                print("\n========== CURRENT WEATHER ==========")
                print(weather_text)

                # Get five-day forecast
                print(f"\nGetting five-day forecast for {city}...")

                forecast_result = await session.call_tool(
                    "get_weather_forecast",
                    {"city": city}
                )

                print("\n========== FIVE-DAY FORECAST ==========")

                for item in forecast_result.content:
                    if hasattr(item, "text"):
                        print(item.text)

                # Give recommendations
                self.give_recommendation(weather_text)


async def main():

    agent = WeatherAgent2()

    print("================================")
    print("       WEATHER AGENT 2")
    print("================================")

    city = input("Enter city name: ").strip()

    if not city:
        print("Please enter a valid city name.")
        return

    await agent.run(city)


if __name__ == "__main__":
    asyncio.run(main())
