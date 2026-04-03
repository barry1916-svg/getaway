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


def _serialise_routes(result):
    """Convert route tuples to dicts with booking URLs."""
    return [
        {
            "airline": airline,
            "airport": airport,
            "url": getaway.get_booking_url(
                airline, airport, result["city"],
                result["depart_date"], result["return_date"]
            ),
        }
        for airline, airport in result["routes"]
    ]


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
    best_raw = None  # best destination regardless of criteria (for no-match fallback)

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
                "routes": _serialise_routes(result),
                "forecast": result["all_days"],
            })
            if best_raw is None or result["best_temp"] > best_raw["best_temp"]:
                best_raw = result
        else:
            raw = getaway.check_destination_unconstrained(dest)
            if raw and (best_raw is None or raw["best_temp"] > best_raw["best_temp"]):
                best_raw = raw

    # Hottest destinations first
    results.sort(key=lambda x: x["best_temp"], reverse=True)

    # Serialise fallback destination (shown when no results meet criteria)
    fallback = None
    if not results and best_raw:
        fallback = {
            "city": best_raw["city"],
            "country": best_raw["country"],
            "best_temp": round(best_raw["best_temp"], 1),
            "good_days_count": len(best_raw["good_days"]),
            "depart_date": best_raw["depart_date"],
            "return_date": best_raw["return_date"],
            "routes": _serialise_routes(best_raw),
            "forecast": best_raw["all_days"],
        }

    data = {
        "destinations": results,
        "fallback": fallback,
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
