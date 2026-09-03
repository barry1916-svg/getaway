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
from urllib.parse import quote
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

# Cities always shown on their country's page, regardless of weather ranking
PINNED_DESTINATIONS = {
    "Spain": ["Santiago de Compostela", "Bilbao"],
}

# Origin airports covered by the dedicated "Shannon & Knock" home page panel
SHANNON_KNOCK_ORIGINS = {"Shannon", "Knock"}


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


def _routes_from(r, origins):
    """Return the (airline, airport) tuples in a candidate whose airport is in `origins`."""
    return [route for route in r["routes"] if route[1] in origins]


def _with_routes(r, routes):
    """Shallow-copy a candidate result with its routes replaced."""
    return {**r, "routes": routes}


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
    return render_template("country.html", heading=country, api_path=f"/api/destinations/{quote(country)}")


@app.route("/shannon-knock")
def shannon_knock_page():
    return render_template(
        "country.html", heading="Shannon & Knock", api_path="/api/destinations/shannon-knock"
    )


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

    # Spain is always shown, even if it didn't naturally rank in the top 6
    top = summaries[:TOP_COUNTRIES]
    if not any(c["country"] == "Spain" for c in top):
        spain = next((c for c in summaries if c["country"] == "Spain"), {
            "country": "Spain", "count": 0,
            "best_city": None, "best_temp": None, "best_good_days": 0,
        })
        top = top[:TOP_COUNTRIES - 1] + [spain]

    sk_matches = [r for r in candidates if _routes_from(r, SHANNON_KNOCK_ORIGINS)]
    if sk_matches:
        best = sk_matches[0]
        shannon_knock = {
            "count": len(sk_matches),
            "best_city": best["city"],
            "best_temp": round(best["best_temp"], 1),
            "best_good_days": len(best["good_days"]),
        }
    else:
        shannon_knock = {"count": 0, "best_city": None, "best_temp": None, "best_good_days": 0}

    data = {
        "countries": top,
        "shannon_knock": shannon_knock,
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

    # Always include certain cities regardless of weather ranking; fetch directly if they didn't make candidates
    pinned_cities = PINNED_DESTINATIONS.get(country, [])
    if pinned_cities:
        pinned = []
        for city in pinned_cities:
            existing = next((r for r in matches if r["city"] == city), None)
            if existing:
                pinned.append(existing)
                continue
            dest = next((d for d in getaway.DESTINATIONS if d["city"] == city), None)
            if dest:
                result = getaway.check_destination_unconstrained(dest)
                if result:
                    pinned.append(result)
        pinned_names = {r["city"] for r in pinned}
        others = [r for r in matches if r["city"] not in pinned_names]
        matches = others[:TOP_DESTINATIONS_PER_COUNTRY - len(pinned)] + pinned
    else:
        matches = matches[:TOP_DESTINATIONS_PER_COUNTRY]

    destinations = [_serialise_destination(r) for r in matches]

    data = {
        "label": country,
        "destinations": destinations,
        "updated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "count": len(destinations),
    }

    resp = jsonify(data)
    resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=3600"
    return resp


@app.route("/api/destinations/shannon-knock")
def destinations_shannon_knock():
    force = request.args.get("refresh") == "1"
    candidates = _get_candidates(force)

    matches = []
    for r in candidates:
        sk_routes = _routes_from(r, SHANNON_KNOCK_ORIGINS)
        if sk_routes:
            matches.append(_with_routes(r, sk_routes))
    matches = matches[:TOP_DESTINATIONS_PER_COUNTRY]

    destinations = [_serialise_destination(r) for r in matches]

    data = {
        "label": "Shannon & Knock",
        "destinations": destinations,
        "updated_at": datetime.utcnow().strftime("%d %b %Y, %H:%M UTC"),
        "count": len(destinations),
    }

    resp = jsonify(data)
    resp.headers["Cache-Control"] = "public, max-age=0, s-maxage=3600"
    return resp


@app.route("/api/debug/weather-test")
def debug_weather_test():
    """Temporary diagnostic: surface the real exception from an Open-Meteo call in this environment."""
    import traceback
    try:
        current_month = datetime.now().month
        active = [d for d in getaway.DESTINATIONS if getaway.get_available_routes(d["city"], current_month)]
        t0 = time.time()
        forecasts = getaway.get_weather_forecasts_bulk(active)
        elapsed = time.time() - t0
        candidates = []
        for dest, forecast in zip(active, forecasts):
            result = getaway.check_destination_from_forecast(dest, forecast)
            if result:
                candidates.append(result)
        return jsonify({
            "ok": True,
            "active_count": len(active),
            "elapsed_seconds": round(elapsed, 2),
            "forecasts_none_count": sum(1 for f in forecasts if f is None),
            "candidates_count": len(candidates),
            "none_cities": [d["city"] for d, f in zip(active, forecasts) if f is None],
        })
    except Exception as e:
        return jsonify({"ok": False, "error_type": type(e).__name__, "error": str(e), "traceback": traceback.format_exc()})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
