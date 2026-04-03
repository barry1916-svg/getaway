"""
Getaway Web App — Flask backend serving the destination dashboard.
Runs locally with: python app.py
Deployed on Railway via the Procfile.
"""

import os
import sys
import time
from datetime import datetime
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

load_dotenv()

# Import weather-checking logic from getaway.py in the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import getaway

app = Flask(__name__)

# Simple in-memory cache (persists across requests on Railway / local; not on Vercel)
_cache = {"data": None, "ts": 0}
CACHE_TTL = 3600  # 1 hour


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather")
def weather():
    now = time.time()

    # Return cached data if fresh
    if _cache["data"] is not None and (now - _cache["ts"]) < CACHE_TTL:
        resp = jsonify(_cache["data"])
        resp.headers["Cache-Control"] = "public, s-maxage=3600"
        return resp

    # Pre-filter: only check destinations that have flights available this month
    current_month = datetime.now().month
    active = [
        d for d in getaway.DESTINATIONS
        if getaway.get_available_routes(d["city"], current_month)
    ]

    results = []
    for dest in active:
        result = getaway.check_destination(dest)
        if result:
            results.append({
                "city": result["city"],
                "country": result["country"],
                "best_temp": round(result["best_temp"], 1),
                "good_days_count": len(result["good_days"]),
                "depart_date": result["depart_date"],
                "return_date": result["return_date"],
                # Convert tuples to lists for JSON serialisation
                "routes": [list(r) for r in result["routes"]],
                "forecast": result["all_days"],
            })

    # Hottest destinations first
    results.sort(key=lambda x: x["best_temp"], reverse=True)

    data = {
        "destinations": results,
        "updated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "count": len(results),
    }

    _cache["data"] = data
    _cache["ts"] = now

    resp = jsonify(data)
    resp.headers["Cache-Control"] = "public, s-maxage=3600"
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
