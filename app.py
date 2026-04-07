"""
Getaway Web App — Flask backend serving the destination dashboard.
Runs locally with: python app.py
Deployed on Railway via the Procfile.
"""

import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

load_dotenv()

# Import weather-checking logic from getaway.py in the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import getaway

app = Flask(__name__)

# Simple in-memory cache (persists across requests on Railway / local; not on Vercel)
_cache = {"data": None, "ts": 0}
CACHE_TTL = 3600  # 1 hour


def _booking_links(result):
    """Generate Skyscanner, Airbnb and Booking.com search URLs."""
    city, country = result["city"], result["country"]
    dep, ret = result["depart_date"], result["return_date"]
    return {
        "skyscanner_url": getaway.get_skyscanner_url("Dublin", city, dep, ret),
        "airbnb_url": (
            f"https://www.airbnb.com/s/{city}/homes"
            f"?checkin={dep}&checkout={ret}"
            f"&adults=2&room_types%5B%5D=Entire%20home%2Fapt&min_bedrooms=1"
        ),
        "booking_url": (
            f"https://www.booking.com/searchresults.html"
            f"?ss={city}%2C+{country}"
            f"&checkin={dep}&checkout={ret}"
            f"&group_adults=2&no_rooms=1"
        ),
    }


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

    # Return cached data if fresh (skip cache on ?refresh=1)
    force = request.args.get("refresh") == "1"
    if not force and _cache["data"] is not None and (now - _cache["ts"]) < CACHE_TTL:
        resp = jsonify(_cache["data"])
        resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=3600"
        return resp

    # Pre-filter: only check destinations that have flights available this month
    current_month = datetime.now().month
    active = [
        d for d in getaway.DESTINATIONS
        if getaway.get_available_routes(d["city"], current_month)
    ]

    results = []
    raw_candidates = []  # all destinations regardless of criteria (for fallback)

    def _check(dest):
        result = getaway.check_destination(dest)
        if result:
            return ("ok", result)
        raw = getaway.check_destination_unconstrained(dest)
        return ("raw", raw)

    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(_check, dest): dest for dest in active}
        for future in as_completed(futures):
            kind, data_ = future.result()
            if kind == "ok":
                results.append({
                    "city": data_["city"],
                    "country": data_["country"],
                    "best_temp": round(data_["best_temp"], 1),
                    "good_days_count": len(data_["good_days"]),
                    "depart_date": data_["depart_date"],
                    "return_date": data_["return_date"],
                    "routes": _serialise_routes(data_),
                    "forecast": data_["all_days"],
                    **_booking_links(data_),
                })
                raw_candidates.append(data_)
            elif data_:
                raw_candidates.append(data_)

    # Most sunny days first, then hottest
    results.sort(key=lambda x: (x["good_days_count"], x["best_temp"]), reverse=True)

    # Top 5 fallback destinations when nothing meets the criteria
    fallback = []
    if not results:
        raw_candidates.sort(key=lambda x: (len(x["good_days"]), x["best_temp"]), reverse=True)
        for raw in raw_candidates[:5]:
            fallback.append({
                "city": raw["city"],
                "country": raw["country"],
                "best_temp": round(raw["best_temp"], 1),
                "good_days_count": len(raw["good_days"]),
                "depart_date": raw["depart_date"],
                "return_date": raw["return_date"],
                "routes": _serialise_routes(raw),
                "forecast": raw["all_days"],
                **_booking_links(raw),
            })

    data = {
        "destinations": results,
        "fallback": fallback,
        "updated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "count": len(results),
    }

    _cache["data"] = data
    _cache["ts"] = now

    resp = jsonify(data)
    resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=3600"
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
