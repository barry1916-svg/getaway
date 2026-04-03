# Weather Alert App

Get daily email alerts about sunny European destinations with direct flights from Ireland.

The app checks 55+ destinations and emails you when any have:
- Temperature above 22°C
- Clear or mostly sunny skies

---

## Setup Instructions

### Step 1: Install Python

**Check if you have Python:**
```bash
python3 --version
```

If you see a version number (like `Python 3.11.0`), you're good! Skip to Step 2.

**If you don't have Python:**
- **Mac:** Open Terminal and run: `brew install python3`
  (If you don't have Homebrew, visit https://brew.sh first)
- **Windows:** Download from https://www.python.org/downloads/ and run the installer.
  **Important:** Check "Add Python to PATH" during installation.

---

### Step 2: Download the App

Put these files in a folder (e.g., `weather-alert`):
- `check_weather.py`
- `requirements.txt`
- `.env.example`

---

### Step 3: Install Required Packages

Open Terminal (Mac) or Command Prompt (Windows), navigate to your folder, and run:

```bash
cd /path/to/weather-alert
pip3 install -r requirements.txt
```

---

### Step 4: Set Up Gmail App Password

Gmail requires a special "App Password" for apps to send email. Here's how to get one:

1. Go to https://myaccount.google.com/security
2. Make sure **2-Step Verification** is turned ON (required for App Passwords)
3. Go to https://myaccount.google.com/apppasswords
4. Select "Mail" and your device, then click "Generate"
5. Google will show you a 16-character password like `abcd efgh ijkl mnop`
6. Copy this password (remove the spaces)

---

### Step 5: Create Your Configuration File

1. Copy `.env.example` to a new file called `.env`:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in any text editor and fill in your details:
   ```
   GMAIL_ADDRESS=yourname@gmail.com
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   RECIPIENT_EMAIL=whereyouwantalerts@email.com
   ```

**Important:** Never share your `.env` file or commit it to version control!

---

### Step 6: Test It!

Run the app:

```bash
python3 check_weather.py
```

You should see:
- A list of destinations being checked
- A summary of destinations with good weather
- Confirmation that the email was sent

Check your inbox!

---

## Scheduling Daily Alerts

### Mac/Linux (using cron)

1. Open Terminal and type:
   ```bash
   crontab -e
   ```

2. Add this line (runs daily at 7:00 AM):
   ```
   0 7 * * * cd /path/to/weather-alert && /usr/bin/python3 check_weather.py >> /tmp/weather-alert.log 2>&1
   ```

   Replace `/path/to/weather-alert` with your actual folder path.

3. Save and exit (in nano: Ctrl+X, then Y, then Enter)

**To find your Python path:** Run `which python3` in Terminal.

**To check your scheduled jobs:** Run `crontab -l`

**To remove the schedule:** Run `crontab -e` and delete the line.

---

### Windows (using Task Scheduler)

1. Press `Win + R`, type `taskschd.msc`, press Enter

2. Click **"Create Basic Task"** in the right panel

3. Name it "Weather Alert" and click Next

4. Select **"Daily"** and click Next

5. Set your preferred time (e.g., 7:00 AM) and click Next

6. Select **"Start a program"** and click Next

7. Fill in:
   - **Program:** `python` (or full path like `C:\Python311\python.exe`)
   - **Arguments:** `check_weather.py`
   - **Start in:** `C:\path\to\weather-alert` (your folder path)

8. Click Next, then Finish

**To test:** Find your task in Task Scheduler Library, right-click, and select "Run"

---

## Troubleshooting

### "No module named 'requests'" or similar
Run: `pip3 install -r requirements.txt`

### "Missing email configuration" error
Make sure you have a `.env` file (not just `.env.example`) with your credentials.

### "Authentication failed" email error
- Double-check your App Password (no spaces)
- Make sure 2-Step Verification is enabled on your Google account
- Try generating a new App Password

### No destinations found
This just means no cities currently have clear skies above 22°C. Try again another day, or lower the temperature threshold in the code (change `MIN_TEMP = 22.0`).

### Cron job not running (Mac/Linux)
- Check the log file: `cat /tmp/weather-alert.log`
- Make sure paths are absolute (full paths, not `~/`)
- Give cron Full Disk Access in System Preferences > Security & Privacy

---

## Customization

### Change temperature threshold
In `check_weather.py`, find this line and change the number:
```python
MIN_TEMP = 22.0
```

### Add or remove destinations
Edit the `DESTINATIONS` list at the top of `check_weather.py`. Each entry needs:
```python
{"city": "City Name", "country": "Country", "lat": 12.345, "lon": 67.890},
```
You can find coordinates by searching "city name coordinates" on Google.

---

## How It Works

1. Checks weather forecast for 55+ European cities
2. Uses the free Open-Meteo API (no API key needed)
3. Looks for days with temperature > 22°C AND clear/sunny skies
4. Sends a nicely formatted HTML email with results grouped by country

Weather codes considered "good": Clear sky (0), Mainly clear (1), Partly cloudy (2)

---

Enjoy your sunny escapes!
