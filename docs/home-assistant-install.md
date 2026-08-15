# Home Assistant Installation

This guide is written for people who are comfortable copying files and editing
Home Assistant entity IDs, but do not want to read the dashboard JSON by hand.

## 1. Install The Custom Cards

The dashboard uses two common custom cards:

- `apexcharts-card`
- `power-flow-card-plus`

The easiest way to install them is through HACS.

1. Open Home Assistant.
2. Go to HACS.
3. Search for `apexcharts-card` and install it.
4. Search for `power-flow-card-plus` and install it.
5. Restart Home Assistant if HACS asks you to.

## 2. Install The Solar Roof Card

Copy this file into your Home Assistant `www` folder:

```text
home-assistant/solar-roof-card.js
```

Recommended target path:

```text
/config/www/community/solar-roof-card/solar-roof-card.js
```

Then add this Lovelace resource:

```text
/local/community/solar-roof-card/solar-roof-card.js
```

In Home Assistant you can add it under:

```text
Settings -> Dashboards -> Resources
```

Choose:

```text
Resource type: JavaScript module
```

## 3. Prepare Your Entity Mapping

Copy:

```text
home-assistant/entities.example.yaml
```

to:

```text
entities.yaml
```

Then replace the example entity IDs with your own Home Assistant sensors.

Example:

```yaml
pv_total: sensor.my_inverter_solar_power
load_power: sensor.my_home_load
grid_import: sensor.my_grid_import
grid_export: sensor.my_grid_export
battery_soc: sensor.my_battery_percent
```

The full mapping is explained in [entity-mapping.md](entity-mapping.md).

## 4. Render The Dashboard

From the repository folder, run:

```bash
python home-assistant/render-dashboard.py \
  --entities entities.yaml \
  --template home-assistant/energy-solar-dashboard.template.json \
  --output energy-solar-dashboard.json
```

If you see a message like this, it worked:

```text
Rendered energy-solar-dashboard.json
```

## 5. Import Into Home Assistant

There are several ways to import a dashboard. The most beginner-friendly way is:

1. Open Home Assistant.
2. Go to `Settings -> Dashboards`.
3. Create a new dashboard.
4. Open the dashboard.
5. Open the three-dot menu.
6. Choose `Raw configuration editor`.
7. Paste the contents of `energy-solar-dashboard.json`.
8. Save.

If a card shows an error, check the card message first. Most problems are
caused by a missing custom card or a wrong entity ID.

## Need To Find Your Inverter First?

If you do not know the local IP address of your inverter, see:

```text
docs/modbus-discovery.md
```

The included discovery script safely checks your local network for devices with
Modbus TCP port 502 open.

## Optional: Start With Fewer Sensors

You do not need every optional feature on day one. If you do not have a solar
forecast or spot-price sensor yet, you can still render the dashboard by mapping
those fields to temporary helper sensors. Later, replace them with real sensors.

For a clean public dashboard, the template keeps all sections in one file. You
can remove sections you do not use after rendering.
