# Getaway App - Plan & Summary

## Overview

A Python app that sends daily email alerts about sunny European destinations with direct flights from Ireland. It checks weather forecasts, finds the best travel windows, and provides booking links for flights and accommodation.

---

## How It Works

1. **Fetches 10-day weather forecasts** starting 3 days from today (Open-Meteo API)
2. **Finds the best 7-day window** within those 10 days for each destination
3. **Filters destinations** that meet the weather criteria
4. **Checks flight availability** based on seasonal routes
5. **Sends HTML email** with ranked results and booking links

---

## Weather Criteria

A destination qualifies if the best 7-day window has:
- **3+ sunny days** (WMO codes 0 = Clear sky, 1 = Mainly clear)
- **4+ warm days** (temperature > 21°C)
- **No rain** in the forecast

Destinations are ranked by:
1. Number of sunny days (descending)
2. Average temperature (descending)

---

## Destinations (106 total)

| Country | Destinations |
|---------|-------------|
| **Spain (26)** | Barcelona, Madrid, Malaga, Seville, Valencia, Alicante, Palma Mallorca, Ibiza, Menorca, Tenerife, Gran Canaria, Lanzarote, Fuerteventura, Bilbao, Santiago de Compostela, Girona, Reus, Murcia, Almeria, Jerez, Santander, Asturias, Zaragoza, Granada, A Coruna, Vigo |
| **Portugal (5)** | Lisbon, Porto, Faro, Funchal (Madeira), Ponta Delgada (Azores) |
| **Italy (15)** | Rome, Milan, Venice, Naples, Pisa, Bologna, Turin, Bari, Verona, Cagliari, Olbia, Alghero (Sardinia), Palermo, Catania (Sicily) |
| **Greece (14)** | Athens, Santorini, Heraklion, Chania, Kos, Rhodes, Corfu, Zakynthos, Kefalonia, Mykonos, Preveza, Skiathos, Kalamata, Thessaloniki |
| **Croatia (5)** | Split, Dubrovnik, Zagreb, Zadar, Pula |
| **Montenegro (2)** | Podgorica, Tivat |
| **France (14)** | Nice, Marseille, Paris, Bordeaux, Toulouse, Lyon, Nantes, Montpellier, Biarritz, Carcassonne, Bergerac, La Rochelle, Perpignan, Grenoble |
| **Turkey (4)** | Antalya, Dalaman, Bodrum, Istanbul |
| **Cyprus (2)** | Paphos, Larnaca |
| **Other (19)** | Amsterdam, Brussels, Geneva, Zurich, Budapest, Prague, Vienna, Bratislava, Ljubljana, Krakow, Warsaw, Stockholm, Copenhagen, Oslo, Helsinki, Riga, Tallinn, Vilnius, Sofia, Bucharest |

---

## Irish Departure Airports

- Dublin (DUB)
- Cork (ORK)
- Shannon (SNN)
- Knock (NOC)
- Kerry (KIR)

---

## Airlines

- Ryanair (most routes)
- Aer Lingus
- Iberia
- TAP Portugal
- Air France
- KLM
- Swiss
- SAS

Routes are filtered by **seasonal availability** (e.g., Greek islands May-September only).

---

## Email Features

Each destination card includes:

### Weather Display
- 7-day forecast with temperature and weather icons
- Sunny days highlighted in yellow
- Green badge showing number of sunny days

### Booking Buttons
| Button | Color | Links To |
|--------|-------|----------|
| Compare flights | Blue | Skyscanner (direct flights, dates pre-filled) |
| Find stays | Coral | Airbnb (entire home, 1+ bedroom, dates pre-filled) |
| Hotels | Dark Blue | Booking.com (dates pre-filled) |
| Things to do | Purple | Google search for events during travel dates |

### Flight Routes
- Shows all available airlines with logos
- Links to airline booking pages (Ryanair pre-populated, others to homepage)

---

## Configuration

### Environment Variables (.env)
```
GMAIL_ADDRESS=your@gmail.com
GMAIL_APP_PASSWORD=your-16-char-app-password
RECIPIENT_EMAIL=recipient@email.com
```

### Key Constants (in getaway.py)
```python
FORECAST_START_OFFSET = 3   # Days ahead to start forecast
MIN_TEMP = 21.0             # Minimum temperature (°C)
MIN_SUNNY_DAYS = 3          # Minimum sunny days required
MIN_WARM_DAYS = 4           # Minimum warm days required
GOOD_WEATHER_CODES = {0, 1} # Clear sky, Mainly clear
```

---

## Running the App

### Ad-hoc
```bash
python3 /Users/barry/flight-alert/getaway.py
```

### Daily (cron job at 7 AM)
```
0 7 * * * cd /Users/barry/flight-alert && /usr/bin/python3 getaway.py >> /tmp/getaway.log 2>&1
```

---

## Dependencies

```
requests>=2.28.0
python-dotenv>=1.0.0
```

---

## APIs Used

- **Open-Meteo** (free, no API key): Weather forecasts
- **Google Favicon Service**: Airline/service logos

---

## Future Enhancements (Not Implemented)

- Flight prices (requires paid API)
- Weekend-aligned trip windows
- Shorter trip options (3-5 days)
- Wind speed for beach destinations
- SMS/push notifications
