🌍 AI Geography Guessing Game
An interactive terminal-based geography guessing game that challenges players to identify countries, capitals, and neighboring nations using distance, direction, and adjacency hints.

✨ Features
This game includes three fun modes:

1️⃣ Guess the Country
A random mystery country is selected.

You guess countries one by one.

You'll get feedback on:

Whether your guess is adjacent to the mystery country.

How far your guess is from the mystery country.

What direction to move in (with arrow indicators like ⬆️, ↘️, etc.).

2️⃣ Guess the Capital
A random capital is selected (you’re guessing the capital name).

You'll get clues based on:

The distance and direction from your guessed capital to the mystery capital.

Whether the guessed capital’s country borders the mystery capital’s country.

3️⃣ Border Blitz
A random country is selected.

Your task is to guess all of its neighboring countries.

Immediate feedback is provided for correct/incorrect guesses.

🧠 How Is AI Used?
Uses fuzzy string matching (via thefuzz) to interpret imprecise or partially correct user input.

Intelligent suggestions and forgiving input detection make it feel more natural and accessible.

🧩 Libraries Used
pandas — Data handling

geopy — Calculating geographic distance between countries/capitals

thefuzz — Fuzzy matching of user input to known country/capital names

math — Directional bearing calculations

random — Random selection of countries/capitals

📁 Data Files Required
Make sure these files are in the same directory as the Python script:

country-capital-lat-long-population.csv
Contains country names, capital names, and their coordinates.

GEODATASOURCE-COUNTRY-BORDERS (1).CSV
Contains bordering country relationships.
