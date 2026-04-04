#!/usr/bin/env python3
"""
Weather Alert App - Check sunny destinations with direct flights from Ireland
"""

import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env in the same directory as this script
script_dir = Path(__file__).parent
load_dotenv(script_dir / ".env")

# European destinations with direct flights from Ireland (Dublin, Cork, Shannon)
DESTINATIONS = [
    # Spain
    {"city": "Barcelona", "country": "Spain", "lat": 41.3851, "lon": 2.1734},
    {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lon": -3.7038},
    {"city": "Malaga", "country": "Spain", "lat": 36.7213, "lon": -4.4213},
    {"city": "Seville", "country": "Spain", "lat": 37.3891, "lon": -5.9845},
    {"city": "Valencia", "country": "Spain", "lat": 39.4699, "lon": -0.3763},
    {"city": "Alicante", "country": "Spain", "lat": 38.3452, "lon": -0.4810},
    {"city": "Palma Mallorca", "country": "Spain", "lat": 39.5696, "lon": 2.6502},
    {"city": "Ibiza", "country": "Spain", "lat": 38.9067, "lon": 1.4206},
    {"city": "Menorca", "country": "Spain", "lat": 39.9496, "lon": 4.1104},
    {"city": "Tenerife", "country": "Spain", "lat": 28.2916, "lon": -16.6291},
    {"city": "Gran Canaria", "country": "Spain", "lat": 27.9202, "lon": -15.5474},
    {"city": "Lanzarote", "country": "Spain", "lat": 28.9500, "lon": -13.6000},
    {"city": "Fuerteventura", "country": "Spain", "lat": 28.3587, "lon": -14.0530},
    {"city": "Bilbao", "country": "Spain", "lat": 43.2630, "lon": -2.9350},
    {"city": "Santiago de Compostela", "country": "Spain", "lat": 42.8782, "lon": -8.5448},
    {"city": "Girona", "country": "Spain", "lat": 41.9794, "lon": 2.8214},
    {"city": "Reus", "country": "Spain", "lat": 41.1561, "lon": 1.1069},
    {"city": "Murcia", "country": "Spain", "lat": 37.9922, "lon": -1.1307},
    {"city": "Almeria", "country": "Spain", "lat": 36.8402, "lon": -2.4679},
    {"city": "Jerez", "country": "Spain", "lat": 36.6850, "lon": -6.1261},
    {"city": "Santander", "country": "Spain", "lat": 43.4623, "lon": -3.8100},
    {"city": "Asturias", "country": "Spain", "lat": 43.5643, "lon": -6.0346},
    {"city": "Zaragoza", "country": "Spain", "lat": 41.6488, "lon": -0.8891},
    {"city": "Granada", "country": "Spain", "lat": 37.1773, "lon": -3.5986},
    {"city": "A Coruna", "country": "Spain", "lat": 43.3713, "lon": -8.4188},
    {"city": "Vigo", "country": "Spain", "lat": 42.2328, "lon": -8.7226},

    # Portugal
    {"city": "Lisbon", "country": "Portugal", "lat": 38.7223, "lon": -9.1393},
    {"city": "Porto", "country": "Portugal", "lat": 41.1579, "lon": -8.6291},
    {"city": "Faro", "country": "Portugal", "lat": 37.0194, "lon": -7.9322},
    {"city": "Funchal", "country": "Portugal", "lat": 32.6669, "lon": -16.9241},
    {"city": "Ponta Delgada", "country": "Portugal", "lat": 37.7833, "lon": -25.5333},

    # Italy
    {"city": "Rome", "country": "Italy", "lat": 41.9028, "lon": 12.4964},
    {"city": "Milan", "country": "Italy", "lat": 45.4642, "lon": 9.1900},
    {"city": "Venice", "country": "Italy", "lat": 45.4408, "lon": 12.3155},
    {"city": "Naples", "country": "Italy", "lat": 40.8518, "lon": 14.2681},
    {"city": "Pisa", "country": "Italy", "lat": 43.7228, "lon": 10.4017},
    {"city": "Bologna", "country": "Italy", "lat": 44.4949, "lon": 11.3426},
    {"city": "Turin", "country": "Italy", "lat": 45.0703, "lon": 7.6869},
    {"city": "Bari", "country": "Italy", "lat": 41.1171, "lon": 16.8719},
    {"city": "Verona", "country": "Italy", "lat": 45.4384, "lon": 10.9916},
    # Sardinia
    {"city": "Cagliari", "country": "Italy", "lat": 39.2238, "lon": 9.1217},

    {"city": "Alghero", "country": "Italy", "lat": 40.5589, "lon": 8.3190},
    # Sicily
    {"city": "Palermo", "country": "Italy", "lat": 38.1157, "lon": 13.3615},
    {"city": "Catania", "country": "Italy", "lat": 37.5079, "lon": 15.0830},

    # Greece
    {"city": "Athens", "country": "Greece", "lat": 37.9838, "lon": 23.7275},
    {"city": "Santorini", "country": "Greece", "lat": 36.3932, "lon": 25.4615},
    {"city": "Heraklion", "country": "Greece", "lat": 35.3387, "lon": 25.1442},
    {"city": "Chania", "country": "Greece", "lat": 35.5138, "lon": 24.0180},
    {"city": "Kos", "country": "Greece", "lat": 36.8935, "lon": 26.9861},
    {"city": "Rhodes", "country": "Greece", "lat": 36.4349, "lon": 28.2176},
    {"city": "Corfu", "country": "Greece", "lat": 39.6243, "lon": 19.9217},
    {"city": "Zakynthos", "country": "Greece", "lat": 37.7870, "lon": 20.8979},
    {"city": "Kefalonia", "country": "Greece", "lat": 38.1794, "lon": 20.4894},
    {"city": "Mykonos", "country": "Greece", "lat": 37.4467, "lon": 25.3289},
    {"city": "Preveza", "country": "Greece", "lat": 38.9504, "lon": 20.7653},
    {"city": "Skiathos", "country": "Greece", "lat": 39.1622, "lon": 23.4917},
    {"city": "Kalamata", "country": "Greece", "lat": 37.0389, "lon": 22.1143},
    {"city": "Thessaloniki", "country": "Greece", "lat": 40.6401, "lon": 22.9444},

    # Croatia
    {"city": "Split", "country": "Croatia", "lat": 43.5081, "lon": 16.4402},
    {"city": "Dubrovnik", "country": "Croatia", "lat": 42.6507, "lon": 18.0944},
    {"city": "Zagreb", "country": "Croatia", "lat": 45.8150, "lon": 15.9819},
    {"city": "Zadar", "country": "Croatia", "lat": 44.1194, "lon": 15.2314},
    {"city": "Pula", "country": "Croatia", "lat": 44.8666, "lon": 13.8496},

    # Montenegro
    {"city": "Podgorica", "country": "Montenegro", "lat": 42.4304, "lon": 19.2594},
    {"city": "Tivat", "country": "Montenegro", "lat": 42.4047, "lon": 18.7235},

    # Cyprus
    {"city": "Paphos", "country": "Cyprus", "lat": 34.7720, "lon": 32.4297},
    {"city": "Larnaca", "country": "Cyprus", "lat": 34.9229, "lon": 33.6233},

    # Turkey
    {"city": "Antalya", "country": "Turkey", "lat": 36.8969, "lon": 30.7133},
    {"city": "Dalaman", "country": "Turkey", "lat": 36.7130, "lon": 28.7875},
    {"city": "Bodrum", "country": "Turkey", "lat": 37.0343, "lon": 27.4305},
    {"city": "Istanbul", "country": "Turkey", "lat": 41.0082, "lon": 28.9784},

    # France
    {"city": "Nice", "country": "France", "lat": 43.7102, "lon": 7.2620},
    {"city": "Marseille", "country": "France", "lat": 43.2965, "lon": 5.3698},
    {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522},
    {"city": "Bordeaux", "country": "France", "lat": 44.8378, "lon": -0.5792},
    {"city": "Toulouse", "country": "France", "lat": 43.6047, "lon": 1.4442},
    {"city": "Lyon", "country": "France", "lat": 45.7640, "lon": 4.8357},
    {"city": "Nantes", "country": "France", "lat": 47.2184, "lon": -1.5536},
    {"city": "Montpellier", "country": "France", "lat": 43.6108, "lon": 3.8767},
    {"city": "Biarritz", "country": "France", "lat": 43.4832, "lon": -1.5586},
    {"city": "Carcassonne", "country": "France", "lat": 43.2130, "lon": 2.3491},
    {"city": "Beziers", "country": "France", "lat": 43.3442, "lon": 3.2150},
    {"city": "Bergerac", "country": "France", "lat": 44.8530, "lon": 0.4833},
    {"city": "La Rochelle", "country": "France", "lat": 46.1603, "lon": -1.1511},
    {"city": "Perpignan", "country": "France", "lat": 42.6887, "lon": 2.8948},
    {"city": "Grenoble", "country": "France", "lat": 45.1885, "lon": 5.7245},

    # Other Western Europe
    {"city": "Amsterdam", "country": "Netherlands", "lat": 52.3676, "lon": 4.9041},
    {"city": "Brussels", "country": "Belgium", "lat": 50.8503, "lon": 4.3517},
    {"city": "Geneva", "country": "Switzerland", "lat": 46.2044, "lon": 6.1432},
    {"city": "Zurich", "country": "Switzerland", "lat": 47.3769, "lon": 8.5417},

    # Central Europe
    {"city": "Budapest", "country": "Hungary", "lat": 47.4979, "lon": 19.0402},
    {"city": "Prague", "country": "Czech Republic", "lat": 50.0755, "lon": 14.4378},
    {"city": "Vienna", "country": "Austria", "lat": 48.2082, "lon": 16.3738},
    {"city": "Bratislava", "country": "Slovakia", "lat": 48.1486, "lon": 17.1077},
    {"city": "Ljubljana", "country": "Slovenia", "lat": 46.0569, "lon": 14.5058},

    # Poland
    {"city": "Krakow", "country": "Poland", "lat": 50.0647, "lon": 19.9450},
    {"city": "Warsaw", "country": "Poland", "lat": 52.2297, "lon": 21.0122},

    # Nordics
    {"city": "Stockholm", "country": "Sweden", "lat": 59.3293, "lon": 18.0686},
    {"city": "Copenhagen", "country": "Denmark", "lat": 55.6761, "lon": 12.5683},
    {"city": "Oslo", "country": "Norway", "lat": 59.9139, "lon": 10.7522},
    {"city": "Helsinki", "country": "Finland", "lat": 60.1699, "lon": 24.9384},

    # Baltics
    {"city": "Riga", "country": "Latvia", "lat": 56.9496, "lon": 24.1052},
    {"city": "Tallinn", "country": "Estonia", "lat": 59.4370, "lon": 24.7536},
    {"city": "Vilnius", "country": "Lithuania", "lat": 54.6872, "lon": 25.2797},

    # Balkans
    {"city": "Sofia", "country": "Bulgaria", "lat": 42.6977, "lon": 23.3219},
    {"city": "Bucharest", "country": "Romania", "lat": 44.4268, "lon": 26.1025},

    # Malta
    {"city": "Malta", "country": "Malta", "lat": 35.9375, "lon": 14.3754},
]

# WMO Weather codes mapping with icons
WEATHER_CODES = {
    0: {"desc": "Clear sky", "icon": "☀️"},
    1: {"desc": "Mainly clear", "icon": "🌤️"},
    2: {"desc": "Partly cloudy", "icon": "⛅"},
    3: {"desc": "Overcast", "icon": "☁️"},
    45: {"desc": "Foggy", "icon": "🌫️"},
    48: {"desc": "Depositing rime fog", "icon": "🌫️"},
    51: {"desc": "Light drizzle", "icon": "🌦️"},
    53: {"desc": "Moderate drizzle", "icon": "🌦️"},
    55: {"desc": "Dense drizzle", "icon": "🌧️"},
    61: {"desc": "Slight rain", "icon": "🌧️"},
    63: {"desc": "Moderate rain", "icon": "🌧️"},
    65: {"desc": "Heavy rain", "icon": "🌧️"},
    71: {"desc": "Slight snow", "icon": "🌨️"},
    73: {"desc": "Moderate snow", "icon": "🌨️"},
    75: {"desc": "Heavy snow", "icon": "❄️"},
    80: {"desc": "Slight rain showers", "icon": "🌦️"},
    81: {"desc": "Moderate rain showers", "icon": "🌧️"},
    82: {"desc": "Violent rain showers", "icon": "⛈️"},
    95: {"desc": "Thunderstorm", "icon": "⛈️"},
}

# Days to skip before starting forecast
FORECAST_START_OFFSET = 3

# Airline logos
AIRLINE_LOGOS = {
    "Ryanair": "https://www.google.com/s2/favicons?domain=ryanair.com&sz=64",
    "Aer Lingus": "https://www.google.com/s2/favicons?domain=aerlingus.com&sz=64",
    "Iberia": "https://www.google.com/s2/favicons?domain=iberia.com&sz=64",
    "TAP": "https://www.google.com/s2/favicons?domain=flytap.com&sz=64",
    "Air France": "https://www.google.com/s2/favicons?domain=airfrance.com&sz=64",
    "KLM": "https://www.google.com/s2/favicons?domain=klm.com&sz=64",
    "Swiss": "https://www.google.com/s2/favicons?domain=swiss.com&sz=64",
    "SAS": "https://www.google.com/s2/favicons?domain=flysas.com&sz=64",
    "Skyscanner": "https://www.google.com/s2/favicons?domain=skyscanner.com&sz=64",
    "Airbnb": "https://www.google.com/s2/favicons?domain=airbnb.com&sz=64",
    "Booking": "https://www.google.com/s2/favicons?domain=booking.com&sz=64",
}


def get_skyscanner_url(origin: str, destination: str, depart_date: str, return_date: str) -> str:
    """Generate a Skyscanner search URL."""
    origin_code = IRISH_AIRPORTS.get(origin, "DUB")
    dest_code = DESTINATION_AIRPORTS.get(destination, "")
    dep_formatted = depart_date.replace("-", "")
    ret_formatted = return_date.replace("-", "")
    return f"https://www.skyscanner.ie/transport/flights/{origin_code.lower()}/{dest_code.lower()}/{dep_formatted}/{ret_formatted}/?adultsv2=1&cabinclass=economy&preferdirects=true"

# Irish airport IATA codes
IRISH_AIRPORTS = {
    "Dublin": "DUB",
    "Cork": "ORK",
    "Shannon": "SNN",
    "Knock": "NOC",
    "Kerry": "KIR",
}

# Destination airport IATA codes
DESTINATION_AIRPORTS = {
    # Spain
    "Barcelona": "BCN", "Madrid": "MAD", "Malaga": "AGP", "Seville": "SVQ",
    "Valencia": "VLC", "Alicante": "ALC", "Palma Mallorca": "PMI", "Ibiza": "IBZ",
    "Menorca": "MAH", "Tenerife": "TFS", "Gran Canaria": "LPA", "Lanzarote": "ACE",
    "Fuerteventura": "FUE", "Bilbao": "BIO", "Santiago de Compostela": "SCQ",
    "Girona": "GRO", "Reus": "REU", "Murcia": "RMU", "Almeria": "LEI",
    "Jerez": "XRY", "Santander": "SDR", "Asturias": "OVD", "Zaragoza": "ZAZ",
    "Granada": "GRX", "A Coruna": "LCG", "Vigo": "VGO",
    # Portugal
    "Lisbon": "LIS", "Porto": "OPO", "Faro": "FAO", "Funchal": "FNC", "Ponta Delgada": "PDL",
    # Italy
    "Rome": "FCO", "Milan": "MXP", "Venice": "VCE", "Naples": "NAP",
    "Pisa": "PSA", "Bologna": "BLQ", "Turin": "TRN", "Bari": "BRI", "Verona": "VRN",
    "Cagliari": "CAG", "Alghero": "AHO", "Palermo": "PMO", "Catania": "CTA",
    # Greece
    "Athens": "ATH", "Santorini": "JTR", "Heraklion": "HER", "Chania": "CHQ",
    "Kos": "KGS", "Rhodes": "RHO", "Corfu": "CFU", "Zakynthos": "ZTH",
    "Kefalonia": "EFL", "Mykonos": "JMK", "Preveza": "PVK", "Skiathos": "JSI",
    "Kalamata": "KLX", "Thessaloniki": "SKG",
    # Croatia
    "Split": "SPU", "Dubrovnik": "DBV", "Zagreb": "ZAG", "Zadar": "ZAD", "Pula": "PUY",
    # Montenegro
    "Podgorica": "TGD", "Tivat": "TIV",
    # Cyprus
    "Paphos": "PFO", "Larnaca": "LCA",
    # Turkey
    "Antalya": "AYT", "Dalaman": "DLM", "Bodrum": "BJV", "Istanbul": "IST",
    # France
    "Nice": "NCE", "Marseille": "MRS", "Paris": "CDG", "Bordeaux": "BOD",
    "Toulouse": "TLS", "Lyon": "LYS", "Nantes": "NTE", "Montpellier": "MPL",
    "Biarritz": "BIQ", "Carcassonne": "CCF", "Beziers": "BZR", "Bergerac": "EGC", "La Rochelle": "LRH",
    "Perpignan": "PGF", "Grenoble": "GNB",
    # Other
    "Amsterdam": "AMS", "Brussels": "BRU", "Geneva": "GVA", "Zurich": "ZRH",
    "Budapest": "BUD", "Prague": "PRG", "Vienna": "VIE", "Bratislava": "BTS",
    "Ljubljana": "LJU", "Krakow": "KRK", "Warsaw": "WAW", "Stockholm": "ARN",
    "Copenhagen": "CPH", "Oslo": "OSL", "Helsinki": "HEL", "Riga": "RIX",
    "Tallinn": "TLL", "Vilnius": "VNO", "Sofia": "SOF", "Bucharest": "OTP",
    # Malta
    "Malta": "MLA",
}


def get_booking_url(airline: str, origin: str, destination: str, depart_date: str, return_date: str) -> str:
    """Generate a pre-populated booking URL for the airline."""
    origin_code = IRISH_AIRPORTS.get(origin, "DUB")
    dest_code = DESTINATION_AIRPORTS.get(destination, "")

    if airline == "Ryanair":
        return f"https://www.ryanair.com/gb/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={depart_date}&dateIn={return_date}&originIata={origin_code}&destinationIata={dest_code}&isReturn=true"

    elif airline == "Aer Lingus":
        return "https://www.aerlingus.com"

    elif airline == "Iberia":
        return f"https://www.iberia.com/gb/?FLIGHT_ORIGIN={origin_code}&FLIGHT_DESTINATION={dest_code}&FLIGHT_DATE_1={depart_date}&FLIGHT_DATE_2={return_date}&adults=1"

    elif airline == "TAP":
        return "https://www.flytap.com"

    elif airline == "Air France":
        return f"https://www.airfrance.co.uk/search/offers?pax=1:0:0:0:0:0:0:0&cabinClass=ECONOMY&activeConnection=0&connections={origin_code}-A>{dest_code}-A-{depart_date}_{dest_code}-A>{origin_code}-A-{return_date}"

    elif airline == "KLM":
        return f"https://www.klm.co.uk/search/offers?pax=1:0:0:0:0:0:0:0&cabinClass=ECONOMY&activeConnection=0&connections={origin_code}-A>{dest_code}-A-{depart_date}_{dest_code}-A>{origin_code}-A-{return_date}"

    elif airline == "Swiss":
        return f"https://www.swiss.com/gb/en/book/outbound?adults=1&from={origin_code}&to={dest_code}&departDate={depart_date}&returnDate={return_date}"

    elif airline == "SAS":
        return f"https://www.flysas.com/en/book/flights?from={origin_code}&to={dest_code}&outDate={depart_date}&inDate={return_date}&adt=1"

    else:
        return f"https://www.google.com/travel/flights?q=flights+from+{origin}+to+{destination}"

# Routes from Irish airports: {destination: [(airline, airport, start_month, end_month), ...]}
# Months: 1=Jan, 12=Dec. Year-round = (1, 12), Summer only = (4, 10) or (5, 9)
ROUTES = {
    # Spain
    "Barcelona": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 4, 10), ("Ryanair", "Shannon", 4, 10)
    ],
    "Madrid": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Iberia", "Dublin", 1, 12),
        ("Ryanair", "Cork", 4, 10), ("Ryanair", "Shannon", 1, 12)
    ],
    "Malaga": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12), ("Ryanair", "Knock", 5, 9),
        ("Aer Lingus", "Cork", 4, 10), ("Aer Lingus", "Shannon", 4, 10)
    ],
    "Seville": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Cork", 4, 10)],
    "Valencia": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Cork", 4, 10)],
    "Alicante": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 4, 10), ("Ryanair", "Knock", 5, 9),
        ("Ryanair", "Kerry", 5, 9), ("Aer Lingus", "Cork", 4, 10)
    ],
    "Palma Mallorca": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10),
        ("Ryanair", "Cork", 1, 12), ("Aer Lingus", "Cork", 4, 10),
        ("Ryanair", "Shannon", 1, 12), ("Ryanair", "Knock", 4, 10)
    ],
    "Ibiza": [("Ryanair", "Dublin", 5, 9), ("Aer Lingus", "Dublin", 5, 9)],
    "Menorca": [("Ryanair", "Dublin", 5, 9)],
    "Tenerife": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12),
        ("Aer Lingus", "Cork", 1, 12), ("Aer Lingus", "Shannon", 1, 12)
    ],
    "Gran Canaria": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 4, 10)
    ],
    "Lanzarote": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12), ("Ryanair", "Knock", 1, 12),
        ("Aer Lingus", "Cork", 1, 12), ("Aer Lingus", "Shannon", 1, 12)
    ],
    "Fuerteventura": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 4, 10)
    ],
    "Bilbao": [("Aer Lingus", "Dublin", 1, 12), ("Aer Lingus", "Cork", 1, 12)],
    "Santiago de Compostela": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Shannon", 5, 9), ("Aer Lingus", "Cork", 6, 10)],
    "Girona": [("Ryanair", "Dublin", 4, 10), ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 4, 10), ("Ryanair", "Knock", 5, 9)],
    "Reus": [("Ryanair", "Dublin", 4, 10), ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 4, 10)],
    "Murcia": [("Ryanair", "Dublin", 1, 12)],
    "Almeria": [],  # Ryanair DUB route discontinued
    "Jerez": [],  # Ryanair closed Jerez base, route ended 2025
    "Santander": [("Ryanair", "Dublin", 1, 12)],
    "Asturias": [],  # Ryanair ended all flights to Asturias
    "Zaragoza": [],  # No direct Dublin service
    "Granada": [("Ryanair", "Dublin", 5, 9)],
    "A Coruna": [],  # No direct Dublin service
    "Vigo": [],  # Ryanair suspended all Vigo flights Jan 2026
    # Portugal
    "Lisbon": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("TAP", "Dublin", 1, 12),
        ("Ryanair", "Cork", 4, 10), ("Ryanair", "Shannon", 4, 10)
    ],
    "Porto": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Cork", 4, 10), ("Ryanair", "Shannon", 4, 10)],
    "Faro": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 4, 10), ("Ryanair", "Knock", 5, 9),
        ("Ryanair", "Kerry", 5, 9), ("Aer Lingus", "Cork", 4, 10), ("Aer Lingus", "Shannon", 4, 10)
    ],
    "Funchal": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Shannon", 4, 10)],
    "Ponta Delgada": [],  # Ryanair discontinued all Azores routes March 2026
    # Italy
    "Rome": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 4, 10), ("Ryanair", "Shannon", 1, 12)
    ],
    "Milan": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 4, 10), ("Ryanair", "Knock", 4, 10)
    ],
    "Venice": [("Ryanair", "Dublin", 4, 10), ("Ryanair", "Cork", 1, 12)],
    "Naples": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Shannon", 4, 10)],
    "Pisa": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10), ("Ryanair", "Cork", 1, 12)],
    "Bologna": [("Ryanair", "Dublin", 1, 12)],
    "Turin": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Shannon", 1, 12)],
    "Bari": [("Ryanair", "Dublin", 4, 10)],
    "Verona": [("Ryanair", "Dublin", 4, 10)],
    # Sardinia
    "Cagliari": [("Ryanair", "Dublin", 4, 10)],

    "Alghero": [("Ryanair", "Dublin", 5, 9), ("Ryanair", "Cork", 5, 9)],
    # Sicily
    "Palermo": [("Ryanair", "Dublin", 1, 12)],
    "Catania": [("Ryanair", "Dublin", 1, 12)],
    # Greece
    "Athens": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10)],
    "Santorini": [("Ryanair", "Dublin", 5, 9)],
    "Heraklion": [("Aer Lingus", "Dublin", 5, 10), ("Aer Lingus", "Cork", 6, 9)],
    "Chania": [("Ryanair", "Dublin", 5, 9)],
    "Kos": [("Ryanair", "Dublin", 5, 9)],
    "Rhodes": [("Ryanair", "Dublin", 5, 9), ("Ryanair", "Cork", 5, 10)],
    "Corfu": [("Ryanair", "Dublin", 4, 10), ("Ryanair", "Shannon", 6, 10)],
    "Zakynthos": [("Ryanair", "Dublin", 5, 9)],
    "Kefalonia": [("Ryanair", "Dublin", 5, 9)],
    "Mykonos": [("Ryanair", "Dublin", 5, 9)],
    "Preveza": [("Ryanair", "Dublin", 5, 9)],
    "Skiathos": [("Ryanair", "Dublin", 5, 9)],
    "Kalamata": [("Ryanair", "Dublin", 5, 9)],
    "Thessaloniki": [("Ryanair", "Dublin", 3, 10)],
    # Croatia
    "Split": [("Ryanair", "Dublin", 4, 10), ("Aer Lingus", "Dublin", 5, 9)],
    "Dubrovnik": [("Ryanair", "Dublin", 4, 10), ("Aer Lingus", "Dublin", 5, 9)],
    "Zagreb": [("Ryanair", "Dublin", 1, 12)],
    "Zadar": [("Ryanair", "Dublin", 5, 9), ("Ryanair", "Cork", 5, 9)],
    "Pula": [("Ryanair", "Dublin", 5, 9)],
    # Montenegro
    "Podgorica": [("Ryanair", "Dublin", 5, 9)],
    "Tivat": [("Ryanair", "Dublin", 5, 9)],
    # Cyprus
    "Paphos": [("Ryanair", "Dublin", 1, 12)],
    "Larnaca": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10)],
    # Turkey
    "Antalya": [("Ryanair", "Dublin", 5, 10), ("Aer Lingus", "Dublin", 5, 10)],
    "Dalaman": [("Ryanair", "Dublin", 5, 10), ("Aer Lingus", "Dublin", 5, 10)],
    "Bodrum": [("Ryanair", "Dublin", 4, 10)],
    "Istanbul": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12)],
    # France
    "Nice": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10), ("Aer Lingus", "Cork", 5, 9)],
    "Marseille": [("Ryanair", "Dublin", 5, 10)],
    "Paris": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Air France", "Dublin", 1, 12),
        ("Aer Lingus", "Cork", 1, 12), ("Aer Lingus", "Shannon", 1, 12)
    ],
    "Bordeaux": [("Aer Lingus", "Dublin", 5, 10), ("Ryanair", "Cork", 5, 9), ("Aer Lingus", "Cork", 5, 9)],
    "Toulouse": [("Ryanair", "Dublin", 1, 12)],
    "Lyon": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Cork", 1, 12)],
    "Nantes": [("Ryanair", "Dublin", 1, 12)],
    "Montpellier": [("Ryanair", "Dublin", 5, 9)],
    "Biarritz": [("Ryanair", "Dublin", 5, 9)],
    "Carcassonne": [("Ryanair", "Dublin", 5, 10), ("Ryanair", "Cork", 5, 10)],
    "Beziers": [],  # Ryanair dropped BZR routes S26
    "Bergerac": [("Ryanair", "Dublin", 5, 9)],
    "La Rochelle": [("Ryanair", "Dublin", 5, 9), ("Ryanair", "Cork", 5, 9)],
    "Perpignan": [("Ryanair", "Dublin", 5, 9)],
    "Grenoble": [("Ryanair", "Dublin", 12, 3)],
    # Other Western Europe
    "Amsterdam": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("KLM", "Dublin", 1, 12),
        ("Aer Lingus", "Cork", 1, 12), ("Aer Lingus", "Shannon", 1, 12), ("KLM", "Cork", 1, 12)
    ],
    "Brussels": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Ryanair", "Cork", 4, 10)],
    "Geneva": [("Aer Lingus", "Dublin", 1, 12)],
    "Zurich": [("Aer Lingus", "Dublin", 1, 12), ("Swiss", "Dublin", 1, 12)],
    # Central Europe
    "Budapest": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Shannon", 4, 10)],
    "Prague": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Cork", 1, 12)],
    "Vienna": [("Ryanair", "Dublin", 1, 12)],
    "Bratislava": [("Ryanair", "Dublin", 1, 12)],
    "Ljubljana": [],  # No direct Dublin service (Ryanair negotiations ongoing but no deal)
    # Poland
    "Krakow": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12)],
    "Warsaw": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12)],
    # Nordics
    "Stockholm": [("Ryanair", "Dublin", 1, 12)],
    "Copenhagen": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("SAS", "Dublin", 1, 12)],
    "Oslo": [("Ryanair", "Dublin", 1, 12)],
    "Helsinki": [("Ryanair", "Dublin", 1, 12)],
    # Baltics
    "Riga": [("Ryanair", "Dublin", 1, 12)],
    "Tallinn": [("Ryanair", "Dublin", 1, 12)],
    "Vilnius": [("Ryanair", "Dublin", 1, 12)],
    # Balkans
    "Sofia": [("Ryanair", "Dublin", 1, 12)],
    "Bucharest": [("Ryanair", "Dublin", 1, 12)],
    # Malta
    "Malta": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10), ("Ryanair", "Cork", 4, 10)],
}


def get_available_routes(destination: str, travel_month: int) -> list:
    """Filter routes to only include those operating in the given month."""
    all_routes = ROUTES.get(destination, [])
    available = []
    for route in all_routes:
        airline, airport, start_month, end_month = route
        # Handle wrap-around (e.g., Nov-Feb would be 11, 2)
        if start_month <= end_month:
            if start_month <= travel_month <= end_month:
                available.append((airline, airport))
        else:
            # Wrap around case (e.g., 11 to 2 means Nov, Dec, Jan, Feb)
            if travel_month >= start_month or travel_month <= end_month:
                available.append((airline, airport))
    return available

# Good weather codes (sunny/clear only - no partly cloudy)
GOOD_WEATHER_CODES = {0, 1}

# Rain codes - exclude destinations with any of these
RAIN_CODES = {51, 53, 55, 61, 63, 65, 80, 81, 82, 95}

# Minimum temperature for "good weather"
MIN_TEMP = 22.0

# Minimum sunny days required
MIN_SUNNY_DAYS = 5

# Minimum warm days required (days above MIN_TEMP)
MIN_WARM_DAYS = 5


def get_weather_forecast(lat: float, lon: float) -> Optional[Dict]:
    """Fetch 10-day weather forecast from Open-Meteo API, starting 4 days from now."""
    url = "https://api.open-meteo.com/v1/forecast"

    # Start 4 days from now, get 10 days of forecast
    start_date = datetime.now() + timedelta(days=FORECAST_START_OFFSET)
    end_date = start_date + timedelta(days=9)

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,weather_code",
        "timezone": "auto",
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  Error fetching weather: {e}")
        return None


def check_destination(destination: Dict) -> Optional[Dict]:
    """Check if a destination has good weather, finding best 7-day window in 10-day forecast."""
    forecast = get_weather_forecast(destination["lat"], destination["lon"])

    if not forecast or "daily" not in forecast:
        return None

    daily = forecast["daily"]
    dates = daily.get("time", [])
    temps = daily.get("temperature_2m_max", [])
    codes = daily.get("weather_code", [])

    # Build list of all days with weather info
    all_forecast_days = []
    for date, temp, code in zip(dates, temps, codes):
        weather_info = WEATHER_CODES.get(code, {"desc": "Unknown", "icon": "❓"})
        is_sunny = code in GOOD_WEATHER_CODES
        is_warm = temp is not None and temp > MIN_TEMP
        day_info = {
            "date": date,
            "temp": temp,
            "code": code,
            "description": weather_info["desc"],
            "icon": weather_info["icon"],
            "is_good": is_warm and is_sunny,
        }
        all_forecast_days.append(day_info)

    # Find the best 7-day window within the 10 days
    best_window = None
    best_score = (-1, -1)  # (sunny_days, avg_temp)

    for start_idx in range(len(all_forecast_days) - 6):  # 0, 1, 2, 3 for 10 days
        window = all_forecast_days[start_idx:start_idx + 7]

        sunny_count = sum(1 for d in window if d["code"] in GOOD_WEATHER_CODES)
        warm_count = sum(1 for d in window if d["temp"] is not None and d["temp"] > MIN_TEMP)
        avg_temp = sum(d["temp"] for d in window if d["temp"] is not None) / 7

        # Check if window meets minimum criteria
        if sunny_count >= MIN_SUNNY_DAYS and warm_count >= MIN_WARM_DAYS:
            score = (sunny_count, avg_temp)
            if score > best_score:
                best_score = score
                best_window = (start_idx, window)

    if best_window is None:
        return None

    start_idx, all_days = best_window
    good_days = [d for d in all_days if d["is_good"]]

    if good_days:
        # Calculate travel dates based on the best window
        depart_date = datetime.now() + timedelta(days=FORECAST_START_OFFSET + start_idx)
        return_date = depart_date + timedelta(days=7)
        travel_month = depart_date.month

        # Get only routes available for this time period
        available_routes = get_available_routes(destination["city"], travel_month)

        # Skip destinations with no available flights
        if not available_routes:
            return None

        return {
            "city": destination["city"],
            "country": destination["country"],
            "good_days": good_days,
            "all_days": all_days,
            "best_temp": max(day["temp"] for day in good_days),
            "routes": available_routes,
            "depart_date": depart_date.strftime("%Y-%m-%d"),
            "return_date": return_date.strftime("%Y-%m-%d"),
        }

    return None


def format_date_short(date_str: str) -> tuple:
    """Format date string to short format for cards."""
    date = datetime.strptime(date_str, "%Y-%m-%d")
    return date.strftime("%a"), date.strftime("%d")


def generate_html_email(results: List[Dict]) -> str:
    """Generate a nicely formatted HTML email."""
    # Sort all destinations by weather quality: sunny days (desc), then temperature (desc)
    sorted_results = sorted(results, key=lambda x: (len(x["good_days"]), x["best_temp"]), reverse=True)

    # Calculate date range for header (10-day window)
    start_date = datetime.now() + timedelta(days=FORECAST_START_OFFSET)
    end_date = start_date + timedelta(days=9)
    date_range = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"

    html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5;
            color: #1a1a1a;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }
        .header {
            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0 0 8px 0;
            font-size: 28px;
            font-weight: 700;
        }
        .header .subtitle {
            font-size: 16px;
            opacity: 0.95;
            margin: 0;
        }
        .header .date-range {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 8px 20px;
            border-radius: 20px;
            margin-top: 15px;
            font-size: 14px;
            font-weight: 600;
        }
        .content {
            padding: 30px;
        }
        .country-section {
            margin-bottom: 30px;
        }
        .country-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }
        .country-flag {
            font-size: 24px;
            margin-right: 10px;
        }
        .country-name {
            font-size: 20px;
            font-weight: 700;
            color: #333;
        }
        .destination {
            background: #fafafa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #eee;
        }
        .city-row {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .rank {
            font-size: 14px;
            font-weight: 700;
            color: #FF6B35;
            margin-right: 10px;
            min-width: 28px;
        }
        .city-name {
            font-size: 18px;
            font-weight: 600;
            color: #222;
            margin-right: 15px;
        }
        .sunny-badge {
            background: #28a745;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .flights-section {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e0e0e0;
        }
        .flights-label {
            font-size: 11px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }
        .flight-route {
            display: inline-flex;
            align-items: center;
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 10px 14px;
            margin: 4px 6px 4px 0;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        .flight-route:hover {
            border-color: #007bff;
            background: #f0f7ff;
        }
        .airline-logo {
            width: 28px;
            height: 28px;
            margin-right: 10px;
            border-radius: 4px;
        }
        .route-info {
            display: flex;
            flex-direction: column;
        }
        .airline-name {
            font-size: 12px;
            font-weight: 600;
            color: #333;
        }
        .airport-name {
            font-size: 11px;
            color: #666;
        }
        .skyscanner-section {
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px dashed #ddd;
            display: flex;
            flex-wrap: wrap;
            align-items: stretch;
            gap: 8px;
        }
        .skyscanner-btn, .things-to-do-btn, .airbnb-btn, .booking-btn {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 10px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            color: white !important;
            min-width: 100px;
            max-width: 130px;
            text-align: center;
            box-sizing: border-box;
            line-height: 1.2;
            margin: 4px 10px 4px 0;
        }
        .skyscanner-btn {
            background: #0770e3;
        }
        .skyscanner-btn:hover {
            background: #055bb5;
        }
        .skyscanner-btn img, .airbnb-btn img {
            width: 20px;
            height: 20px;
            margin-right: 8px;
            border-radius: 4px;
        }
        .things-to-do-btn {
            background: #9c27b0;
        }
        .things-to-do-btn:hover {
            background: #7b1fa2;
        }
        .airbnb-btn {
            background: #FF5A5F;
        }
        .airbnb-btn:hover {
            background: #e04950;
        }
        .booking-btn {
            background: #003580;
        }
        .booking-btn:hover {
            background: #00264d;
        }
        .booking-btn img {
            width: 20px;
            height: 20px;
            margin-right: 8px;
            border-radius: 4px;
        }
        .forecast-grid {
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }
        .day-card {
            flex: 1;
            min-width: 70px;
            text-align: center;
            padding: 12px 8px;
            border-radius: 10px;
            background: white;
            border: 1px solid #e0e0e0;
        }
        .day-card.sunny {
            background: linear-gradient(180deg, #FFF9E6 0%, #FFF3CD 100%);
            border: 2px solid #FFD93D;
        }
        .day-name {
            font-size: 11px;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .day-date {
            font-size: 18px;
            font-weight: 700;
            color: #333;
            margin: 2px 0;
        }
        .day-icon {
            font-size: 26px;
            margin: 6px 0;
        }
        .day-temp {
            font-size: 15px;
            font-weight: 700;
        }
        .day-card.sunny .day-temp {
            color: #E65100;
        }
        .day-card:not(.sunny) .day-temp {
            color: #666;
        }
        .day-desc {
            font-size: 9px;
            color: #888;
            margin-top: 4px;
        }
        .footer {
            text-align: center;
            padding: 25px 30px;
            background: #f8f9fa;
            border-top: 1px solid #eee;
        }
        .footer p {
            margin: 5px 0;
            font-size: 12px;
            color: #888;
        }
        .no-rain {
            display: inline-block;
            background: #e8f5e9;
            color: #2e7d32;
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 11px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Your Sunny Escapes</h1>
            <p class="subtitle">Rain-free destinations with direct flights from Ireland</p>
            <div class="date-range">""" + date_range + """</div>
        </div>
        <div class="content">
"""

    # Country flag mapping
    flags = {
        "Spain": "🇪🇸", "Portugal": "🇵🇹", "Italy": "🇮🇹", "Greece": "🇬🇷",
        "Croatia": "🇭🇷", "Cyprus": "🇨🇾", "France": "🇫🇷", "Netherlands": "🇳🇱",
        "Belgium": "🇧🇪", "Switzerland": "🇨🇭", "Hungary": "🇭🇺", "Czech Republic": "🇨🇿",
        "Austria": "🇦🇹", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Poland": "🇵🇱",
        "Sweden": "🇸🇪", "Denmark": "🇩🇰", "Norway": "🇳🇴", "Finland": "🇫🇮",
        "Latvia": "🇱🇻", "Estonia": "🇪🇪", "Lithuania": "🇱🇹", "Bulgaria": "🇧🇬",
        "Romania": "🇷🇴",
        "Turkey": "🇹🇷",
        "Montenegro": "🇲🇪"
    }

    # Add rank counter
    for rank, dest in enumerate(sorted_results, 1):
        num_sunny = len(dest["good_days"])
        flag = flags.get(dest["country"], "🌍")

        html += f"""
            <div class="destination">
                <div class="city-row">
                    <span class="rank">#{rank}</span>
                    <span class="city-name">{flag} {dest["city"]}, {dest["country"]}</span>
                    <span class="sunny-badge">{num_sunny} sunny day{"s" if num_sunny > 1 else ""}</span>
                </div>
                <div class="forecast-grid">
"""
        for day in dest["all_days"]:
            day_name, day_date = format_date_short(day["date"])
            sunny_class = "sunny" if day["is_good"] else ""
            html += f"""
                    <div class="day-card {sunny_class}">
                        <div class="day-name">{day_name}</div>
                        <div class="day-date">{day_date}</div>
                        <div class="day-icon">{day["icon"]}</div>
                        <div class="day-temp">{day["temp"]:.0f}°</div>
                    </div>
"""

        # Add flight routes with airline logos and booking links
        routes_html = ""
        for airline, airport in dest["routes"]:
            logo_url = AIRLINE_LOGOS.get(airline, "")
            booking_url = get_booking_url(airline, airport, dest["city"], dest["depart_date"], dest["return_date"])
            routes_html += f'''
                    <a href="{booking_url}" class="flight-route" target="_blank" style="text-decoration: none;">
                        <img src="{logo_url}" alt="{airline}" class="airline-logo">
                        <div class="route-info">
                            <span class="airline-name">{airline}</span>
                            <span class="airport-name">from {airport}</span>
                        </div>
                    </a>'''

        # Generate Skyscanner link (use Dublin as default origin for the compare button)
        skyscanner_url = get_skyscanner_url("Dublin", dest["city"], dest["depart_date"], dest["return_date"])
        skyscanner_logo = AIRLINE_LOGOS.get("Skyscanner", "")

        # Generate Airbnb link (entire home, 1+ bedroom)
        airbnb_url = f"https://www.airbnb.com/s/{dest['city']}/homes?checkin={dest['depart_date']}&checkout={dest['return_date']}&adults=2&room_types%5B%5D=Entire%20home%2Fapt&min_bedrooms=1"
        airbnb_logo = AIRLINE_LOGOS.get("Airbnb", "")

        # Generate Booking.com link
        booking_url = f"https://www.booking.com/searchresults.html?ss={dest['city']}%2C+{dest['country']}&checkin={dest['depart_date']}&checkout={dest['return_date']}&group_adults=2&no_rooms=1"
        booking_logo = AIRLINE_LOGOS.get("Booking", "")

        # Generate "things to do" search URL
        depart_dt = datetime.strptime(dest["depart_date"], "%Y-%m-%d")
        return_dt = datetime.strptime(dest["return_date"], "%Y-%m-%d")
        date_range_str = f"{depart_dt.strftime('%B %d')} to {return_dt.strftime('%B %d %Y')}"
        things_to_do_query = f"things to do events {dest['city']} {dest['country']} {date_range_str}".replace(" ", "+")
        things_to_do_url = f"https://www.google.com/search?q={things_to_do_query}"

        html += f"""
                </div>
                <div class="flights-section">
                    <div class="flights-label">Fly from Ireland</div>
                    {routes_html}
                    <div class="skyscanner-section">
                        <a href="{skyscanner_url}" class="skyscanner-btn" target="_blank" style="text-decoration: none;">
                            <img src="{skyscanner_logo}" alt="Skyscanner">
                            Compare flights
                        </a>
                        <a href="{airbnb_url}" class="airbnb-btn" target="_blank" style="text-decoration: none;">
                            <img src="{airbnb_logo}" alt="Airbnb">
                            Find stays
                        </a>
                        <a href="{booking_url}" class="booking-btn" target="_blank" style="text-decoration: none;">
                            <img src="{booking_logo}" alt="Booking.com">
                            Hotels
                        </a>
                        <a href="{things_to_do_url}" class="things-to-do-btn" target="_blank" style="text-decoration: none;">
                            🎭 Things to do
                        </a>
                    </div>
                </div>
            </div>
"""

    html += f"""
        </div>
        <div class="footer">
            <p>Generated {datetime.now().strftime("%A, %B %d at %H:%M")}</p>
            <p>Weather data from Open-Meteo API • No rain forecast for any of these destinations</p>
        </div>
    </div>
</body>
</html>
"""

    return html


def send_email(html_content: str, num_destinations: int, subject: str = None) -> bool:
    """Send the email via Gmail SMTP."""
    gmail_address = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    if not all([gmail_address, gmail_password, recipient_email]):
        print("Error: Missing email configuration in .env file")
        print("Required: GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL")
        return False

    # Create message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject if subject else f"☀️ Your sunny escape options this week - {num_destinations} destinations!"
    msg["From"] = gmail_address
    msg["To"] = recipient_email

    # Attach HTML content
    html_part = MIMEText(html_content, "html")
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_address, gmail_password)
            server.sendmail(gmail_address, recipient_email, msg.as_string())
        return True
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")
        return False


def check_destination_unconstrained(destination: Dict) -> Optional[Dict]:
    """Find the best 7-day window for a destination regardless of weather criteria thresholds."""
    forecast = get_weather_forecast(destination["lat"], destination["lon"])
    if not forecast or "daily" not in forecast:
        return None

    daily = forecast["daily"]
    dates = daily.get("time", [])
    temps = daily.get("temperature_2m_max", [])
    codes = daily.get("weather_code", [])

    all_forecast_days = []
    for date, temp, code in zip(dates, temps, codes):
        weather_info = WEATHER_CODES.get(code, {"desc": "Unknown", "icon": "❓"})
        is_sunny = code in GOOD_WEATHER_CODES
        is_warm = temp is not None and temp > MIN_TEMP
        all_forecast_days.append({
            "date": date, "temp": temp, "code": code,
            "description": weather_info["desc"], "icon": weather_info["icon"],
            "is_good": is_warm and is_sunny,
        })

    if len(all_forecast_days) < 7:
        return None

    # Pick best window by (sunny_days, avg_temp), no criteria gate
    best_window = None
    best_score = (-1, -999.0)
    for start_idx in range(len(all_forecast_days) - 6):
        window = all_forecast_days[start_idx:start_idx + 7]
        valid_temps = [d["temp"] for d in window if d["temp"] is not None]
        if not valid_temps:
            continue
        sunny_count = sum(1 for d in window if d["code"] in GOOD_WEATHER_CODES)
        avg_temp = sum(valid_temps) / len(valid_temps)
        score = (sunny_count, avg_temp)
        if score > best_score:
            best_score = score
            best_window = (start_idx, window)

    if best_window is None:
        return None

    start_idx, all_days = best_window
    good_days = [d for d in all_days if d["is_good"]]
    best_temp = max((d["temp"] for d in all_days if d["temp"] is not None), default=0.0)

    depart_date = datetime.now() + timedelta(days=FORECAST_START_OFFSET + start_idx)
    return_date = depart_date + timedelta(days=7)
    available_routes = get_available_routes(destination["city"], depart_date.month)

    return {
        "city": destination["city"],
        "country": destination["country"],
        "good_days": good_days,
        "all_days": all_days,
        "best_temp": best_temp,
        "routes": available_routes,
        "depart_date": depart_date.strftime("%Y-%m-%d"),
        "return_date": return_date.strftime("%Y-%m-%d"),
    }


def generate_html_email_no_match(best: Dict) -> str:
    """Generate the no-match email with the closest destination's full card."""
    flags = {
        "Spain": "🇪🇸", "Portugal": "🇵🇹", "Italy": "🇮🇹", "Greece": "🇬🇷",
        "Croatia": "🇭🇷", "Cyprus": "🇨🇾", "France": "🇫🇷", "Netherlands": "🇳🇱",
        "Belgium": "🇧🇪", "Switzerland": "🇨🇭", "Hungary": "🇭🇺", "Czech Republic": "🇨🇿",
        "Austria": "🇦🇹", "Slovakia": "🇸🇰", "Slovenia": "🇸🇮", "Poland": "🇵🇱",
        "Sweden": "🇸🇪", "Denmark": "🇩🇰", "Norway": "🇳🇴", "Finland": "🇫🇮",
        "Latvia": "🇱🇻", "Estonia": "🇪🇪", "Lithuania": "🇱🇹", "Bulgaria": "🇧🇬",
        "Romania": "🇷🇴", "Turkey": "🇹🇷", "Montenegro": "🇲🇪",
    }
    flag = flags.get(best["country"], "🌍")
    num_sunny = len(best["good_days"])
    sunny_badge = f'{num_sunny} sunny day{"s" if num_sunny != 1 else ""}' if num_sunny else "No sunny days"

    forecast_html = ""
    for day in best["all_days"]:
        day_name, day_date = format_date_short(day["date"])
        sunny_class = "sunny" if day["is_good"] else ""
        forecast_html += f"""
                    <div class="day-card {sunny_class}">
                        <div class="day-name">{day_name}</div>
                        <div class="day-date">{day_date}</div>
                        <div class="day-icon">{day["icon"]}</div>
                        <div class="day-temp">{day["temp"]:.0f}°</div>
                    </div>
"""

    routes_html = ""
    for airline, airport in best["routes"]:
        logo_url = AIRLINE_LOGOS.get(airline, "")
        booking_url = get_booking_url(airline, airport, best["city"], best["depart_date"], best["return_date"])
        routes_html += f'''
                    <a href="{booking_url}" class="flight-route" target="_blank" style="text-decoration: none;">
                        <img src="{logo_url}" alt="{airline}" class="airline-logo">
                        <div class="route-info">
                            <span class="airline-name">{airline}</span>
                            <span class="airport-name">from {airport}</span>
                        </div>
                    </a>'''

    skyscanner_url = get_skyscanner_url("Dublin", best["city"], best["depart_date"], best["return_date"])
    skyscanner_logo = AIRLINE_LOGOS.get("Skyscanner", "")
    airbnb_url = f"https://www.airbnb.com/s/{best['city']}/homes?checkin={best['depart_date']}&checkout={best['return_date']}&adults=2&room_types%5B%5D=Entire%20home%2Fapt&min_bedrooms=1"
    airbnb_logo = AIRLINE_LOGOS.get("Airbnb", "")
    booking_url = f"https://www.booking.com/searchresults.html?ss={best['city']}%2C+{best['country']}&checkin={best['depart_date']}&checkout={best['return_date']}&group_adults=2&no_rooms=1"
    booking_logo = AIRLINE_LOGOS.get("Booking", "")
    depart_dt = datetime.strptime(best["depart_date"], "%Y-%m-%d")
    return_dt = datetime.strptime(best["return_date"], "%Y-%m-%d")
    date_range_str = f"{depart_dt.strftime('%B %d')} to {return_dt.strftime('%B %d %Y')}"
    things_to_do_query = f"things to do events {best['city']} {best['country']} {date_range_str}".replace(" ", "+")
    things_to_do_url = f"https://www.google.com/search?q={things_to_do_query}"

    return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.5; color: #1a1a1a; background-color: #f5f5f5; margin: 0; padding: 20px;
        }}
        .container {{
            max-width: 700px; margin: 0 auto; background: white; border-radius: 16px;
            overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .header {{
            background: linear-gradient(135deg, #607d8b 0%, #90a4ae 100%);
            color: white; padding: 40px 30px; text-align: center;
        }}
        .header h1 {{ margin: 0 0 8px 0; font-size: 28px; font-weight: 700; }}
        .header .subtitle {{ font-size: 16px; opacity: 0.95; margin: 0; }}
        .content {{ padding: 30px; }}
        .destination {{
            background: #fafafa; border-radius: 12px; padding: 20px;
            margin-bottom: 15px; border: 1px solid #eee;
        }}
        .city-row {{ display: flex; align-items: center; margin-bottom: 15px; }}
        .city-name {{ font-size: 18px; font-weight: 600; color: #222; margin-right: 15px; }}
        .sunny-badge {{
            background: #607d8b; color: white; padding: 4px 12px;
            border-radius: 12px; font-size: 12px; font-weight: 600;
        }}
        .flights-section {{ margin-top: 15px; padding-top: 15px; border-top: 1px solid #e0e0e0; }}
        .flights-label {{
            font-size: 11px; color: #666; text-transform: uppercase;
            letter-spacing: 0.5px; margin-bottom: 10px;
        }}
        .flight-route {{
            display: inline-flex; align-items: center; background: #ffffff;
            border: 1px solid #e0e0e0; border-radius: 8px; padding: 10px 14px;
            margin: 4px 6px 4px 0; cursor: pointer;
        }}
        .airline-logo {{ width: 28px; height: 28px; margin-right: 10px; border-radius: 4px; }}
        .route-info {{ display: flex; flex-direction: column; }}
        .airline-name {{ font-size: 12px; font-weight: 600; color: #333; }}
        .airport-name {{ font-size: 11px; color: #666; }}
        .skyscanner-section {{
            margin-top: 12px; padding-top: 12px; border-top: 1px dashed #ddd;
            display: flex; flex-wrap: wrap; align-items: stretch; gap: 8px;
        }}
        .skyscanner-btn, .things-to-do-btn, .airbnb-btn, .booking-btn {{
            display: inline-flex; align-items: center; justify-content: center;
            padding: 10px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;
            color: white !important; min-width: 100px; max-width: 130px;
            text-align: center; box-sizing: border-box; line-height: 1.2; margin: 4px 10px 4px 0;
        }}
        .skyscanner-btn {{ background: #0770e3; }}
        .skyscanner-btn img, .airbnb-btn img {{ width: 20px; height: 20px; margin-right: 8px; border-radius: 4px; }}
        .things-to-do-btn {{ background: #9c27b0; }}
        .airbnb-btn {{ background: #FF5A5F; }}
        .booking-btn {{ background: #003580; }}
        .booking-btn img {{ width: 20px; height: 20px; margin-right: 8px; border-radius: 4px; }}
        .forecast-grid {{ display: flex; gap: 8px; overflow-x: auto; }}
        .day-card {{
            flex: 1; min-width: 70px; text-align: center; padding: 12px 8px;
            border-radius: 10px; background: white; border: 1px solid #e0e0e0;
        }}
        .day-card.sunny {{
            background: linear-gradient(180deg, #FFF9E6 0%, #FFF3CD 100%);
            border: 2px solid #FFD93D;
        }}
        .day-name {{ font-size: 11px; font-weight: 600; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }}
        .day-date {{ font-size: 18px; font-weight: 700; color: #333; margin: 2px 0; }}
        .day-icon {{ font-size: 26px; margin: 6px 0; }}
        .day-temp {{ font-size: 15px; font-weight: 700; }}
        .day-card.sunny .day-temp {{ color: #E65100; }}
        .day-card:not(.sunny) .day-temp {{ color: #666; }}
        .footer {{
            text-align: center; padding: 25px 30px;
            background: #f8f9fa; border-top: 1px solid #eee;
        }}
        .footer p {{ margin: 5px 0; font-size: 12px; color: #888; }}
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>Nowhere sunny enough today</h1>
        <p class="subtitle">Closest destination — doesn't quite meet the criteria</p>
    </div>
    <div class="content">
        <div class="destination">
            <div class="city-row">
                <span class="city-name">{flag} {best["city"]}, {best["country"]}</span>
                <span class="sunny-badge">{sunny_badge}</span>
            </div>
            <div class="forecast-grid">
{forecast_html}
            </div>
            <div class="flights-section">
                <div class="flights-label">Fly from Ireland</div>
                {routes_html}
                <div class="skyscanner-section">
                    <a href="{skyscanner_url}" class="skyscanner-btn" target="_blank" style="text-decoration: none;">
                        <img src="{skyscanner_logo}" alt="Skyscanner">Compare flights
                    </a>
                    <a href="{airbnb_url}" class="airbnb-btn" target="_blank" style="text-decoration: none;">
                        <img src="{airbnb_logo}" alt="Airbnb">Find stays
                    </a>
                    <a href="{booking_url}" class="booking-btn" target="_blank" style="text-decoration: none;">
                        <img src="{booking_logo}" alt="Booking.com">Hotels
                    </a>
                    <a href="{things_to_do_url}" class="things-to-do-btn" target="_blank" style="text-decoration: none;">
                        🎭 Things to do
                    </a>
                </div>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>Generated {datetime.now().strftime("%A, %B %d at %H:%M")}</p>
        <p>Weather data from Open-Meteo API</p>
    </div>
</div>
</body>
</html>
"""


def print_summary(results: List[Dict]) -> None:
    """Print a summary to the terminal."""
    print("\n" + "=" * 60)
    print("  WEATHER ALERT SUMMARY")
    print("=" * 60)

    if not results:
        print("\nNo destinations found with good weather criteria.")
        print(f"(Looking for: temp > {MIN_TEMP}°C AND clear/sunny skies)")
        return

    print(f"\nFound {len(results)} destinations with good weather!\n")

    # Group by country
    by_country = defaultdict(list)
    for result in results:
        by_country[result["country"]].append(result)

    for country in sorted(by_country.keys()):
        print(f"  {country}:")
        for dest in sorted(by_country[country], key=lambda x: x["best_temp"], reverse=True):
            num_days = len(dest["good_days"])
            print(f"    - {dest['city']}: {dest['best_temp']:.1f}°C ({num_days} good day{'s' if num_days > 1 else ''})")

    print("\n" + "=" * 60)


def main():
    """Main function to check weather and send alerts."""
    print("\nWeather Alert - Checking destinations...")
    print("-" * 40)

    results = []
    best_raw = None  # best destination regardless of criteria

    for dest in DESTINATIONS:
        print(f"Checking {dest['city']}, {dest['country']}...", end=" ")
        result = check_destination(dest)

        if result:
            print(f"GOOD ({result['best_temp']:.1f}°C)")
            results.append(result)
            if best_raw is None or result["best_temp"] > best_raw["best_temp"]:
                best_raw = result
        else:
            print("no match")
            raw = check_destination_unconstrained(dest)
            if raw and (best_raw is None or raw["best_temp"] > best_raw["best_temp"]):
                best_raw = raw

    # Print summary
    print_summary(results)

    # Send email
    if results:
        print("\nSending email alert...")
        html = generate_html_email(results)
        if send_email(html, len(results)):
            print("Email sent successfully!")
        else:
            print("Failed to send email. Check your .env configuration.")
    elif best_raw:
        print("\nSending no-match email alert...")
        html = generate_html_email_no_match(best_raw)
        if send_email(html, 0, subject="Nowhere sunny enough today"):
            print("No-match email sent successfully!")
        else:
            print("Failed to send email. Check your .env configuration.")
    else:
        print("\nNo email sent (no weather data available).")

    print()


if __name__ == "__main__":
    main()
