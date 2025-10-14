#!/usr/bin/env python3
"""
Essential Beestat Data Fetcher
Extracts only the 5 key thermostat fields you need:
1. Current temperature (°F)
2. HVAC mode (heat/cool/auto - inferred from equipment and setpoints)
3. Running equipment
4. Current humidity (%)
5. Temperature setpoints
"""

import json
import urllib.request
import urllib.error
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configuration
BEESTAT_API_KEY = "e1984530c9b7d61e838c470e451b5c16856dbd40"
BEESTAT_API_BASE = "https://api.beestat.io/"

# Target thermostats to filter (set to None to show all)
TARGET_THERMOSTATS = ["Downstairs", "809 Sailors Cove"]


def fetch_beestat_data() -> Dict[str, Any]:
    """
    Fetch thermostat data from Beestat API
    Single API call: thermostat.read_id
    """
    endpoint = f"{BEESTAT_API_BASE}?api_key={BEESTAT_API_KEY}&resource=thermostat&method=read_id"

    try:
        req = urllib.request.Request(endpoint)
        req.add_header('User-Agent', 'Mozilla/5.0')

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                data = json.loads(response.read().decode('utf-8'))
                if data and data.get('success'):
                    return data

        raise Exception("API returned unexpected format")

    except Exception as e:
        raise Exception(f"API request failed: {e}")


def infer_hvac_mode(thermostat: Dict[str, Any]) -> str:
    """
    Infer HVAC mode from running equipment and setpoints
    Since Beestat API doesn't return the mode directly, we infer it
    """
    running_equipment = thermostat.get('running_equipment', [])
    heat_setpoint = thermostat.get('setpoint_heat')
    cool_setpoint = thermostat.get('setpoint_cool')

    # Check running equipment first (most accurate indicator)
    for equipment in running_equipment:
        eq_lower = equipment.lower()
        if 'cool' in eq_lower or 'compcool' in eq_lower:
            return 'cool'
        elif 'heat' in eq_lower or 'compheat' in eq_lower or 'auxheat' in eq_lower:
            return 'heat'

    # If nothing running, infer from setpoints
    # If both setpoints are the same, it's likely in a specific mode
    if heat_setpoint and cool_setpoint:
        if heat_setpoint == cool_setpoint:
            # Same setpoint - probably set to a specific temp in heat or cool mode
            # We'll call this 'auto' since we can't determine which
            return 'auto'
        else:
            # Different setpoints - auto mode (thermostat will heat or cool as needed)
            return 'auto'
    elif heat_setpoint and not cool_setpoint:
        return 'heat'
    elif cool_setpoint and not heat_setpoint:
        return 'cool'
    else:
        # Default
        return 'auto'


def parse_essential_data(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse and extract ONLY the 5 essential fields
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

        # Extract the 5 essential fields
        record = {
            # Identification
            'thermostat_id': thermostat.get('thermostat_id'),
            'name': name,

            # 1. Current Temperature (°F)
            'current_temperature_f': thermostat.get('temperature'),

            # 2. HVAC Mode (inferred)
            'hvac_mode': infer_hvac_mode(thermostat),

            # 3. Running Equipment
            'running_equipment': thermostat.get('running_equipment', []),
            'equipment_state': ', '.join(thermostat.get('running_equipment', [])) if thermostat.get('running_equipment') else 'idle',

            # 4. Current Humidity (%)
            'current_humidity_percent': thermostat.get('humidity'),

            # 5. Temperature Setpoints (°F)
            'heat_setpoint_f': thermostat.get('setpoint_heat'),
            'cool_setpoint_f': thermostat.get('setpoint_cool'),

            # Metadata
            'timestamp': datetime.now().isoformat(),
        }

        thermostats.append(record)

    return thermostats


def display_essential_data(thermostats: List[Dict[str, Any]]) -> None:
    """
    Display the 5 essential fields in a clean format
    """
    print("=" * 80)
    print(f"BEESTAT ESSENTIAL DATA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print()

    for t in thermostats:
        print(f"📍 {t['name']} (ID: {t['thermostat_id']})")
        print()
        print(f"   1️⃣  Current Temperature:  {t['current_temperature_f']}°F")
        print(f"   2️⃣  HVAC Mode:            {t['hvac_mode'].upper()}")
        print(f"   3️⃣  Running Equipment:    {t['equipment_state']}")
        if t['running_equipment']:
            print(f"       └─ Active: {t['running_equipment']}")
        print(f"   4️⃣  Current Humidity:     {t['current_humidity_percent']}%")
        print(f"   5️⃣  Temperature Setpoints:")
        print(f"       └─ Heat: {t['heat_setpoint_f']}°F")
        print(f"       └─ Cool: {t['cool_setpoint_f']}°F")
        print()
        print("-" * 80)
        print()

    print("=" * 80)


def save_essential_data(thermostats: List[Dict[str, Any]]) -> None:
    """
    Save essential data to JSON file
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"beestat_essential_{timestamp}.json"

    with open(filename, 'w') as f:
        json.dump(thermostats, f, indent=2)

    print(f"✓ Essential data saved to: {filename}")


def main():
    """
    Main function
    """
    try:
        print("Fetching essential thermostat data from Beestat API...")
        print(f"API Call: GET {BEESTAT_API_BASE}?api_key=***&resource=thermostat&method=read_id")
        print()

        # Single API call gets everything
        raw_data = fetch_beestat_data()
        print(f"✓ API call successful!")
        print()

        # Parse essential fields
        thermostats = parse_essential_data(raw_data)

        if not thermostats:
            print("No thermostats found matching the criteria.")
            return 1

        # Display
        display_essential_data(thermostats)

        # Save to file
        save_essential_data(thermostats)

        print()
        print("=" * 80)
        print("FIELD MAPPING")
        print("=" * 80)
        print("API Response Structure:")
        print("  1. Current Temperature:  data[id]['temperature']")
        print("  2. HVAC Mode:            INFERRED (see note below)")
        print("  3. Running Equipment:    data[id]['running_equipment']")
        print("  4. Current Humidity:     data[id]['humidity']")
        print("  5. Heat Setpoint:        data[id]['setpoint_heat']")
        print("     Cool Setpoint:        data[id]['setpoint_cool']")
        print()
        print("Note: HVAC mode is not directly provided by the Beestat API.")
        print("      It is inferred from running equipment and setpoint configuration.")
        print("      Logic: Check running equipment for 'cool'/'heat', otherwise use setpoints.")
        print("=" * 80)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
