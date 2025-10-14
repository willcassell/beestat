# Beestat API - Quick Reference Card

## 🚀 Quick Start

```bash
cd /Users/wcassell/Projects/beestat
python3 fetch_beestat_comprehensive.py
```

## 📁 Files

| File | Purpose |
|------|---------|
| `fetch_beestat_comprehensive.py` | ⭐ **Main script** - Gets ALL thermostat data |
| `fetch_beestat_simple.py` | Basic version with limited data |
| `README.md` | Full user documentation |
| `API_GUIDE.md` | Complete API reference |
| `SUMMARY.md` | Project overview |
| `QUICK_REFERENCE.md` | This file |

## 🔑 API Key

Your API key: `e1984530c9b7d61e838c470e451b5c16856dbd40`
Get new keys at: https://beestat.io/account

## 🌐 API Endpoint (Single Call Gets Everything!)

```
https://api.beestat.io/?api_key={KEY}&resource=thermostat&method=read_id
```

## 📊 Data Retrieved Per Thermostat

| Category | Data Points |
|----------|-------------|
| **Current Status** | Temperature, humidity, setpoints, running equipment, HVAC state |
| **Weather** | Outdoor temp, conditions, wind, pressure, humidity |
| **Location** | GPS coordinates, property details (size, age, type) |
| **System** | Equipment types, stages, configuration |
| **Programs** | All comfort settings, weekly schedule, sensors |
| **Analytics** | Runtime totals, degree days, efficiency metrics |
| **Maintenance** | Filter status, alerts, reminders |
| **Timestamps** | Sync times, data range, time zone |

## 🏠 Your Thermostats

### Home - Downstairs
- Location: Richmond area (37.52465, -77.63107)
- 3000 sq ft, 2-story detached, 17 years old
- Beestat ID: 14739
- Ecobee ID: 497381

### Lake - 809 Sailors Cove
- Location: Roanoke area (37.05319, -79.61242)
- 1000 sq ft, 2-story condo, 45 years old
- Beestat ID: 47526
- Ecobee ID: 530168

## 📤 Output Files

Each run creates:
- `beestat_raw_{timestamp}.json` - Complete API response
- `beestat_comprehensive_{timestamp}.json` - Parsed data

## 🔧 Configuration

Edit these variables in the script:

```python
BEESTAT_API_KEY = "your_key_here"
TARGET_THERMOSTATS = ["Downstairs", "809 Sailors Cove"]  # or None for all
```

## 📋 Sample Data Structure

```json
{
  "thermostat_id": 14739,
  "name": "Downstairs",
  "temperature": 70.7,
  "humidity": 57,
  "setpoint_heat": 69.2,
  "setpoint_cool": 74.2,
  "running_equipment": [],
  "hvac_state": "idle",
  "location": {"latitude": 37.52465, "longitude": -77.63107},
  "weather": {...},
  "property": {...},
  "system_type": {...},
  "program": {...},
  "efficiency_metrics": {...},
  "filters": {...},
  "alerts": [...]
}
```

## ⚡ Key Features

✅ Single API call gets everything
✅ No external dependencies (pure Python)
✅ Human-readable console output
✅ Machine-readable JSON output
✅ Efficiency metrics calculated
✅ Current weather included
✅ Maintenance alerts tracked
✅ Historical analytics (1 year)

## ❓ Do I Need Other API Calls?

**No!** For thermostat monitoring, one call does it all.

Other resources exist but are rarely needed:
- `runtime_thermostat_summary` - Daily historical (specialized use)
- `runtime_thermostat` - 5-min intervals (debugging only)
- `sensor` - Room sensors (data already in climates)

## 🔄 Recommended Polling

- Every 5-15 minutes is fine
- Beestat syncs from Ecobee every 5 minutes
- Faster polling won't get newer data

## 📚 Resources

- Beestat: https://beestat.io/
- API Keys: https://beestat.io/account
- Community: https://community.beestat.io/
- GitHub: https://github.com/beestat/app

## 💡 Pro Tips

1. **Run script regularly** - Set up cron job for automatic updates
2. **Store JSON files** - Build historical database
3. **Monitor alerts** - Check `active_alerts_count` field
4. **Compare properties** - Efficiency metrics show which is more efficient
5. **Track filter changes** - Use `filters` data for maintenance reminders

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| 404 Error | Use `api.beestat.io` (not `beestat.io/api`) |
| No thermostats | Check `TARGET_THERMOSTATS` filter |
| Old data | Beestat syncs every 5 min, some lag is normal |
| Missing fields | Check if thermostat has that feature |

## 🎯 One-Liner Summary

**One API call (`thermostat.read_id`) returns everything you need: current status, weather, property info, system details, one year of analytics, maintenance alerts, and complete program schedules.**
