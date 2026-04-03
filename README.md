# ☀️ Getaway

A live web dashboard showing sunny European destinations reachable by direct flight from Ireland. Destinations are sorted hottest-first, each showing a 7-day forecast, travel dates, and available airlines.

Weather data is fetched from [Open-Meteo](https://open-meteo.com/) (free, no API key needed). Results are cached for 1 hour.

---

## Running locally

```bash
# 1. Clone the repo
git clone https://github.com/barry1916-svg/getaway.git
cd getaway

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
python app.py
```

Open [http://localhost:5000](http://localhost:5000). The first load checks weather for all active destinations and takes about a minute. Subsequent loads within the hour are instant.

---

## Deploying on Railway

Railway runs the app as a persistent server, so the 1-hour cache works perfectly.

### Step 1 — Sign up
Go to [railway.app](https://railway.app) and sign up with your GitHub account.

### Step 2 — New project
Click **New Project** → **Deploy from GitHub repo** → select **barry1916-svg/getaway**.

### Step 3 — Environment variables (optional)
The web dashboard works without any environment variables. They are only needed if you also want email alerts.

In your Railway project, click the service → **Variables** → **New Variable**:

| Name | Value |
|------|-------|
| `GMAIL_ADDRESS` | your Gmail address |
| `GMAIL_APP_PASSWORD` | your Gmail App Password |
| `RECIPIENT_EMAIL` | where to send alerts |

### Step 4 — Done
Railway detects the `Procfile` automatically and starts the app. Once the deployment turns green, click the generated URL to open your dashboard.

Every time you push to GitHub, Railway automatically redeploys.

---

## Email alerts (GitHub Actions)

The project also sends a daily weather email at 07:00 and 19:00 UTC. This runs via GitHub Actions — no server required.

To enable it, add the three secrets above to your GitHub repo under **Settings → Secrets and variables → Actions**.

---

## How it works

- Fetches a 10-day forecast from Open-Meteo for each destination
- Finds the best 7-day window with ≥ 5 sunny days above 22°C
- Filters to destinations with direct flights from Ireland this month
- Sorts results hottest-first and renders the dashboard

---

## Tech stack

- **Python 3.12** + Flask
- **Open-Meteo API** — free weather forecasts, no key needed
- **Gunicorn** — WSGI server for production
- **GitHub Actions** — scheduled email alerts
- **Railway** — recommended hosting
