# Troubleshooting

## A Card Says "Custom Element Doesn't Exist"

The custom card is missing.

Check that you installed:

- `apexcharts-card`
- `power-flow-card-plus`
- `solar-roof-card.js`

Also check that the Lovelace resource path is correct.

## The Dashboard Shows Empty Values

The most common cause is a wrong entity ID.

Open `entities.yaml` and compare every value with the entity IDs shown in Home
Assistant under:

```text
Settings -> Devices & services -> Entities
```

## The Power Flow Direction Looks Wrong

Some integrations use positive numbers for import/export differently. The
dashboard expects:

- grid import as a positive import sensor;
- grid export as a positive export/feed-in sensor;
- battery charge as a positive charging sensor;
- battery discharge as a positive discharging sensor.

If your integration exposes one signed sensor instead of two separate sensors,
create Home Assistant template sensors that split it into two positive values.

## Forecast Looks Too High Or Too Low

Some forecast integrations report watts, others report kilowatts. The dashboard
expects the live forecast sensor to be watts in the comparison chart and divides
it by 1000 for kW display.

If your forecast already reports kW, remove this transform from the rendered
dashboard:

```text
return Number(x) / 1000;
```

## PV String Gauges Have The Wrong Scale

The template uses simple defaults:

```text
PV1 max: 2 kW
PV2 max: 6 kW
PV3 max: 3 kW
```

After rendering, adjust the `max` values to match your real strings.
