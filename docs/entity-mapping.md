# Entity Mapping Guide

The dashboard does not care which inverter or meter you use. It only needs Home
Assistant entities that represent the right values.

All power sensors should preferably use:

```text
kW
```

All energy sensors should preferably use:

```text
kWh
```

Spot-price sensors should use:

```text
EUR/kWh
```

## Required For The Main Dashboard

| Mapping key | Meaning | Example |
|---|---|---|
| `pv_total` | Current total solar production | `sensor.inverter_pv_power` |
| `load_power` | Current home consumption | `sensor.house_load_power` |
| `grid_import` | Current power imported from the grid | `sensor.grid_import_power` |
| `grid_export` | Current power exported to the grid | `sensor.grid_export_power` |
| `battery_charge` | Current battery charging power | `sensor.battery_charge_power` |
| `battery_discharge` | Current battery discharging power | `sensor.battery_discharge_power` |
| `battery_soc` | Battery state of charge in percent | `sensor.battery_soc` |

## Daily Energy Sensors

| Mapping key | Meaning |
|---|---|
| `solar_energy_today` | Solar energy produced today |
| `load_energy_today` | Home energy consumed today |
| `grid_import_energy_today` | Imported grid energy today |
| `grid_export_energy_today` | Exported grid energy today |
| `battery_charge_energy_today` | Energy charged into the battery today |
| `battery_discharge_energy_today` | Energy discharged from the battery today |

If your inverter integration does not provide daily energy sensors, you can
create them with Home Assistant utility meters.

## PV String Sensors

| Mapping key | Meaning |
|---|---|
| `pv_string_1` | Current power of string 1 |
| `pv_string_2` | Current power of string 2 |
| `pv_string_3` | Current power of string 3 |

If you only have one or two strings, you can still use the dashboard. Either
remove the unused card after rendering or temporarily map it to an existing
string sensor.

## Forecast And Weather

| Mapping key | Meaning |
|---|---|
| `solar_forecast_now` | Current forecasted solar power |
| `solar_forecast_current_hour` | Forecasted energy for this hour |
| `solar_forecast_next_hour` | Forecasted energy for the next hour |
| `solar_forecast_today` | Forecasted solar energy today |
| `solar_forecast_tomorrow` | Forecasted solar energy tomorrow |
| `weather_entity` | Home Assistant weather entity |
| `sun_entity` | Usually `sun.sun` |

Common integrations are Forecast.Solar, Solcast, Open-Meteo based helpers, or
other solar forecasting integrations.

## Spot Price

| Mapping key | Meaning |
|---|---|
| `spot_price_now` | Current electricity spot price |
| `spot_price_next` | Next price interval |
| `spot_price_low` | Lowest price today |
| `spot_price_high` | Highest price today |
| `monthly_grid_cost` | Optional helper for monthly grid energy cost |

Nord Pool is a common source in Europe. Other dynamic-tariff integrations can
work as long as they provide similar sensors.

## Inverter And Temperature

| Mapping key | Meaning |
|---|---|
| `inverter_state` | Text/state sensor for the inverter |
| `inverter_temperature` | Inverter temperature |
| `battery_temperature` | Battery temperature |

These are used for status and troubleshooting cards. They do not affect the
main energy calculations.
