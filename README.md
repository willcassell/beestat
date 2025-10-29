# Beestat API Client

Standalone Python scripts and documentation for working with the Beestat API to retrieve Ecobee thermostat data.

**No Ecobee OAuth required!** Access your thermostat data with just a Beestat API key.

## 📁 Repository Contents

### Python Scripts
- **`fetch_beestat_fresh.py`** - ⭐ **NEW!** Uses sync API for guaranteed fresh data
- **`fetch_beestat_essential.py`** - Extract 5 key fields (temp, mode, equipment, humidity, setpoints)
- **`fetch_beestat_comprehensive.py`** - Full thermostat data with analytics and metrics
- **`fetch_beestat_simple.py`** - Basic script with minimal data extraction
- **`fetch_beestat.py`** - Alternative version using `requests` library

### Documentation
- **`ESSENTIAL_FIELDS.md`** - Field mapping and API reference for the 5 key fields
- **`API_GUIDE.md`** - Complete Beestat API documentation
- **`QUICK_REFERENCE.md`** - One-page cheat sheet
- **`SUMMARY.md`** - Project overview and findings
- **`README.md`** - This file

## ✨ Key Features

- ✅ **Single API Call** - Get all thermostat data with one request
- ✅ **No OAuth Required** - Just use your Beestat API key
- ✅ **No External Dependencies** - Pure Python standard library
- ✅ **Multiple Output Formats** - Console display and JSON files
- ✅ **Filter by Thermostat** - Show only specific thermostats
- ✅ **Comprehensive Data** - Temperature, humidity, setpoints, equipment status, weather, analytics
- ✅ **HVAC Mode Inference** - Smart detection from equipment and setpoints

## Usage

### Quick Start

**⭐ Recommended - Fresh Data with Sync API:**
```bash
python3 fetch_beestat_fresh.py
```
Uses official sync methods to guarantee fresh data (within 15 minutes of real-time).

**Comprehensive Data (may be cached):**
```bash
python3 fetch_beestat_comprehensive.py
```

**Basic Data Only:**
```bash
python3 fetch_beestat_simple.py
```

### Configuration

Edit the script to configure:

```python
# Your Beestat API key
BEESTAT_API_KEY = "your_api_key_here"

# Target thermostats to display (set to None for all)
TARGET_THERMOSTATS = ["Downstairs", "Lake"]
```

### Output

The script will:
1. Display formatted thermostat data in the console
2. Save raw API response to `beestat_raw_YYYYMMDD_HHMMSS.json`
3. Save parsed data to `beestat_parsed_YYYYMMDD_HHMMSS.json`

### Example Output

```
================================================================================
BEESTAT THERMOSTAT DATA - 2025-10-14 17:42:53
================================================================================

Thermostat: Downstairs
  ID: 14739
  Ecobee ID: 497381
  Current Temperature: 70.5°F
  Heat Setpoint: 69.2°F
  Cool Setpoint: 74.2°F
  Humidity: 56%
  HVAC Mode: None
  HVAC State: idle
  Running Equipment: []

Thermostat: Lake
  ID: 47526
  Ecobee ID: 530168
  Current Temperature: 72.6°F
  Heat Setpoint: 75°F
  Cool Setpoint: 75°F
  Humidity: 58%
  HVAC Mode: heat
  HVAC State: fan
  Running Equipment: ['fan']

================================================================================
```

## API Information

- **API Endpoint**: `https://api.beestat.io/`
- **Authentication**: API key (get yours at https://beestat.io/account)

### Primary Resource (Used by This Script)
- **Resource**: `thermostat`
- **Method**: `read_id`
- **Description**: Returns comprehensive thermostat data including current status, weather, property info, system details, efficiency metrics, and more

### Additional Available Resources

The Beestat API provides additional resources that could be called for more specialized data:

1. **runtime_thermostat_summary** - Daily summary data
   - Average/min/max temperatures (indoor/outdoor)
   - Daily runtime totals per equipment type
   - Heating/cooling degree days
   - Humidity data

2. **runtime_thermostat** - Detailed 5-minute interval data
   - High-resolution runtime data
   - Equipment state changes
   - Temperature and humidity trends
   - Limited to 31-day queries

3. **sensor** - Individual sensor data
   - Room-by-room temperature data
   - Occupancy information
   - Sensor-specific readings

4. **address** - Location details
   - GPS coordinates
   - Weather station information

**Note**: The `thermostat.read_id` resource already includes most relevant data for general use. Additional resources are useful for:
- Historical analysis (runtime_thermostat_summary)
- Detailed troubleshooting (runtime_thermostat)
- Multi-zone analysis (sensor)

## Data Fields

The comprehensive script extracts ALL available thermostat data into one record per thermostat:

### Core Status
- Current temperature, humidity, setpoints
- Running equipment and HVAC state
- Active climate/comfort setting details

### Location & Property
- GPS coordinates
- Property details (size, age, type, stories)

### Weather Data
- Current conditions (temperature, humidity, wind, pressure)
- Daily high/low temperatures
- Dew point and barometric pressure

### HVAC System Details
- System type (cooling/heating equipment)
- Number of stages
- Auxiliary heat configuration

### Program & Schedule
- All comfort settings (Home, Away, Sleep, etc.)
- Weekly schedule (48 time blocks per day)
- Active sensors per climate setting

### Efficiency & Analytics (Past Year)
- Total runtime per equipment type
- Heating/cooling degree days
- Runtime per degree day (efficiency metric)
- Temperature deltas and balance points

### Maintenance
- Filter information (last changed, life remaining)
- Active alerts and notifications
- HVAC inspection reminders

### System Information
- Sync timestamps
- Data availability range
- Time zone
- Thermostat IDs (Beestat & Ecobee)

## Requirements

- Python 3.6 or higher
- No external libraries required for `fetch_beestat_simple.py`
- `requests` library required for `fetch_beestat.py` (install with `pip3 install requests`)

## Notes

- The script tries multiple API endpoint variations to ensure compatibility
- Data is automatically filtered to show only configured target thermostats
- All temperature values are in Fahrenheit

### ⚠️ Important: Data Freshness

**Beestat API may serve cached data that is hours old!**

The scripts in this repository fetch data as-is from Beestat's cache. For real-time monitoring applications, you should:

1. **Use sync methods before fetching** - See `API_GUIDE.md` for documentation on:
   - `thermostat.sync` - Force sync thermostat data (max once per 3 min)
   - `sensor.sync` - Force sync sensor data (max once per 3 min)
   - Batch API - Combine sync calls for efficiency

2. **Implement sync-then-fetch pattern:**
   ```python
   # Step 1: Trigger sync
   sync_url = f"{API_BASE}?api_key={API_KEY}&resource=thermostat&method=sync"
   urllib.request.urlopen(sync_url)

   # Step 2: Wait for sync to complete (30 seconds)
   time.sleep(30)

   # Step 3: Fetch fresh data
   fetch_url = f"{API_BASE}?api_key={API_KEY}&resource=thermostat&method=read_id"
   response = urllib.request.urlopen(fetch_url)
   ```

3. **Check sync timestamps** - The API response includes `sync_end` field showing when data was last synced

**See `API_GUIDE.md` for complete documentation on sync methods and batch API calls.**
