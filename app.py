import requests
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    location = request.args.get("location")
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    # Case 1: Location name given → use Geocoding API
    if location:
        geo_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_API_KEY}"
        geo_resp = requests.get(geo_url).json()

        if not geo_resp.get("results"):
            return jsonify({"error": "Invalid location"}), 400

        lat = geo_resp["results"][0]["geometry"]["location"]["lat"]
        lng = geo_resp["results"][0]["geometry"]["location"]["lng"]

    # Case 2: Lat/lng directly given
    if not lat or not lng:
        return jsonify({"error": "Location or coordinates required"}), 400

    # Places API → nearby cafes
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius=2000&type=cafe&key={GOOGLE_API_KEY}"
    places_resp = requests.get(places_url).json()

    cafes = []
    for place in places_resp.get("results", []):
        cafes.append({
            "name": place["name"],
            "lat": place["geometry"]["location"]["lat"],
            "lng": place["geometry"]["location"]["lng"],
            "rating": place.get("rating"),
            "address": place.get("vicinity")
        })

    return jsonify({"lat": float(lat), "lng": float(lng), "cafes": cafes})

if __name__ == "__main__":
    app.run(debug=True)
