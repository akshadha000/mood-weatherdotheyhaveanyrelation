import pandas as pd
import requests

# ==============================
# STEP 1: LOAD CLEANED DATA
# ==============================

df = pd.read_csv("cleaned_mood_data.csv")

print("Loaded dataset:", df.shape)

# ==============================
# STEP 2: DEFINE CITIES
# ==============================

cities = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
    "Hyderabad", "Pune", "Ahmedabad", "Jaipur", "Lucknow"
]

# ==============================
# STEP 3: API KEY
# ==============================


api key =4cc0b77fa86080351722000fb1f13aa6
# ==============================
# STEP 4: FETCH WEATHER
# ==============================

weather_cache = {}

for city in cities:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    response = requests.get(url).json()

    if response.get("cod") != 200:
        print(f"❌ Error for {city}")
        continue

    weather_cache[city] = {
        "temp": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "weather": response["weather"][0]["main"]
    }

# ==============================
# STEP 5: MAP WEATHER
# ==============================

df["temp"] = df["city"].map(lambda x: weather_cache.get(x, {}).get("temp"))
df["humidity"] = df["city"].map(lambda x: weather_cache.get(x, {}).get("humidity"))
df["weather"] = df["city"].map(lambda x: weather_cache.get(x, {}).get("weather"))

# ==============================
# STEP 6: SAVE FINAL DATA
# ==============================

df.to_csv("final_mood_weather_data.csv", index=False)

print("✅ Final dataset saved!")