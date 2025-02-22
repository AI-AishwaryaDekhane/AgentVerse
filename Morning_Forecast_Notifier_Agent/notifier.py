from uagents import Agent, Context, Model
import requests
import os

class Message(Model):
    message: str

my_first_agent = Agent(
    name='My First Agent',
    port=4040,
    endpoint=['http://localhost:4040/submit'],
    seed='chorot 3 seed phrase'
)

def get_weather(api_key, city="Ann Arbor"):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data["cod"] != 200:
            return f"Error: {data['message']}"

        location = data["name"]
        weather = data["weather"][0]["description"]
        temperature = data["main"]["temp"]

        return f"Location: {location}\nWeather: {weather}\nTemperature: {temperature}°C"
    except Exception as e:
        return f"An error occurred: {e}"

def display_notification(message):
    os.system(f"""
              osascript -e 'display notification "{message}" with title "Morning Weather Forecast"'
              """)

@my_first_agent.on_event('startup')
async def startup_handler(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')
    
    api_key = 'your_key'  # Replace with the obtained API key
    #get your api keys here: [https://home.openweathermap.org/api_keys]
    weather_info = get_weather(api_key)
    print(f"Weather Info: {weather_info}")
    ctx.logger.info(f"Weather Info: {weather_info}")

    display_notification(weather_info)

if __name__ == "__main__":
    my_first_agent.run()