# Grafana And PowerNet Notes

The Home Assistant dashboard can be used on its own.

Grafana is optional. It is useful if you store long-term data in a database and
want cost analysis, backtesting, or machine-learning features.

## Expected TimescaleDB Shape

The original PowerNet setup stores a 5-minute sample table similar to this:

```sql
CREATE TABLE powernet.power_sample_5m (
    sample_at timestamptz PRIMARY KEY,
    pv_power_kw double precision,
    pv1_power_kw double precision,
    pv2_power_kw double precision,
    pv3_power_kw double precision,
    load_power_kw double precision,
    grid_import_kw double precision,
    grid_export_kw double precision,
    battery_charge_kw double precision,
    battery_discharge_kw double precision,
    battery_soc_pct double precision,
    market_price_eur_kwh double precision,
    sample_quality smallint
);
```

The important idea is simple:

- one row every 5 minutes;
- current solar, load, grid, battery, and price values in columns;
- quality flags so training and analysis can ignore bad samples.

## Datasource

The original Grafana dashboards expect a PostgreSQL/TimescaleDB datasource.
The common datasource UID used in the private setup is:

```text
powernet-timescale
```

If your datasource has a different UID, change it before importing a Grafana
dashboard JSON.

## Why This Is Optional

Home Assistant is good for live control and daily visibility.

TimescaleDB and Grafana are better when you want:

- months or years of history;
- cost comparison between tariffs;
- solar forecast evaluation;
- machine-learning training data;
- PV string analysis over time.

You can start with Home Assistant only and add PowerNet-style long-term storage
later.
