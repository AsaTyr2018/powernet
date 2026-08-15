# PowerNet Energy Dashboard Pack

PowerNet is a small dashboard pack for people who want a clear Home Assistant
energy dashboard for solar production, home consumption, grid import/export,
battery flow, spot prices, and PV string visibility.

It started as a private solar dashboard and was cleaned up into templates so it
can be reused without copying someone else's server names, IP addresses, or
private Home Assistant setup.

## What You Get

- A Home Assistant Energy/Solar dashboard template.
- A custom `solar-roof-card` for a simple live roof/string visualization.
- An entity mapping file so you can connect the dashboard to your own sensors.
- Optional Grafana/PowerNet notes for people who also store energy data in
  TimescaleDB.

## Who This Is For

This pack is useful if you already have Home Assistant sensors for:

- current solar production;
- home/load consumption;
- grid import and grid export;
- battery charge, discharge, and state of charge;
- optional PV string power values;
- optional spot market price;
- optional solar forecast.

You do not need to use the same inverter as the original setup. The dashboard
uses your own entity IDs through a mapping file.

## Quick Start

1. Install the required Home Assistant custom cards:
   - `apexcharts-card`
   - `power-flow-card-plus`
   - the included `solar-roof-card.js`
2. Copy `home-assistant/entities.example.yaml` to `entities.yaml`.
3. Replace the example entity IDs in `entities.yaml` with your own Home
   Assistant sensors.
4. Render the dashboard:

   ```bash
   python home-assistant/render-dashboard.py \
     --entities entities.yaml \
     --template home-assistant/energy-solar-dashboard.template.json \
     --output energy-solar-dashboard.json
   ```

5. Import the rendered JSON into a Home Assistant Lovelace dashboard.

For friendly step-by-step instructions, see:

- [Home Assistant installation](docs/home-assistant-install.md)
- [Entity mapping guide](docs/entity-mapping.md)
- [Safe Modbus TCP discovery](docs/modbus-discovery.md)
- [Grafana and PowerNet notes](docs/grafana-powernet.md)

## Required Home Assistant Integrations

The dashboard does not require a specific vendor. It only needs sensors with
compatible meanings and units.

Common sources include:

- inverter integrations such as FoxESS, Fronius, SMA, Huawei, Solis, Victron;
- the Home Assistant Energy dashboard helpers;
- Nord Pool or another spot-price integration;
- Forecast.Solar or another solar forecast integration;
- Ecowitt or another local weather station, optional.

## Privacy

This repository intentionally does not contain:

- private URLs;
- IP addresses;
- credentials;
- mail, alerting, or admin settings;
- network operations dashboards;
- cluster-specific deployment details.

## Status

This is an export-ready dashboard pack, not a one-click Home Assistant add-on.
The first goal is to make the dashboard understandable, portable, and safe to
share. A nicer UI-based installer may come later.

## License

MIT. See [LICENSE](LICENSE).
