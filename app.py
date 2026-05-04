print("THIS IS THE FILE BEING EXECUTED")
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ✅ Home route (THIS FIXES 404)
@app.route('/')
def home():
    return render_template("index.html")

# ✅ Weather route
@app.route('/weather')
def get_weather():
    city = request.args.get('city')

    if not city:
        return jsonify({"error": "No city provided"})

    API_KEY = "4271987c02d2e74a4de95d162de2de1b"

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return jsonify({"error": "City not found"})

    return jsonify({
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    })

if __name__ == "__main__":
    app.run(debug=True)