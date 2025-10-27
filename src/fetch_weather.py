#!/usr/bin/env python3
"""
Fetch current weather data from OpenWeatherMap and upload it to AWS S3.

- Uses environment variables (no hardcoded secrets)
- Includes basic error handling
- Adds logging and clear console feedback
"""

import os
import json
import requests
import boto3
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# === Load environment variables from key.env ===
load_dotenv("key.env")

# === Configuration from environment ===
API_KEY = os.getenv("OWM_API_KEY")
CITY = os.getenv("CITY", "Plymouth")
BUCKET_NAME = os.getenv("S3_BUCKET")

# Validate required variables early
if not API_KEY:
    raise SystemExit("❌ Missing environment variable: OWM_API_KEY")
if not BUCKET_NAME:
    raise SystemExit("❌ Missing environment variable: S3_BUCKET")

# Optional: choose metric or imperial units
UNITS = os.getenv("UNITS", "metric")  # or 'imperial'

def fetch_weather(city: str, api_key: str, units: str = "metric") -> dict:
    """Fetch current weather data for a given city from OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": units}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # raise HTTPError for bad responses
        print(f"🌍 Successfully fetched weather data for {city}")
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"❌ HTTP error: {err}")
    except requests.exceptions.RequestException as err:
        print(f"❌ Network or connection error: {err}")
    return {}

def upload_to_s3(data: dict, bucket: str, city: str):
    """Upload weather data JSON to S3 under a timestamped key."""
    if not data:
        print("⚠️ No data to upload.")
        return

    s3 = boto3.client("s3")
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    key = f"raw/{city}_{timestamp}.json"

    try:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
        print(f"✅ Uploaded to s3://{bucket}/{key}")
    except (BotoCoreError, ClientError) as err:
        print(f"❌ AWS upload failed: {err}")

def main():
    """Main entrypoint for fetching and uploading weather data."""
    print(f"⏳ Fetching weather data for {CITY}...")
    data = fetch_weather(CITY, API_KEY, UNITS)
    upload_to_s3(data, BUCKET_NAME, CITY)

if __name__ == "__main__":
    main()
