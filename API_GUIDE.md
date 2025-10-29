# Beestat API Complete Guide

## Overview

The Beestat API provides access to comprehensive Ecobee thermostat data without needing to authenticate directly with Ecobee. All you need is a Beestat API key.

## Getting Your API Key

1. Visit https://beestat.io/account
2. Log in with your Beestat account (linked to your Ecobee)
3. Generate an API key
4. The key never expires!

## API Endpoint

```
https://api.beestat.io/
```

## Authentication

Pass your API key as a query parameter:
```
?api_key=YOUR_API_KEY_HERE
```

---

## Single API Call for Complete Thermostat Data

### Resource: `thermostat.read_id`

**This is the primary endpoint you need** - it returns ALL thermostat data in one call!

#### URL Format
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=thermostat&method=read_id
```

#### What You Get

This single API call returns everything about your thermostats:

##### ✅ Real-Time Status
- Current temperature, humidity, setpoints
- Running equipment (what's actively heating/cooling)
- HVAC state (idle, heating, cooling, fan)
- Active climate/comfort setting

##### ✅ Location & Property
- GPS coordinates (latitude/longitude)
- Property details (size, age, type, number of stories)
- Address ID

##### ✅ Current Weather
- Outdoor temperature (current, high, low)
- Humidity, dew point
- Wind speed and direction
- Barometric pressure
- Weather condition (sunny, cloudy, etc.)

##### ✅ HVAC System Configuration
- Detected system type (compressor, geothermal, etc.)
- Number of cooling stages
- Number of heating stages
- Auxiliary heat type and stages
- System differentials (deadband settings)

##### ✅ Comfort Settings (Programs)
- All climate definitions (Home, Away, Sleep, etc.)
- Temperature settings for each climate
- Active sensors for each climate
- Current active climate
- Full weekly schedule (7 days × 48 half-hour blocks)

##### ✅ Historical Analytics (Past Year)
- Total runtime per equipment type (minutes)
- Heating and cooling degree days
- Runtime per degree day (efficiency metric)
- Temperature deltas (how fast system heats/cools)
- Balance points
- Average setpoints and setbacks

##### ✅ Maintenance Information
- Filter data (type, last changed date, remaining life)
- Runtime totals
- Active alerts and reminders
- System inspection notifications

##### ✅ System Information
- Thermostat IDs (Beestat and Ecobee)
- User ID
- Time zone
- First connected date
- Last sync timestamp
- Data availability range
- Active/inactive status

#### Example Response Structure

```json
{
  "success": true,
  "data": {
    "12345": {
      "thermostat_id": 12345,
      "ecobee_thermostat_id": 498765,
      "name": "Downstairs",
      "temperature": 72.5,
      "humidity": 45,
      "setpoint_heat": 68.0,
      "setpoint_cool": 76.0,
      "running_equipment": ["fan"],
      "weather": { ... },
      "property": { ... },
      "system_type": { ... },
      "program": { ... },
      "profile": { ... },
      "filters": { ... },
      "alerts": [ ... ]
    }
  }
}
```

---

## Optional: Additional API Resources

These are **NOT required** for general thermostat monitoring, but provide specialized historical data:

### 1. Daily Summaries: `runtime_thermostat_summary.read_id`

For day-by-day historical analysis.

#### URL Format
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=runtime_thermostat_summary&method=read_id&arguments={"attributes":{"thermostat_id":12345,"date":"2025-10-01"}}
```

#### Returns
- Daily average/min/max temperatures (indoor/outdoor)
- Daily runtime totals for each equipment type
- Daily heating/cooling degree days
- Daily humidity averages

#### Use Cases
- Tracking efficiency over time
- Comparing performance across seasons
- Generating monthly reports

---

### 2. 5-Minute Intervals: `runtime_thermostat.read_id`

For detailed troubleshooting and analysis.

#### URL Format
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=runtime_thermostat&method=read_id&arguments={"attributes":{"thermostat_id":12345,"timestamp":{"value":["2025-10-01 00:00:00","2025-10-02 00:00:00"],"operator":"between"}}}
```

#### Returns
- 5-minute interval data points
- Equipment state changes
- Temperature trends
- Outdoor conditions

#### Limitations
- Limited to 31-day queries
- Large data volumes

#### Use Cases
- Debugging short-cycling issues
- Analyzing system response times
- Detailed energy audits

---

### 3. Sensor Data: `sensor.read_id`

For multi-zone temperature analysis.

#### URL Format
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=sensor&method=read_id&arguments={"attributes":{"thermostat_id":12345}}
```

#### Returns
- Individual room sensor readings
- Sensor names and IDs
- Occupancy data (for sensors that support it)
- Temperature readings per room

#### Use Cases
- Multi-zone temperature monitoring
- Room-by-room comfort analysis
- Identifying hot/cold spots

**Note**: Basic sensor information is already included in the `thermostat.read_id` response within the program climates.

---

## Recommendation

**For most use cases, you only need one API call:**

```python
endpoint = f"https://api.beestat.io/?api_key={API_KEY}&resource=thermostat&method=read_id"
```

This returns all the thermostat data you need including:
- Current status
- Weather
- Property info
- System details
- Historical analytics
- Maintenance alerts
- Schedule and programs

The additional resources (`runtime_thermostat_summary`, `runtime_thermostat`, `sensor`) are only needed for:
- Historical trend analysis
- Detailed troubleshooting
- Room-by-room sensor data

---

## Forcing Fresh Data with Sync Methods

**IMPORTANT**: Beestat API serves cached data that can be hours old. Use sync methods to force fresh updates!

### Official Sync Methods

Beestat provides official sync methods to force immediate data updates from Ecobee:

#### 1. Thermostat Sync: `thermostat.sync`

Force Beestat to sync your thermostats from Ecobee immediately.

**URL Format:**
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=thermostat&method=sync
```

**Rate Limit:** Maximum once per 3 minutes

**Use Case:** Before fetching current thermostat data to ensure it's fresh

#### 2. Sensor Sync: `sensor.sync`

Force Beestat to sync your sensor data from Ecobee immediately.

**URL Format:**
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=sensor&method=sync
```

**Rate Limit:** Maximum once per 3 minutes

**Use Case:** Before fetching room sensor data

#### 3. Runtime Sync: `runtime.sync`

Force Beestat to sync historical runtime data from Ecobee.

**URL Format:**
```
https://api.beestat.io/?api_key=YOUR_KEY&resource=runtime&method=sync&arguments={"thermostat_id":12345}
```

**Rate Limit:** Maximum once per 15 minutes

**Use Case:** Before analyzing historical runtime data

---

## Batch API Calls

**Make multiple API calls in a single HTTP request for better performance!**

### Batch Format

Instead of making separate API calls, batch them together:

```
https://api.beestat.io/?api_key=YOUR_KEY&batch=[
  {"resource":"thermostat","method":"sync","alias":"thermostat_sync"},
  {"resource":"sensor","method":"sync","alias":"sensor_sync"}
]
```

### Batch Response Format

```json
{
  "thermostat_sync": {
    "success": true,
    "data": {...}
  },
  "sensor_sync": {
    "success": true,
    "data": {...}
  }
}
```

### Benefits of Batching

- ✅ Single HTTP connection (faster)
- ✅ Reduced API overhead
- ✅ Atomic operation (all succeed or fail together)
- ✅ Cleaner code

### Example: Sync + Fetch Pattern (Recommended)

For fresh data, use this two-step pattern:

**Step 1: Trigger sync (batched)**
```python
import json
import urllib.request

batch = [
    {"resource": "thermostat", "method": "sync", "alias": "thermostat_sync"},
    {"resource": "sensor", "method": "sync", "alias": "sensor_sync"}
]

url = f"https://api.beestat.io/?api_key={API_KEY}&batch={json.dumps(batch)}"
urllib.request.urlopen(url)
```

**Step 2: Wait briefly (30 seconds), then fetch data**
```python
import time
time.sleep(30)

url = f"https://api.beestat.io/?api_key={API_KEY}&resource=thermostat&method=read_id"
response = urllib.request.urlopen(url)
data = json.loads(response.read())
```

**Why this matters:**
- Without sync: Data can be hours old
- With sync: Data is fresh (within 15 minutes of Ecobee's last update)
- Ecobee updates every 15 minutes, so sync gets the latest available data

---

## Rate Limits

Beestat API has rate limiting to prevent abuse:
- **Read operations**: Reasonable polling (every 5-15 minutes) is fine
- **Sync operations**:
  - thermostat.sync / sensor.sync: Max once per 3 minutes
  - runtime.sync: Max once per 15 minutes
- More frequent requests won't give newer data due to Ecobee's update cycle

## Data Freshness

**Without sync methods:**
- Cached data can be hours or days old
- Beestat syncs automatically "based on user activity"
- Website visits trigger syncs, but API calls don't

**With sync methods (recommended):**
- Force immediate sync from Ecobee
- Data freshness within 15 minutes (Ecobee's update interval)
- Ecobee thermostats report to cloud every 15 minutes
- Weather data updates regularly
- Historical analytics calculated daily

## Support

- Beestat Community: https://community.beestat.io/
- Documentation: https://beestat.notion.site/
- GitHub: https://github.com/beestat/app
