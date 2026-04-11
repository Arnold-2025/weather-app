from flask import Flask, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature REAL,
        description TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# Home route
@app.route("/")
def home():
    return "Weather Backend Running"

# Weather route (using Open-Meteo - NO API KEY)
@app.route("/weather", methods=["GET"])
def get_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City is required"}), 400

    # Step 1: Get coordinates
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
    geo_response = requests.get(geo_url).json()

    if "results" not in geo_response:
        return jsonify({"error": "City not found"}), 404

    lat = geo_response["results"][0]["latitude"]
    lon = geo_response["results"][0]["longitude"]
    city_name = geo_response["results"][0]["name"]

    # Step 2: Get weather
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    weather_data = requests.get(weather_url).json()

    current = weather_data.get("current_weather")

    if not current:
        return jsonify({"error": "Weather data not available"}), 500

    result = {
        "city": city_name,
        "temperature": current["temperature"],
        "windspeed": current["windspeed"]
    }

    # Save to DB
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO weather (city, temperature, description) VALUES (?, ?, ?)",
        (result["city"], result["temperature"], f"windspeed: {result['windspeed']}")
    )

    conn.commit()
    conn.close()

    return jsonify(result)

# History route
@app.route("/history", methods=["GET"])
def get_history():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM weather")
    rows = cursor.fetchall()

    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "city": row[1],
            "temperature": row[2],
            "description": row[3]
        })

    return jsonify(data)


@app.route("/delete/<int:id>", methods=["POST", "GET"])
def delete_data(id):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM weather WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({"message": "Deleted successfully"})

@app.route("/update/<int:id>")
def update_data(id):
    new_city = request.args.get("city")

    if not new_city:
        return jsonify({"error": "City is required"}), 400

    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()

    cursor.execute("UPDATE weather SET city=? WHERE id=?", (new_city, id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Updated successfully"})
if __name__ == "__main__":
    app.run(debug=True)
