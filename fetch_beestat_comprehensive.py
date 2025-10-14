#!/usr/bin/env python3
"""
Comprehensive Beestat API Client
Fetches and parses ALL available thermostat data from the Beestat API
Creates one comprehensive record per thermostat with all available fields
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
    Fetch comprehensive thermostat data from Beestat API
    """
    endpoint = f"{BEESTAT_API_BASE}?api_key={BEESTAT_API_KEY}&resource=thermostat&method=read_id"

    try:
        print(f"Fetching data from Beestat API...")
        req = urllib.request.Request(endpoint)
        req.add_header('User-Agent', 'Mozilla/5.0 (Beestat Python Client)')

        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            if status_code == 200:
                response_text = response.read().decode('utf-8')
                data = json.loads(response_text)

                if data and (data.get('success') or data.get('data')):
                    print(f"✓ Success! Retrieved data for {len(data.get('data', {}))} thermostats\n")
                    return data
                else:
                    raise Exception(f"Unexpected response format: {data}")
            else:
                raise Exception(f"HTTP {status_code}")

    except Exception as e:
        raise Exception(f"API request failed: {e}")


def parse_comprehensive_thermostat_data(raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse ALL available thermostat data into comprehensive records
    One complete record per thermostat with all fields
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

        # Build comprehensive thermostat record
        record = {
            # === IDENTIFICATION ===
            'thermostat_id': thermostat.get('thermostat_id'),
            'ecobee_thermostat_id': thermostat.get('ecobee_thermostat_id'),
            'user_id': thermostat.get('user_id'),
            'name': name,
            'identifier': thermostat.get('identifier'),
            'address_id': thermostat.get('address_id'),

            # === CURRENT STATUS ===
            'temperature': thermostat.get('temperature'),
            'temperature_unit': thermostat.get('temperature_unit'),
            'humidity': thermostat.get('humidity'),
            'setpoint_heat': thermostat.get('setpoint_heat'),
            'setpoint_cool': thermostat.get('setpoint_cool'),
            'running_equipment': thermostat.get('running_equipment', []),
            'hvac_state': ', '.join(thermostat.get('running_equipment', [])) if thermostat.get('running_equipment') else 'idle',

            # === LOCATION ===
            'location': {
                'latitude': thermostat.get('profile', {}).get('address', {}).get('latitude'),
                'longitude': thermostat.get('profile', {}).get('address', {}).get('longitude'),
            },

            # === PROPERTY INFORMATION ===
            'property': {
                'age': thermostat.get('property', {}).get('age'),
                'stories': thermostat.get('property', {}).get('stories'),
                'square_feet': thermostat.get('property', {}).get('square_feet'),
                'structure_type': thermostat.get('property', {}).get('structure_type'),
            },

            # === SYSTEM TYPE ===
            'system_type': thermostat.get('system_type', {}),

            # === WEATHER ===
            'weather': {
                'condition': thermostat.get('weather', {}).get('condition'),
                'temperature': thermostat.get('weather', {}).get('temperature'),
                'temperature_low': thermostat.get('weather', {}).get('temperature_low'),
                'temperature_high': thermostat.get('weather', {}).get('temperature_high'),
                'dew_point': thermostat.get('weather', {}).get('dew_point'),
                'humidity_relative': thermostat.get('weather', {}).get('humidity_relative'),
                'wind_speed': thermostat.get('weather', {}).get('wind_speed'),
                'wind_bearing': thermostat.get('weather', {}).get('wind_bearing'),
                'barometric_pressure': thermostat.get('weather', {}).get('barometric_pressure'),
            },

            # === SETTINGS ===
            'settings': {
                'differential_cool': thermostat.get('settings', {}).get('differential_cool'),
                'differential_heat': thermostat.get('settings', {}).get('differential_heat'),
            },

            # === PROGRAM/SCHEDULE ===
            'program': {
                'climates': thermostat.get('program', {}).get('climates', []),
                'current_climate': thermostat.get('program', {}).get('currentClimateRef'),
                'schedule': thermostat.get('program', {}).get('schedule', []),
            },

            # === FILTERS ===
            'filters': thermostat.get('filters', {}),

            # === ALERTS ===
            'alerts': thermostat.get('alerts', []),
            'active_alerts_count': len([a for a in thermostat.get('alerts', []) if not a.get('dismissed', False)]),

            # === PROFILE/ANALYTICS ===
            'profile': {
                'runtime': thermostat.get('profile', {}).get('runtime', {}),
                'setback': thermostat.get('profile', {}).get('setback', {}),
                'setpoint': thermostat.get('profile', {}).get('setpoint', {}),
                'degree_days': thermostat.get('profile', {}).get('degree_days', {}),
                'differential': thermostat.get('profile', {}).get('differential', {}),
                'balance_point': thermostat.get('profile', {}).get('balance_point', {}),
                'runtime_per_degree_day': thermostat.get('profile', {}).get('runtime_per_degree_day', {}),
                'metadata': thermostat.get('profile', {}).get('metadata', {}),
            },

            # === TIMESTAMPS ===
            'time_zone': thermostat.get('time_zone'),
            'first_connected': thermostat.get('first_connected'),
            'sync_begin': thermostat.get('sync_begin'),
            'sync_end': thermostat.get('sync_end'),
            'data_begin': thermostat.get('data_begin'),
            'data_end': thermostat.get('data_end'),

            # === STATUS FLAGS ===
            'inactive': thermostat.get('inactive', False),
            'deleted': thermostat.get('deleted', False),

            # === METADATA ===
            'fetch_timestamp': datetime.now().isoformat(),
        }

        # Calculate derived fields
        record['current_climate_details'] = get_current_climate_details(thermostat)
        record['system_summary'] = get_system_summary(thermostat)
        record['efficiency_metrics'] = get_efficiency_metrics(thermostat)

        thermostats.append(record)

    return thermostats


def get_current_climate_details(thermostat: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get details about the currently active climate/comfort setting
    """
    program = thermostat.get('program', {})
    current_ref = program.get('currentClimateRef')

    if not current_ref:
        return None

    climates = program.get('climates', [])
    for climate in climates:
        if climate.get('climateRef') == current_ref:
            return {
                'name': climate.get('name'),
                'type': climate.get('type'),
                'heat_temp': climate.get('heatTemp'),
                'cool_temp': climate.get('coolTemp'),
                'is_occupied': climate.get('isOccupied'),
                'is_optimized': climate.get('isOptimized'),
                'sensors': climate.get('sensors', []),
            }

    return None


def get_system_summary(thermostat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a human-readable system summary
    """
    system_type = thermostat.get('system_type', {})
    detected = system_type.get('detected', {})

    return {
        'cooling_system': f"{detected.get('cool', {}).get('stages', 0)}-stage {detected.get('cool', {}).get('equipment', 'unknown')}",
        'heating_system': f"{detected.get('heat', {}).get('stages', 0)}-stage {detected.get('heat', {}).get('equipment', 'unknown')}",
        'auxiliary_heat': detected.get('auxiliary_heat', {}).get('equipment', 'none'),
    }


def get_efficiency_metrics(thermostat: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate efficiency metrics from profile data
    """
    profile = thermostat.get('profile', {})
    runtime = profile.get('runtime', {})
    degree_days = profile.get('degree_days', {})

    # Calculate total runtime
    total_cool_runtime = runtime.get('cool_1', 0) + runtime.get('cool_2', 0)
    total_heat_runtime = runtime.get('heat_1', 0) + runtime.get('heat_2', 0)
    total_aux_runtime = runtime.get('auxiliary_heat_1', 0) + runtime.get('auxiliary_heat_2', 0)

    # Calculate efficiency (runtime per degree day)
    cool_efficiency = None
    heat_efficiency = None

    if degree_days.get('cool', 0) > 0:
        cool_efficiency = round(total_cool_runtime / degree_days['cool'], 2)

    if degree_days.get('heat', 0) > 0:
        heat_efficiency = round(total_heat_runtime / degree_days['heat'], 2)

    return {
        'total_cool_runtime_minutes': total_cool_runtime,
        'total_heat_runtime_minutes': total_heat_runtime,
        'total_aux_heat_runtime_minutes': total_aux_runtime,
        'cool_degree_days': degree_days.get('cool'),
        'heat_degree_days': degree_days.get('heat'),
        'cool_runtime_per_degree_day': cool_efficiency,
        'heat_runtime_per_degree_day': heat_efficiency,
    }


def display_comprehensive_data(thermostats: List[Dict[str, Any]]) -> None:
    """
    Display comprehensive thermostat data in a readable format
    """
    print("=" * 100)
    print(f"COMPREHENSIVE BEESTAT THERMOSTAT DATA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()

    for thermostat in thermostats:
        print(f"╔══════════════════════════════════════════════════════════════════════════════════════════════╗")
        print(f"║ {thermostat['name']:^92} ║")
        print(f"╚══════════════════════════════════════════════════════════════════════════════════════════════╝")
        print()

        # Current Status
        print(f"📊 CURRENT STATUS")
        print(f"   Temperature:       {thermostat['temperature']}°F")
        print(f"   Humidity:          {thermostat['humidity']}%")
        print(f"   Heat Setpoint:     {thermostat['setpoint_heat']}°F")
        print(f"   Cool Setpoint:     {thermostat['setpoint_cool']}°F")
        print(f"   HVAC State:        {thermostat['hvac_state']}")
        print(f"   Running Equipment: {thermostat['running_equipment']}")
        print()

        # Current Climate
        if thermostat['current_climate_details']:
            climate = thermostat['current_climate_details']
            print(f"🏠 CURRENT CLIMATE: {climate['name']}")
            print(f"   Occupied:          {climate['is_occupied']}")
            print(f"   Heat Setting:      {climate['heat_temp']}°F")
            print(f"   Cool Setting:      {climate['cool_temp']}°F")
            print(f"   Active Sensors:    {len(climate['sensors'])} sensors")
            print()

        # Weather
        weather = thermostat['weather']
        print(f"🌤  WEATHER")
        print(f"   Condition:         {weather['condition']}")
        print(f"   Outdoor Temp:      {weather['temperature']}°F (Low: {weather['temperature_low']}°F, High: {weather['temperature_high']}°F)")
        print(f"   Humidity:          {weather['humidity_relative']}%")
        print(f"   Wind:              {weather['wind_speed']} mph @ {weather['wind_bearing']}°")
        print(f"   Pressure:          {weather['barometric_pressure']} mb")
        print()

        # Property
        prop = thermostat['property']
        print(f"🏡 PROPERTY")
        print(f"   Type:              {prop['structure_type']}")
        print(f"   Size:              {prop['square_feet']} sq ft, {prop['stories']} stories")
        print(f"   Age:               {prop['age']} years")
        print()

        # System
        system = thermostat['system_summary']
        print(f"⚙️  HVAC SYSTEM")
        print(f"   Cooling:           {system['cooling_system']}")
        print(f"   Heating:           {system['heating_system']}")
        print(f"   Auxiliary Heat:    {system['auxiliary_heat']}")
        print()

        # Efficiency
        eff = thermostat['efficiency_metrics']
        print(f"📈 EFFICIENCY METRICS (Past Year)")
        print(f"   Cool Runtime:      {eff['total_cool_runtime_minutes']:,} minutes ({eff['cool_degree_days']} degree days)")
        print(f"   Heat Runtime:      {eff['total_heat_runtime_minutes']:,} minutes ({eff['heat_degree_days']} degree days)")
        if eff['total_aux_heat_runtime_minutes'] > 0:
            print(f"   Aux Heat Runtime:  {eff['total_aux_heat_runtime_minutes']:,} minutes")
        if eff['cool_runtime_per_degree_day']:
            print(f"   Cool Efficiency:   {eff['cool_runtime_per_degree_day']} min/degree-day")
        if eff['heat_runtime_per_degree_day']:
            print(f"   Heat Efficiency:   {eff['heat_runtime_per_degree_day']} min/degree-day")
        print()

        # Filters
        if thermostat['filters']:
            print(f"🔧 MAINTENANCE")
            for filter_type, filter_info in thermostat['filters'].items():
                print(f"   {filter_type.title()} Filter:")
                print(f"      Last Changed:   {filter_info.get('last_changed')}")
                print(f"      Life:           {filter_info.get('life')} {filter_info.get('life_units')}")
                print(f"      Runtime:        {filter_info.get('runtime'):,} seconds")
            print()

        # Alerts
        if thermostat['active_alerts_count'] > 0:
            print(f"⚠️  ACTIVE ALERTS ({thermostat['active_alerts_count']})")
            for alert in thermostat['alerts']:
                if not alert.get('dismissed', False):
                    print(f"   [{alert.get('code')}] {alert.get('text')[:80]}")
            print()

        # System Info
        print(f"ℹ️  SYSTEM INFO")
        print(f"   Beestat ID:        {thermostat['thermostat_id']}")
        print(f"   Ecobee ID:         {thermostat['ecobee_thermostat_id']}")
        print(f"   Time Zone:         {thermostat['time_zone']}")
        print(f"   Last Sync:         {thermostat['sync_end']}")
        print(f"   Data Range:        {thermostat['data_begin']} to {thermostat['data_end']}")
        print()
        print()

    print("=" * 100)


def save_comprehensive_output(raw_data: Dict[str, Any], thermostats: List[Dict[str, Any]]) -> None:
    """
    Save comprehensive data to JSON files
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save raw response
    raw_filename = f"beestat_raw_{timestamp}.json"
    with open(raw_filename, 'w') as f:
        json.dump(raw_data, f, indent=2)
    print(f"✓ Raw data saved to: {raw_filename}")

    # Save comprehensive parsed data
    comprehensive_filename = f"beestat_comprehensive_{timestamp}.json"
    with open(comprehensive_filename, 'w') as f:
        json.dump(thermostats, f, indent=2, default=str)
    print(f"✓ Comprehensive data saved to: {comprehensive_filename}")


def main():
    """
    Main function
    """
    try:
        # Fetch raw data
        raw_data = fetch_beestat_data()

        # Parse comprehensive thermostat data
        thermostats = parse_comprehensive_thermostat_data(raw_data)

        if not thermostats:
            print("No thermostats found matching the criteria.")
            return 1

        # Display formatted data
        display_comprehensive_data(thermostats)

        # Save to JSON files
        save_comprehensive_output(raw_data, thermostats)

        print(f"\n✓ Successfully processed {len(thermostats)} thermostat(s)")
        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
