#!/usr/bin/env python3
"""
Standalone Beestat API Client (No External Dependencies)
Fetches thermostat data from the Beestat API using only Python standard library
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Any
from datetime import datetime

# Configuration
BEESTAT_API_KEY = "e1984530c9b7d61e838c470e451b5c16856dbd40"
BEESTAT_API_BASE = "https://beestat.io/api/"

# Target thermostats to filter (optional - set to None to show all)
TARGET_THERMOSTATS = ["Downstairs", "809 Sailors Cove"]


def fetch_beestat_data() -> Dict[str, Any]:
    """
    Fetch thermostat data from Beestat API
    Tries multiple endpoint variations
    """
    endpoint_variations = [
        f"{BEESTAT_API_BASE}?api_key={BEESTAT_API_KEY}&resource=thermostat&method=read_id",
        f"{BEESTAT_API_BASE}?api_key={BEESTAT_API_KEY}&resource=ecobee_runtime_thermostat&method=read_id",
        f"{BEESTAT_API_BASE}?api_key={BEESTAT_API_KEY}&resource=runtime_thermostat&method=read_id",
        f"https://api.beestat.io/?api_key={BEESTAT_API_KEY}&resource=thermostat&method=read_id"
    ]

    last_error = None

    for endpoint in endpoint_variations:
        try:
            print(f"Trying endpoint: {endpoint[:50]}...")

            req = urllib.request.Request(endpoint)
            req.add_header('User-Agent', 'Mozilla/5.0 (Beestat Python Client)')

            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                print(f"Response: {status_code}")

                if status_code == 200:
                    response_text = response.read().decode('utf-8')
                    data = json.loads(response_text)

                    # Check if we got valid data
                    if data and (data.get('success') or data.get('data')):
                        print(f"Success! Got data with {len(data.get('data', {}))} thermostats\n")
                        return data
                    else:
                        print(f"Unexpected response format: {json.dumps(data, indent=2)[:200]}\n")
                        last_error = f"Unexpected format: {data}"
                else:
                    print(f"Error response: {status_code}\n")
                    last_error = f"HTTP {status_code}"

        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')[:200] if e.fp else str(e)
            print(f"HTTP Error {e.code}: {error_text}\n")
            last_error = f"HTTP {e.code}: {error_text}"
            continue
        except urllib.error.URLError as e:
            print(f"URL Error: {e.reason}\n")
            last_error = str(e.reason)
            continue
        except Exception as e:
            print(f"Request failed: {e}\n")
            last_error = str(e)
            continue

    raise Exception(f"All endpoints failed. Last error: {last_error}")


def parse_thermostat_data(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse and format thermostat data from Beestat API response
    """
    thermostats = []
    data = raw_data.get('data', {})

    for thermostat_id, thermostat in data.items():
        # Get thermostat name
        name = thermostat.get('name', thermostat.get('identifier', 'Unknown'))

        # Filter by target thermostats if specified
        if TARGET_THERMOSTATS:
            if not any(target.lower() in name.lower() for target in TARGET_THERMOSTATS):
                continue

        # Parse temperature data
        current_temp = (
            thermostat.get('actual_temperature') or
            thermostat.get('indoor_temperature') or
            thermostat.get('temperature')
        )

        heat_setpoint = thermostat.get('setpoint_heat')
        cool_setpoint = thermostat.get('setpoint_cool')
        humidity = thermostat.get('humidity')
        hvac_mode = thermostat.get('hvac_mode') or thermostat.get('settings', {}).get('hvacMode')
        running_equipment = thermostat.get('running_equipment', [])

        # Determine HVAC state
        if running_equipment:
            hvac_state = ', '.join(running_equipment)
        else:
            hvac_state = 'idle'

        # Build parsed thermostat object
        parsed = {
            'id': thermostat_id,
            'ecobee_id': thermostat.get('ecobee_thermostat_id'),
            'name': name,
            'identifier': thermostat.get('identifier'),
            'current_temperature': current_temp,
            'heat_setpoint': heat_setpoint,
            'cool_setpoint': cool_setpoint,
            'humidity': humidity,
            'hvac_mode': hvac_mode,
            'hvac_state': hvac_state,
            'running_equipment': running_equipment,
            'timestamp': datetime.now().isoformat()
        }

        thermostats.append(parsed)

    return thermostats


def display_thermostat_data(thermostats: List[Dict[str, Any]]) -> None:
    """
    Display formatted thermostat data
    """
    print("=" * 80)
    print(f"BEESTAT THERMOSTAT DATA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    for thermostat in thermostats:
        print(f"Thermostat: {thermostat['name']}")
        print(f"  ID: {thermostat['id']}")
        print(f"  Ecobee ID: {thermostat['ecobee_id']}")
        print(f"  Identifier: {thermostat['identifier']}")
        print(f"  Current Temperature: {thermostat['current_temperature']}°F")
        print(f"  Heat Setpoint: {thermostat['heat_setpoint']}°F")
        print(f"  Cool Setpoint: {thermostat['cool_setpoint']}°F")
        print(f"  Humidity: {thermostat['humidity']}%")
        print(f"  HVAC Mode: {thermostat['hvac_mode']}")
        print(f"  HVAC State: {thermostat['hvac_state']}")
        print(f"  Running Equipment: {thermostat['running_equipment']}")
        print()

    print("=" * 80)


def save_json_output(raw_data: Dict[str, Any], thermostats: List[Dict[str, Any]]) -> None:
    """
    Save both raw and parsed data to JSON files
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save raw response
    raw_filename = f"beestat_raw_{timestamp}.json"
    with open(raw_filename, 'w') as f:
        json.dump(raw_data, f, indent=2)
    print(f"Raw data saved to: {raw_filename}")

    # Save parsed data
    parsed_filename = f"beestat_parsed_{timestamp}.json"
    with open(parsed_filename, 'w') as f:
        json.dump(thermostats, f, indent=2)
    print(f"Parsed data saved to: {parsed_filename}")


def main():
    """
    Main function
    """
    try:
        print("Fetching Beestat data...\n")

        # Fetch raw data
        raw_data = fetch_beestat_data()

        # Parse thermostat data
        thermostats = parse_thermostat_data(raw_data)

        if not thermostats:
            print("No thermostats found matching the criteria.")
            return

        # Display formatted data
        display_thermostat_data(thermostats)

        # Save to JSON files
        save_json_output(raw_data, thermostats)

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
