# Grafana

This folder is intentionally small for the first public export.

The Home Assistant dashboard is the main reusable artifact. Grafana support is
documented in [../docs/grafana-powernet.md](../docs/grafana-powernet.md), because
Grafana dashboards depend more heavily on the user's database schema and
datasource UID.

The expected datasource UID in the original setup was:

```text
powernet-timescale
```

The expected table is:

```text
powernet.power_sample_5m
```

A fully generic Grafana dashboard template can be added once the public schema
has stabilized.
