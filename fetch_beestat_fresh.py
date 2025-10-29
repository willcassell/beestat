#!/usr/bin/env python3
"""
Beestat API - Fresh Data Example with Sync Methods

This script demonstrates how to force fresh data from Beestat using official sync methods.
Uses the sync-then-fetch pattern to ensure data is current.

Features:
- Batch sync API calls (thermostat + sensor)
- 30-second wait for sync to complete
- Fetches freshly synced data
- Displays sync timestamps to verify freshness
"""

import json
import urllib.request
import urllib.parse
import time
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

BEESTAT_API_KEY = "your_api_key_here"  # Get from https://beestat.io/account
API_BASE = "https://api.beestat.io/"

# Target thermostats to display (set to None for all)
TARGET_THERMOSTATS = ["Downstairs", "809 Sailors Cove"]

# ============================================================================
# FUNCTIONS
# ============================================================================

def trigger_sync():
    """
    Trigger Beestat to sync fresh data from Ecobee using batch API.

    Uses batch API to sync thermostats and sensors simultaneously for efficiency.
    Rate limited to once per 3 minutes by Beestat.
    """
    print("🔄 Triggering Beestat sync (thermostat + sensor)...")

    # Batch sync request - more efficient than separate calls
    batch = [
        {"resource": "thermostat", "method": "sync", "alias": "thermostat_sync"},
        {"resource": "sensor", "method": "sync", "alias": "sensor_sync"}
    ]

    # URL encode the batch parameter
    batch_json = json.dumps(batch)
    url = f"{API_BASE}?api_key={BEESTAT_API_KEY}&batch={urllib.parse.quote(batch_json)}"

    try:
        response = urllib.request.urlopen(url)
        result = json.loads(response.read())

        # Check for errors in batch response
        if result.get("thermostat_sync", {}).get("error_code"):
            print(f"⚠️  Thermostat sync warning: {result['thermostat_sync']}")
        else:
            print("✓ Thermostat sync triggered successfully")

        if result.get("sensor_sync", {}).get("error_code"):
            print(f"⚠️  Sensor sync warning: {result['sensor_sync']}")
        else:
            print("✓ Sensor sync triggered successfully")

        return True

    except Exception as e:
        print(f"✗ Failed to trigger sync: {e}")
        return False


def fetch_thermostat_data():
    """
    Fetch thermostat data from Beestat API.

    Returns the full API response with all thermostat data.
    """
    url = f"{API_BASE}?api_key={BEESTAT_API_KEY}&resource=thermostat&method=read_id"

    try:
        response = urllib.request.urlopen(url)
        data = json.loads(response.read())
        return data.get("data", {})
    except Exception as e:
        print(f"✗ Failed to fetch data: {e}")
        return None


def display_thermostat_data(thermostats):
    """
    Display formatted thermostat data with sync timestamps.
    """
    if not thermostats:
        print("No thermostat data available")
        return

    print("\n" + "=" * 80)
    print("BEESTAT THERMOSTAT DATA (FRESH)")
    print("=" * 80 + "\n")

    for thermostat_id, therm in thermostats.items():
        name = therm.get("name", "Unknown")

        # Filter by target thermostats if specified
        if TARGET_THERMOSTATS and name not in TARGET_THERMOSTATS:
            continue

        # Extract key fields
        temp = therm.get("temperature", "N/A")
        humidity = therm.get("humidity", "N/A")
        heat_setpoint = therm.get("setpoint_heat", "N/A")
        cool_setpoint = therm.get("setpoint_cool", "N/A")
        running_equipment = therm.get("running_equipment", [])
        sync_end = therm.get("sync_end", "Unknown")
        data_end = therm.get("data_end", "Unknown")

        print(f"Thermostat: {name}")
        print(f"  ID: {therm.get('thermostat_id', 'N/A')}")
        print(f"  Current Temperature: {temp}°F")
        print(f"  Heat Setpoint: {heat_setpoint}°F")
        print(f"  Cool Setpoint: {cool_setpoint}°F")
        print(f"  Humidity: {humidity}%")
        print(f"  Running Equipment: {running_equipment}")
        print(f"  📅 Last Sync: {sync_end}")
        print(f"  📅 Data End: {data_end}")

        # Calculate data age
        try:
            sync_time = datetime.strptime(sync_end, "%Y-%m-%d %H:%M:%S")
            age_minutes = (datetime.now() - sync_time).total_seconds() / 60
            print(f"  ⏱️  Data Age: {age_minutes:.1f} minutes old")
        except:
            pass

        print()

    print("=" * 80)


def main():
    """
    Main execution flow: sync → wait → fetch → display
    """
    print("\n" + "=" * 80)
    print("Beestat API - Fresh Data Example")
    print("=" * 80)

    # Step 1: Trigger sync
    if not trigger_sync():
        print("\n⚠️  Sync trigger failed, but will attempt to fetch data anyway...")

    # Step 2: Wait for sync to complete
    print("\n⏳ Waiting 30 seconds for Beestat to sync with Ecobee...")
    time.sleep(30)

    # Step 3: Fetch fresh data
    print("\n📡 Fetching freshly synced thermostat data...\n")
    thermostats = fetch_thermostat_data()

    # Step 4: Display results
    if thermostats:
        display_thermostat_data(thermostats)

        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"beestat_fresh_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(thermostats, f, indent=2)
        print(f"\n💾 Data saved to: {filename}")
    else:
        print("\n✗ No data retrieved")


if __name__ == "__main__":
    main()
