import pandas as pd
import math
from geopy.distance import geodesic
from thefuzz import process
import folium
import json
import random
df = pd.read_csv(r"C:\Users\KIIT\Desktop\Projects\Globle Clone\country-capital-lat-long-population.csv")
df['Country'] = df['Country'].str.strip()
df['Capital City'] = df['Capital City'].str.strip()

borders_df = pd.read_csv(r"C:\Users\KIIT\Desktop\Projects\Globle Clone\GEODATASOURCE-COUNTRY-BORDERS (1).CSV")
borders_df.dropna(subset=['country_name', 'country_border_name'], inplace=True)
borders_df['country_name'] = borders_df['country_name'].astype(str).str.strip()
borders_df['country_border_name'] = borders_df['country_border_name'].astype(str).str.strip()

def correct_name(name, name_list):
    match = process.extractOne(name.strip(), name_list)
    if match and match[1] >= 70:
        return match[0]
    return None
adjacency_map = {}
for _, row in borders_df.iterrows():
    c1 = correct_name(row['country_name'], df['Country'])
    c2 = correct_name(row['country_border_name'], df['Country'])
    if not c1 or not c2:
        continue
    adjacency_map.setdefault(c1, set()).add(c2)
    adjacency_map.setdefault(c2, set()).add(c1)
with open("countries.geojson", "r", encoding="utf-8") as f:
    geojson_data = json.load(f)
world_map = folium.Map(location=[20, 0], zoom_start=2)
def direction_arrow(bearing):
    directions = [
        (22.5, "⬆️"), (67.5, "↗️"), (112.5, "➡️"), (157.5, "↘️"),
        (202.5, "⬇️"), (247.5, "↙️"), (292.5, "⬅️"), (337.5, "↖️"), (360, "⬆️")
    ]
    for angle, symbol in directions:
        if bearing <= angle:
            return symbol
    return "❓"
def compute_distance_direction(from_row, to_row):
    coord1 = (from_row['Latitude'], from_row['Longitude'])
    coord2 = (to_row['Latitude'], to_row['Longitude'])
    distance = geodesic(coord1, coord2).km

    d_lon = math.radians(coord2[1] - coord1[1])
    lat1 = math.radians(coord1[0])
    lat2 = math.radians(coord2[0])

    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(d_lon)
    bearing = (math.degrees(math.atan2(x, y)) + 360) % 360
    return distance, direction_arrow(bearing)
def highlight_country(country_name, color="blue"):
    folium.GeoJson(
        geojson_data,
        name=country_name,
        style_function=lambda feat: {
            'fillColor': color if feat['properties'].get('ADMIN', '') == country_name else 'transparent',
            'color': 'black' if feat['properties'].get('ADMIN', '') == country_name else 'transparent',
            'weight': 1,
            'fillOpacity': 0.5 if feat['properties'].get('ADMIN', '') == country_name else 0
        },
        tooltip=country_name
    ).add_to(world_map)
def mode_country_guess():
    mystery = df.sample(1).iloc[0]
    mystery_country = mystery['Country']
    attempts = 0
    guessed = set()

    print("\n🎯 Guess the mystery country!")
    print("🆘 Type 'escape' to give up.\n")

    while True:
        user = input("🌍 Your guess: ").strip()
        if user.lower() == "escape":
            print(f"\n🏳️ You gave up! Your last guess was: {user}. The country was: {mystery_country}")
            highlight_country(mystery_country, color="red")
            break

        guess = correct_name(user, df['Country'])
        if not guess or guess in guessed:
            print("❌ Invalid or repeated guess.\n")
            continue

        guessed.add(guess)
        row = df[df['Country'] == guess].iloc[0]
        attempts += 1

        if guess == mystery_country:
            print(f"\n✅ Correct! It was {mystery_country}. Attempts: {attempts}")
            highlight_country(guess, color="green")
            break

        distance, arrow = compute_distance_direction(row, mystery)
        if guess in adjacency_map.get(mystery_country, set()):
            print(f"🧭 {guess} is adjacent! Move {arrow} to reach the mystery country.\n")
        elif distance > 9000:
            print(f"📉 Too far!\n")
        else:
            print(f"🧭 Move {arrow} for {distance:.2f} km from {guess}\n")
        highlight_country(guess, color="orange")

    folium.LayerControl().add_to(world_map)
    world_map.save("game_map.html")
    webbrowser.open("game_map.html")
def mode_capital_guess():
    mystery = df.sample(1).iloc[0]
    mystery_country = mystery['Country']
    mystery_capital = mystery['Capital City']
    attempts = 0
    guessed = set()

    print("\n🎯 Guess the capital of a mystery country!")
    print("🆘 Type 'escape' to give up.\n")

    while True:
        user = input("🏙️ Your capital guess: ").strip()
        if user.lower() == "escape":
            print(f"\n🏳️ You gave up! Your last guess was: {user}. The country was: {mystery_country} and capital is {mystery_capital}")
            highlight_country(mystery_country, color="red")
            break

        guess = correct_name(user, df['Capital City'])
        if not guess or guess in guessed:
            print("❌ Invalid or repeated guess.\n")
            continue

        guessed.add(guess)
        guessed_country = df[df['Capital City'] == guess].iloc[0]
        guessed_country_name = guessed_country['Country']
        attempts += 1

        if guess == mystery_capital:
            print(f"\n✅ Correct! The capital was {mystery_capital}. Attempts: {attempts}")
            highlight_country(mystery_country, color="green")
            break

        distance, arrow = compute_distance_direction(guessed_country, mystery)
        if guessed_country_name in adjacency_map.get(mystery_country, set()):
            print(f"🧭 {guess} ({guessed_country_name}) is adjacent to the mystery capital's country.\n")
        elif distance > 9000:
            print(f"📉 Too far from {guess} ({guessed_country_name})!\n")
        else:
            print(f"🧭 From {guess} ({guessed_country_name}), move {arrow} for {distance:.2f} km\n")
        highlight_country(guessed_country_name, color="orange")

    folium.LayerControl().add_to(world_map)
    world_map.save("game_map.html")
    webbrowser.open("game_map.html")
def mode_border_blitz():
    candidates = [
        c for c in adjacency_map
        if len(adjacency_map.get(c, [])) > 0 and c in df['Country'].values
    ]

    if not candidates:
        print("⚠️ No valid countries with neighbors found.")
        return

    selected = random.choice(candidates)
    neighbors = set(adjacency_map[selected])
    guessed = set()

    print(f"\n🌐 Border Blitz Mode! The selected country is: {selected}")
    print(f"🔲 It has {len(neighbors)} neighboring countries. Can you name them?")
    print("🆘 Type 'escape' to give up.\n")

    while guessed != neighbors:
        user = input("✏️ Your guess: ").strip()
        if user.lower() == "escape":
            break

        guess = correct_name(user, df['Country'])
        if not guess:
            print("❌ Invalid guess.\n")
        elif guess in guessed:
            print("⚠️ Already guessed.\n")
        elif guess in neighbors:
            print(f"✅ Correct! {guess} is a neighbor of {selected}.")
            guessed.add(guess)
        else:
            print(f"❌ {guess} is not a neighbor of {selected}.\n")

    print(f"\n📍 All correct neighbors of {selected}:")
    for n in sorted(neighbors):
        print(f" - {n}")
def main():
    print("\n🌍Welcome to GeoChallenge!")
    print("1️⃣ Mode 1: Guess the country")
    print("2️⃣ Mode 2: Guess the capital")
    print("3️⃣ Mode 3: Border Blitz (guess all neighbors)\n")

    choice = input("🔢 Select a mode (1/2/3): ").strip()
    if choice == '1':
        mode_country_guess()
    elif choice == '2':
        mode_capital_guess()
    elif choice == '3':
        mode_border_blitz()
    else:
        print("❌ Invalid mode selected.")

if __name__ == "__main__":
    main()
