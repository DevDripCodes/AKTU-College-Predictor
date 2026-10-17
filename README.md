# UPTAC College Predictor

A small Flask app that uses a JEE Main CRL rank to find possible colleges from UPTAC 2024 cutoff data.

## Run locally

1. Install Python 3.9 or newer.
2. Create and activate a virtual environment:
   - Windows: py -m venv .venv, then .venv\Scripts\Activate.ps1
   - macOS/Linux: python3 -m venv .venv, then source .venv/bin/activate
3. Install dependencies with pip install -r requirements.txt.
4. Start the app with python app.py.
5. Open http://127.0.0.1:5000 in your browser.

## Deploy on Vercel

Import this repository as a Vercel project and deploy with the default Python settings. Vercel detects the Flask app from app.py. The vercel.json configuration explicitly includes the Jinja templates and cutoff CSV used at runtime.

The app compares your CRL rank with each matching row's closing rank. Results whose closing rank is equal to or greater than your rank are shown, sorted by closing rank.

Predictions are based on historical 2024 cutoffs and are not a guarantee of admission.
