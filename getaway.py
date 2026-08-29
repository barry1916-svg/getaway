#!/usr/bin/env python3
"""
Weather Alert App - Check sunny destinations with direct flights from Ireland
"""

import requests
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Optional, List, Dict

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
    "Rome": "CIA",  # Ryanair uses Ciampino; Aer Lingus uses FCO but its booking link doesn't use IATA
    "Milan": "MXP", "Venice": "VCE", "Naples": "NAP",
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
    "Copenhagen": "CPH", "Riga": "RIX",
    "Tallinn": "TLL", "Vilnius": "VNO", "Sofia": "SOF", "Bucharest": "OTP",
    # Malta
    "Malta": "MLA",
}


def get_booking_url(airline: str, origin: str, destination: str, depart_date: str, return_date: str) -> str:
    """Generate a pre-populated booking URL for the airline."""
    origin_code = IRISH_AIRPORTS.get(origin, "DUB")
    dest_code = DESTINATION_AIRPORTS.get(destination, "")

    if airline == "Ryanair":
        return f"https://www.ryanair.com/gb/en/trip/flights/select?adults=1&teens=0&children=0&infants=0&dateOut={depart_date}&dateIn={return_date}&isReturn=true&discount=0&promoCode=&isConnectedFlight=false&originIata={origin_code}&destinationIata={dest_code}"

    elif airline == "Aer Lingus":
        return (
            f"https://www.aerlingus.com/app/make/flight-search-result"
            f"?departureDate_0={depart_date}&destinationAirportCode_0={dest_code}&sourceAirportCode_0={origin_code}"
            f"&departureDate_1={return_date}&destinationAirportCode_1={origin_code}&sourceAirportCode_1={dest_code}"
            f"&fareCategory=ECONOMY&fareType=RETURN&groupBooking=false&promoCode=&numAdults=1&numChildren=0&numInfants=0&numYoungAdults=0"
        )

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

    elif airline == "Turkish Airlines":
        return f"https://www.google.com/travel/flights?q=Turkish+Airlines+{origin}+to+{destination}+{depart_date}"

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
        ("Ryanair", "Shannon", 1, 12)
    ],
    "Malaga": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12), ("Ryanair", "Knock", 5, 9),
        ("Aer Lingus", "Cork", 4, 10), ("Aer Lingus", "Shannon", 4, 10)
    ],
    "Seville": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Ryanair", "Cork", 4, 10)],
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
    "Ibiza": [("Ryanair", "Dublin", 5, 9)],  # Aer Lingus route not currently bookable (Aug 2026)
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
    "Bilbao": [("Aer Lingus", "Dublin", 4, 10), ("Aer Lingus", "Cork", 4, 10)],
    "Santiago de Compostela": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 5, 10), ("Ryanair", "Shannon", 5, 9), ("Aer Lingus", "Cork", 6, 10)],
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
    "Funchal": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Shannon", 4, 10)],  # Aer Lingus route not currently bookable (Aug 2026)
    "Ponta Delgada": [],  # Ryanair discontinued all Azores routes March 2026
    # Italy
    "Rome": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Shannon", 1, 12)  # Shannon → Ciampino (CIA)
    ],
    "Milan": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12),
        ("Ryanair", "Cork", 4, 10), ("Ryanair", "Knock", 4, 10)
    ],
    "Venice": [("Ryanair", "Dublin", 4, 10), ("Aer Lingus", "Dublin", 4, 10), ("Ryanair", "Cork", 1, 12)],
    "Naples": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10), ("Ryanair", "Shannon", 4, 10)],
    "Pisa": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10), ("Ryanair", "Cork", 1, 12)],
    "Bologna": [("Ryanair", "Dublin", 1, 12)],
    "Turin": [("Ryanair", "Dublin", 1, 12)],
    "Bari": [("Ryanair", "Dublin", 4, 10)],
    "Verona": [("Ryanair", "Dublin", 4, 10)],
    # Sardinia
    "Cagliari": [("Ryanair", "Dublin", 4, 10)],

    "Alghero": [("Ryanair", "Dublin", 5, 9), ("Ryanair", "Cork", 5, 9)],
    # Sicily
    "Palermo": [("Ryanair", "Dublin", 1, 12)],
    "Catania": [("Ryanair", "Dublin", 4, 10), ("Aer Lingus", "Dublin", 4, 10)],
    # Greece
    "Athens": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12)],
    "Santorini": [("Ryanair", "Dublin", 5, 9), ("Aer Lingus", "Dublin", 5, 9)],
    "Heraklion": [("Aer Lingus", "Dublin", 5, 10), ("Aer Lingus", "Cork", 6, 9)],
    "Chania": [("Ryanair", "Dublin", 5, 9)],
    "Kos": [("Ryanair", "Dublin", 5, 9)],
    "Rhodes": [("Ryanair", "Dublin", 5, 9), ("Ryanair", "Cork", 5, 10)],  # Aer Lingus route not currently bookable (Aug 2026)
    "Corfu": [("Ryanair", "Dublin", 4, 10), ("Aer Lingus", "Dublin", 5, 9), ("Ryanair", "Shannon", 6, 10)],
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
    "Larnaca": [("Ryanair", "Dublin", 1, 12)],
    # Turkey
    "Antalya": [("Ryanair", "Dublin", 5, 10)],  # Aer Lingus route not currently bookable (Aug 2026)
    "Dalaman": [("Ryanair", "Dublin", 5, 10)],  # Aer Lingus route not currently bookable (Aug 2026)
    "Bodrum": [("Ryanair", "Dublin", 4, 10)],
    "Istanbul": [("Turkish Airlines", "Dublin", 1, 12)],
    # France
    "Nice": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Aer Lingus", "Cork", 5, 9)],
    "Marseille": [("Ryanair", "Dublin", 5, 10)],
    "Paris": [
        ("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Air France", "Dublin", 1, 12),
        ("Aer Lingus", "Cork", 1, 12), ("Aer Lingus", "Shannon", 1, 12)
    ],
    "Bordeaux": [("Aer Lingus", "Dublin", 5, 10), ("Aer Lingus", "Cork", 5, 9)],  # Ryanair Cork route not currently bookable (Aug 2026)
    "Toulouse": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 4, 10)],
    "Lyon": [("Aer Lingus", "Dublin", 1, 12)],  # Ryanair route not currently bookable (Aug 2026)
    "Nantes": [("Ryanair", "Dublin", 1, 12)],
    "Montpellier": [],  # Neither Ryanair nor Aer Lingus route currently bookable (Aug 2026)
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
    "Budapest": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Ryanair", "Shannon", 4, 10)],
    "Prague": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Aer Lingus", "Cork", 1, 12)],
    "Vienna": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12)],
    "Bratislava": [("Ryanair", "Dublin", 1, 12)],
    "Ljubljana": [],  # No direct Dublin service (Ryanair negotiations ongoing but no deal)
    # Poland
    "Krakow": [("Ryanair", "Dublin", 1, 12), ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12)],
    "Warsaw": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Ryanair", "Cork", 1, 12), ("Ryanair", "Shannon", 1, 12)],
    # Nordics
    "Stockholm": [("Ryanair", "Dublin", 1, 12)],
    "Copenhagen": [("Ryanair", "Dublin", 1, 12), ("SAS", "Dublin", 1, 12)],  # Aer Lingus route not currently bookable (Aug 2026)
    # Baltics
    "Riga": [("Ryanair", "Dublin", 1, 12)],
    "Tallinn": [("Ryanair", "Dublin", 1, 12)],
    "Vilnius": [("Ryanair", "Dublin", 1, 12)],
    # Balkans
    "Sofia": [("Ryanair", "Dublin", 1, 12)],
    "Bucharest": [("Ryanair", "Dublin", 1, 12)],
    # Malta
    "Malta": [("Ryanair", "Dublin", 1, 12), ("Aer Lingus", "Dublin", 1, 12), ("Ryanair", "Cork", 4, 10)],
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
MIN_SUNNY_DAYS = 4

# Minimum warm days required (days above MIN_TEMP)
MIN_WARM_DAYS = 4


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


def get_weather_forecasts_bulk(destinations: list, batch_size: int = 30) -> list:
    """Fetch forecasts in batches to avoid rate limiting and URL length limits.

    Returns a list of forecast dicts (or None entries for failed fetches)
    aligned 1-to-1 with the input destinations list.
    """
    start_date = datetime.now() + timedelta(days=FORECAST_START_OFFSET)
    end_date = start_date + timedelta(days=9)
    url = "https://api.open-meteo.com/v1/forecast"

    all_forecasts = []
    for i in range(0, len(destinations), batch_size):
        batch = destinations[i:i + batch_size]
        params = {
            "latitude": ",".join(str(d["lat"]) for d in batch),
            "longitude": ",".join(str(d["lon"]) for d in batch),
            "daily": "temperature_2m_max,weather_code",
            "timezone": "UTC",
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                all_forecasts.extend(data)
            elif isinstance(data, dict) and "daily" in data:
                # Single-location response (batch of 1)
                all_forecasts.append(data)
            else:
                print(f"  Unexpected bulk response for batch {i}: {data}")
                all_forecasts.extend([None] * len(batch))
        except requests.RequestException as e:
            print(f"  Bulk weather fetch error batch {i}: {e}")
            all_forecasts.extend([None] * len(batch))

    return all_forecasts


def check_destination_unconstrained(destination: Dict) -> Optional[Dict]:
    """Find the best 7-day window for a destination regardless of weather criteria thresholds."""
    forecast = get_weather_forecast(destination["lat"], destination["lon"])
    return check_destination_from_forecast(destination, forecast)


def check_destination_from_forecast(destination: Dict, forecast: Optional[Dict]) -> Optional[Dict]:
    """Process a pre-fetched forecast for a destination (avoids redundant API calls)."""
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


