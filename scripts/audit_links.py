#!/usr/bin/env python3
"""
Check every (airline, destination) pair in getaway.py's ROUTES table for a
genuinely bookable flight, using a headless browser -- these airline sites
are JS-rendered SPAs, so a plain HTTP fetch can't see a client-side error
modal or a stuck loading spinner; the browser has to actually render the
page like a user's would.

Detection signatures below were established manually on 2026-08-29 by
comparing known-broken routes against known-working ones:
  - Aer Lingus: deep link shows a "Content Forbidden" / "permission to
    view this page" modal, or an explicit "no results/flights" message.
  - Ryanair: deep link spins forever and never renders a fare price on
    any nearby date tab (a working route shows a price within ~2s).
  - Iberia: deep link silently redirects away from the flight-selection
    results page (e.g. back to the homepage) instead of showing fares.

SAS's site puts up a Cloudflare bot-check challenge that a headless
browser can't get past -- and per policy we never attempt to solve
CAPTCHAs -- so SAS is skipped rather than misreported as broken. TAP's
link is just its homepage (not a real deep link) and Turkish Airlines
uses a generic Google Flights search fallback -- both trivially "work"
so there's nothing meaningful to check. Air France, KLM, and Swiss are
checked but have no established failure signature yet, so they're only
ever reported as low-confidence / UNCERTAIN, never treated as BROKEN.

IMPORTANT -- these sites' anti-bot protection punishes automated traffic,
not just genuinely dead routes. Testing on 2026-08-29 showed a route we
had just manually confirmed working (Aer Lingus Dublin-Barcelona) flip to
a false "Content Forbidden" on a later automated check, almost certainly
from the same IP making many requests in a short window. To keep this
from ever auto-deleting a real route on a bad-luck day, this script does
NOT report anything as safe-to-fix on the first BROKEN sighting. It keeps
a small persisted state file (audit_state.json, alongside this script)
and only escalates a pair into the "confirmed_broken" list once it has
been seen BROKEN on two separate runs in a row. A single OK result clears
its count immediately. A caller (e.g. the daily scheduled agent) should
only ever edit getaway.py for pairs in confirmed_broken, never for ones
only in this run's raw "results" list.

Usage:
    pip install playwright && playwright install --with-deps chromium
    python3 scripts/audit_links.py

Prints a JSON report to stdout:
    {
      "results": [{airline, destination, origin, url, status, reason, confidence}, ...],
      "confirmed_broken": [{airline, destination, reason}, ...],   # safe to act on
      "newly_suspected": [{airline, destination, reason}, ...]     # seen broken once, watch next run
    }
"""

import json
import os
import random
import re
import sys
import time
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(SCRIPT_DIR, "audit_state.json")

sys.path.insert(0, SCRIPT_DIR + "/..")
import getaway

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print(json.dumps({
        "error": "playwright not installed",
        "fix": "pip install playwright && playwright install --with-deps chromium",
    }))
    sys.exit(1)

HIGH_CONFIDENCE_AIRLINES = {"Aer Lingus", "Ryanair", "Iberia"}
SKIP_AIRLINES = {
    "SAS": "Cloudflare bot-check blocks headless browsers; never attempt to solve CAPTCHAs",
    "TAP": "link is just the homepage, not a real deep link",
    "Turkish Airlines": "uses a generic Google Flights search fallback, always renders something",
}
STEALTH_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
CONFIRM_AFTER_N_BROKEN = 2


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def pick_dates(start_month, end_month):
    """Pick a date pair ~2 weeks out, nudged into the route's active season if needed."""
    depart = datetime.utcnow() + timedelta(days=14)
    in_season = (
        start_month <= depart.month <= end_month
        if start_month <= end_month
        else (depart.month >= start_month or depart.month <= end_month)
    )
    if not in_season:
        year = depart.year if start_month >= depart.month else depart.year + 1
        depart = datetime(year, start_month, 10)
    ret = depart + timedelta(days=7)
    return depart.strftime("%Y-%m-%d"), ret.strftime("%Y-%m-%d")


def collect_checks():
    """Dedupe ROUTES to one representative (origin) check per (airline, destination)."""
    seen = {}
    for city, routes in getaway.ROUTES.items():
        for airline, origin, start_m, end_m in routes:
            key = (airline, city)
            if key not in seen:
                seen[key] = (origin, start_m, end_m)
    return seen


def new_page(browser):
    context = browser.new_context(user_agent=STEALTH_UA, viewport={"width": 1280, "height": 800})
    page = context.new_page()
    page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined})')
    return page


def check_aer_lingus(page, url):
    page.goto(url, wait_until="load", timeout=30000)
    page.wait_for_timeout(3000)
    text = page.inner_text("body").lower()
    if "content forbidden" in text or "do not have permission" in text:
        return "BROKEN", "Content Forbidden / permission error shown"
    if "no results available" in text or "no flights available" in text:
        return "BROKEN", "No results / no flights for this route"
    return "OK", "Flight selection page rendered"


def check_ryanair(page, url):
    page.goto(url, wait_until="load", timeout=30000)
    for label in ["No, thanks", "Yes, I agree"]:
        try:
            page.click(f"text={label}", timeout=2000)
        except Exception:
            pass
    page.wait_for_timeout(8000)
    text = page.inner_text("body")
    if re.search(r"[€£]\s?\d", text):
        return "OK", "At least one fare price rendered"
    return "BROKEN", "No fare price rendered after 8s wait"


def check_iberia(page, url):
    page.goto(url, wait_until="load", timeout=30000)
    page.wait_for_timeout(6000)
    if "/flights/" not in page.url:
        return "BROKEN", f"Redirected away from search results to {page.url}"
    text = page.inner_text("body").lower()
    if "sorry" in text and "interrupted" in text:
        return "UNCERTAIN", "Page-load error shown (site flakiness, not a route signature)"
    if "select an outbound flight" in text or "cabin and price" in text:
        return "OK", "Flight selection page rendered"
    return "UNCERTAIN", "On flights page but couldn't confirm a fare table rendered"


def check_generic(page, url):
    page.goto(url, wait_until="load", timeout=30000)
    page.wait_for_timeout(4000)
    text = page.inner_text("body").lower()
    if "no result" in text or ("sorry" in text and "no flight" in text):
        return "UNCERTAIN", "Possible no-results message (no established signature for this airline)"
    return "UNCERTAIN", "No established failure signature for this airline; needs manual review"


CHECKERS = {
    "Aer Lingus": check_aer_lingus,
    "Ryanair": check_ryanair,
    "Iberia": check_iberia,
}


def main():
    checks = collect_checks()
    results = []
    state = load_state()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])

        for (airline, city), (origin, start_m, end_m) in sorted(checks.items()):
            if airline in SKIP_AIRLINES:
                results.append({
                    "airline": airline, "destination": city, "origin": origin,
                    "status": "SKIPPED", "reason": SKIP_AIRLINES[airline], "confidence": None,
                })
                continue

            depart_date, return_date = pick_dates(start_m, end_m)
            url = getaway.get_booking_url(airline, origin, city, depart_date, return_date)
            checker = CHECKERS.get(airline, check_generic)
            page = new_page(browser)

            try:
                status, reason = checker(page, url)
            except Exception as e:
                status, reason = "UNCERTAIN", f"Check failed to run: {e}"
            finally:
                page.close()

            results.append({
                "airline": airline, "destination": city, "origin": origin, "url": url,
                "status": status, "reason": reason,
                "confidence": "high" if airline in HIGH_CONFIDENCE_AIRLINES else "low",
            })

            # Be a slow, human-paced visitor -- these sites' anti-bot systems
            # escalate against bursts of automated-looking traffic.
            time.sleep(random.uniform(3, 6))

        browser.close()

    confirmed_broken = []
    newly_suspected = []
    for r in results:
        key = f"{r['airline']}||{r['destination']}"
        if r["status"] == "BROKEN" and r["confidence"] == "high":
            count = state.get(key, 0) + 1
            state[key] = count
            if count >= CONFIRM_AFTER_N_BROKEN:
                confirmed_broken.append({"airline": r["airline"], "destination": r["destination"], "reason": r["reason"]})
            else:
                newly_suspected.append({"airline": r["airline"], "destination": r["destination"], "reason": r["reason"]})
        else:
            state.pop(key, None)

    save_state(state)

    print(json.dumps({
        "results": results,
        "confirmed_broken": confirmed_broken,
        "newly_suspected": newly_suspected,
    }, indent=2))


if __name__ == "__main__":
    main()
