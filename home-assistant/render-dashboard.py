#!/usr/bin/env python3
"""Render the PowerNet Home Assistant dashboard template.

The template uses placeholders such as {{PV_TOTAL}}. This script reads a simple
YAML mapping file and replaces those placeholders with your Home Assistant
entity IDs.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: PyYAML. Install it with: python -m pip install pyyaml"
    ) from exc


PLACEHOLDERS = {
    "PV_TOTAL": "pv_total",
    "PV_STRING_1": "pv_string_1",
    "PV_STRING_2": "pv_string_2",
    "PV_STRING_3": "pv_string_3",
    "LOAD_POWER": "load_power",
    "GRID_IMPORT": "grid_import",
    "GRID_EXPORT": "grid_export",
    "BATTERY_CHARGE": "battery_charge",
    "BATTERY_DISCHARGE": "battery_discharge",
    "BATTERY_SOC": "battery_soc",
    "SOLAR_ENERGY_TODAY": "solar_energy_today",
    "LOAD_ENERGY_TODAY": "load_energy_today",
    "GRID_IMPORT_ENERGY_TODAY": "grid_import_energy_today",
    "GRID_EXPORT_ENERGY_TODAY": "grid_export_energy_today",
    "BATTERY_CHARGE_ENERGY_TODAY": "battery_charge_energy_today",
    "BATTERY_DISCHARGE_ENERGY_TODAY": "battery_discharge_energy_today",
    "SPOT_PRICE_NOW": "spot_price_now",
    "SPOT_PRICE_NEXT": "spot_price_next",
    "SPOT_PRICE_LOW": "spot_price_low",
    "SPOT_PRICE_HIGH": "spot_price_high",
    "MONTHLY_GRID_COST": "monthly_grid_cost",
    "SOLAR_FORECAST_NOW": "solar_forecast_now",
    "SOLAR_FORECAST_CURRENT_HOUR": "solar_forecast_current_hour",
    "SOLAR_FORECAST_NEXT_HOUR": "solar_forecast_next_hour",
    "SOLAR_FORECAST_TODAY": "solar_forecast_today",
    "SOLAR_FORECAST_TOMORROW": "solar_forecast_tomorrow",
    "WEATHER_ENTITY": "weather_entity",
    "SUN_ENTITY": "sun_entity",
    "INVERTER_STATE": "inverter_state",
    "INVERTER_TEMPERATURE": "inverter_temperature",
    "BATTERY_TEMPERATURE": "battery_temperature",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entities", required=True, type=Path)
    parser.add_argument("--template", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mapping = yaml.safe_load(args.entities.read_text(encoding="utf-8")) or {}
    template = args.template.read_text(encoding="utf-8")

    missing_keys = [
        key for key in PLACEHOLDERS.values()
        if key not in mapping or not str(mapping[key]).strip()
    ]
    if missing_keys:
        print("Missing entity mappings:", ", ".join(missing_keys), file=sys.stderr)
        return 2

    rendered = template
    for placeholder, key in PLACEHOLDERS.items():
        rendered = rendered.replace("{{" + placeholder + "}}", str(mapping[key]))

    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", rendered)))
    if unresolved:
        print("Unresolved placeholders:", ", ".join(unresolved), file=sys.stderr)
        return 3

    args.output.write_text(rendered, encoding="utf-8")
    print(f"Rendered {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
