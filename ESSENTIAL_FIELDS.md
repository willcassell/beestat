# Beestat Essential Fields - Quick Reference

## The 5 Essential Thermostat Fields

### API Call Required: **Just ONE!**

```
GET https://api.beestat.io/?api_key={KEY}&resource=thermostat&method=read_id
```

---

## Field Mapping

| # | Field You Want | API Response Path | Notes |
|---|----------------|-------------------|-------|
| 1 | **Current Temperature (°F)** | `data[id]['temperature']` | ✅ Direct field |
| 2 | **HVAC Mode** | *INFERRED* | ⚠️ Not provided directly - must infer |
| 3 | **Running Equipment** | `data[id]['running_equipment']` | ✅ Direct field (array) |
| 4 | **Current Humidity (%)** | `data[id]['humidity']` | ✅ Direct field |
| 5 | **Temperature Setpoints (°F)** | `data[id]['setpoint_heat']`<br>`data[id]['setpoint_cool']` | ✅ Direct fields |

---

## HVAC Mode Inference Logic

**Problem**: The Beestat API does not return the HVAC mode (`heat`, `cool`, `auto`, `off`) directly.

**Solution**: Infer it from running equipment and setpoints:

```python
def infer_hvac_mode(thermostat):
    running_equipment = thermostat['running_equipment']
    heat_setpoint = thermostat['setpoint_heat']
    cool_setpoint = thermostat['setpoint_cool']

    # Check what's running (most accurate)
    for equipment in running_equipment:
        if 'cool' in equipment.lower():
            return 'cool'
        elif 'heat' in equipment.lower():
            return 'heat'

    # If nothing running, check setpoints
    if heat_setpoint and cool_setpoint:
        if heat_setpoint == cool_setpoint:
            return 'auto'  # or specific mode (can't determine)
        else:
            return 'auto'  # Different setpoints = auto mode
    elif heat_setpoint and not cool_setpoint:
        return 'heat'
    elif cool_setpoint and not heat_setpoint:
        return 'cool'
    else:
        return 'auto'  # default
```

---

## Example API Response

```json
{
  "success": true,
  "data": {
    "14739": {
      "thermostat_id": 14739,
      "name": "Downstairs",
      "temperature": 70.7,                    // ✅ Field #1
      "humidity": 57,                         // ✅ Field #4
      "setpoint_heat": 69.2,                  // ✅ Field #5a
      "setpoint_cool": 74.2,                  // ✅ Field #5b
      "running_equipment": [],                // ✅ Field #3
      "temperature_unit": "°F",
      // ... many other fields ...
    }
  }
}
```

---

## Extracted Essential Data

```json
{
  "thermostat_id": 14739,
  "name": "Downstairs",
  "current_temperature_f": 70.7,          // #1
  "hvac_mode": "auto",                    // #2 (inferred)
  "running_equipment": [],                // #3
  "equipment_state": "idle",
  "current_humidity_percent": 57,         // #4
  "heat_setpoint_f": 69.2,                // #5
  "cool_setpoint_f": 74.2,                // #5
  "timestamp": "2025-10-14T18:03:11"
}
```

---

## Usage

### Run the Script
```bash
python3 fetch_beestat_essential.py
```

### Output
1. **Console Display**: Formatted, readable output with all 5 fields
2. **JSON File**: `beestat_essential_{timestamp}.json` - Machine-readable data

---

## Example Output

```
📍 Downstairs (ID: 14739)

   1️⃣  Current Temperature:  70.7°F
   2️⃣  HVAC Mode:            AUTO
   3️⃣  Running Equipment:    idle
   4️⃣  Current Humidity:     57%
   5️⃣  Temperature Setpoints:
       └─ Heat: 69.2°F
       └─ Cool: 74.2°F
```

---

## Field Details

### 1. Current Temperature
- **Units**: Fahrenheit (°F)
- **Precision**: 0.1°F
- **Update Frequency**: Every 5 minutes (Beestat sync interval)

### 2. HVAC Mode
- **Possible Values**: `heat`, `cool`, `auto`, `off`
- **Source**: Inferred (not directly provided)
- **Inference Priority**:
  1. Running equipment (most accurate)
  2. Setpoint configuration (fallback)

### 3. Running Equipment
- **Type**: Array of strings
- **Possible Values**:
  - `[]` - Nothing running (idle)
  - `["fan"]` - Fan only
  - `["compCool1"]` - Cooling stage 1
  - `["compHeat1"]` - Heating stage 1
  - `["auxHeat1"]` - Auxiliary heat
  - Multiple items for multi-stage systems

### 4. Current Humidity
- **Units**: Percent (%)
- **Range**: 0-100
- **Precision**: 1%

### 5. Temperature Setpoints
- **Units**: Fahrenheit (°F)
- **Precision**: 0.1°F
- **Fields**:
  - `heat_setpoint_f` - Heating setpoint
  - `cool_setpoint_f` - Cooling setpoint
- **Notes**:
  - In auto mode: Both setpoints active
  - In heat mode: Only heat setpoint relevant
  - In cool mode: Only cool setpoint relevant
  - If equal: Likely in specific mode set to that temp

---

## Important Notes

### Why Isn't HVAC Mode Provided?

The Beestat API appears to not include the `hvac_mode` or `settings.hvacMode` field in the response. This could be:
1. **API limitation**: Not exposed by Beestat
2. **Ecobee sync issue**: Field not synced from Ecobee
3. **Privacy/design choice**: Intentionally omitted

### Alternative: Direct Ecobee API

If you need the actual HVAC mode setting (not inferred), you would need to:
1. Use the Ecobee API directly (requires OAuth)
2. Call the `thermostat` endpoint with `includeSettings: true`
3. Read the `settings.hvacMode` field

However, for most monitoring purposes, the inferred mode based on running equipment is sufficient and more accurate (shows what the system is *actually doing* rather than just the mode setting).

---

## Configuration

Edit `fetch_beestat_essential.py`:

```python
# Your API key
BEESTAT_API_KEY = "your_key_here"

# Filter to specific thermostats (or None for all)
TARGET_THERMOSTATS = ["Downstairs", "809 Sailors Cove"]
```

---

## Summary

✅ **Found**: 4 of 5 fields directly in API response
⚠️ **Inferred**: HVAC mode (logic provided)
📡 **API Calls Needed**: **Just 1** - `thermostat.read_id`
🔄 **Update Frequency**: Every 5-15 minutes (Beestat syncs every 5 min)
📊 **Data Format**: Clean JSON with only essential fields

---

## Files

- `fetch_beestat_essential.py` - Script to extract the 5 fields
- `beestat_essential_{timestamp}.json` - Output file
- `ESSENTIAL_FIELDS.md` - This documentation
