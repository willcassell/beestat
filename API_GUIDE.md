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

## Rate Limits

Beestat API has rate limiting to prevent abuse:
- Reasonable polling intervals (every 5-15 minutes) are fine
- Data is synced from Ecobee every 5 minutes
- More frequent requests won't give you newer data

## Data Freshness

- Beestat syncs with Ecobee every 5 minutes
- Weather data is updated regularly
- Historical analytics are calculated daily
- Some lag compared to direct Ecobee API access

## Support

- Beestat Community: https://community.beestat.io/
- Documentation: https://beestat.notion.site/
- GitHub: https://github.com/beestat/app
