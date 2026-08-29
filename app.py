"""
Getaway Web App — Flask backend serving the destination dashboard.
Runs locally with: python app.py
Deployed on Railway via the Procfile.
"""

import os
import sys
import time
from collections import defaultdict
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

TOP_COUNTRIES = 6
TOP_DESTINATIONS_PER_COUNTRY = 12


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


def _serialise_destination(r):
    """Convert a raw candidate result into the JSON shape the frontend renders."""
    return {
        "city": r["city"],
        "country": r["country"],
        "best_temp": round(r["best_temp"], 1),
        "good_days_count": len(r["good_days"]),
        "depart_date": r["depart_date"],
        "return_date": r["return_date"],
        "routes": _serialise_routes(r),
        "forecast": r["all_days"],
        **_booking_links(r),
    }


def _get_candidates(force=False):
    """Return every qualifying destination, sorted best weather first, using a 1h cache."""
    now = time.time()
    if not force and _cache["data"] is not None and (now - _cache["ts"]) < CACHE_TTL:
        return _cache["data"]

    # Pre-filter: only check destinations that have flights available this month
    current_month = datetime.now().month
    active = [
        d for d in getaway.DESTINATIONS
        if getaway.get_available_routes(d["city"], current_month)
    ]

    # Fetch all forecasts in batches to avoid rate-limiting
    forecasts = getaway.get_weather_forecasts_bulk(active)
    candidates = []
    for dest, forecast in zip(active, forecasts):
        result = getaway.check_destination_from_forecast(dest, forecast)
        if result:
            candidates.append(result)

    # Best weather first: most sunny days, then hottest
    candidates.sort(key=lambda x: (len(x["good_days"]), x["best_temp"]), reverse=True)

    _cache["data"] = candidates
    _cache["ts"] = now
    return candidates


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/country/<country>")
def country_page(country):
    return render_template("country.html", country=country)


@app.route("/api/countries")
def countries():
    force = request.args.get("refresh") == "1"
    candidates = _get_candidates(force)

    by_country = defaultdict(list)
    for r in candidates:
        by_country[r["country"]].append(r)

    summaries = []
    for country, dests in by_country.items():
        best = dests[0]  # dests inherit the overall best-weather-first order
        summaries.append({
            "country": country,
            "count": len(dests),
            "best_city": best["city"],
            "best_temp": round(best["best_temp"], 1),
            "best_good_days": len(best["good_days"]),
        })

    # Rank countries by their best destination's weather
    summaries.sort(key=lambda c: (c["best_good_days"], c["best_temp"]), reverse=True)

    data = {
        "countries": summaries[:TOP_COUNTRIES],
        "updated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
    }

    resp = jsonify(data)
    resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=3600"
    return resp


@app.route("/api/destinations/<country>")
def destinations_by_country(country):
    force = request.args.get("refresh") == "1"
    candidates = _get_candidates(force)

    matches = [r for r in candidates if r["country"] == country]

    # Always include Santiago de Compostela in Spain's results; fetch directly if it didn't make candidates
    if country == "Spain":
        pinned = [r for r in matches if r["city"] == "Santiago de Compostela"]
        if not pinned:
            santiago_dest = next(
                (d for d in getaway.DESTINATIONS if d["city"] == "Santiago de Compostela"), None
            )
            if santiago_dest:
                result = getaway.check_destination_unconstrained(santiago_dest)
                if result:
                    pinned = [result]
        others = [r for r in matches if r["city"] != "Santiago de Compostela"]
        matches = others[:TOP_DESTINATIONS_PER_COUNTRY - len(pinned)] + pinned
    else:
        matches = matches[:TOP_DESTINATIONS_PER_COUNTRY]

    destinations = [_serialise_destination(r) for r in matches]

    data = {
        "country": country,
        "destinations": destinations,
        "updated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "count": len(destinations),
    }

    resp = jsonify(data)
    resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=3600"
    return resp


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
