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

### Step 3 — Done
The web dashboard works without any environment variables. Railway detects the `Procfile` automatically and starts the app. Once the deployment turns green, click the generated URL to open your dashboard.

Every time you push to GitHub, Railway automatically redeploys.

---

## How it works

- Fetches a 10-day forecast from Open-Meteo for each destination
- Finds the best 7-day window with ≥ 5 sunny days above 22°C
- Filters to destinations with direct flights from Ireland this month
- Sorts results hottest-first and renders the dashboard

---

## Route link auditing

`scripts/audit_links.py` checks every (airline, destination) pair in `getaway.py`'s `ROUTES` table for a genuinely bookable flight, using a headless browser (these airline sites are JS-rendered SPAs, so a plain HTTP fetch can't see a client-side error). It runs daily via a scheduled cloud agent.

Because these sites' anti-bot protection can punish automated traffic (a route confirmed working by hand can still come back as a false positive under repeated automated checks), the script never treats a single BROKEN result as final — it only flags a route as `confirmed_broken`, safe to act on, after seeing it BROKEN on two runs in a row (state tracked in `scripts/audit_state.json`, which is committed so the count survives across runs). SAS is skipped (Cloudflare bot-check), and Air France/KLM/Swiss are checked but only ever reported as low-confidence — no established failure signature yet, so they're never auto-fixed.

Run it manually with:
```bash
pip install playwright && playwright install --with-deps chromium
python3 scripts/audit_links.py
```

---

## Tech stack

- **Python 3.12** + Flask
- **Open-Meteo API** — free weather forecasts, no key needed
- **Gunicorn** — WSGI server for production
- **Railway** — recommended hosting
