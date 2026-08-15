# Safe Modbus TCP Discovery

Many solar inverters expose local data through Modbus TCP. This is useful for
Home Assistant because it can provide fast, local, cloud-free values such as PV
power, battery state, grid import/export, and inverter temperature.

This repository includes a small discovery tool to help you find likely Modbus
TCP devices on your own LAN.

## Safety First

The default scan is intentionally boring and safe:

- it only scans private local network ranges;
- it only checks TCP port `502`;
- it does not read Modbus registers;
- it does not write anything;
- it refuses broad scans larger than 1024 addresses;
- it refuses public internet ranges.

Optional `--modbus-probe` sends a read-only "device identification" request.
This is still not a write operation, but it is disabled by default because old
or badly implemented devices can behave strangely.

## Find Your Local Network Range

Most home networks use a private range. Your router or network settings will
show the exact value.

```text
<your-lan-cidr>
```

If your router address ends in `.1`, your range often ends in `.0/24`.
For example, a router at:

```text
<router-ip-ending-in-1>
```

usually means a scan range like:

```text
<same-network-ending-in-0/24>
```

## Windows

Open PowerShell in the repository folder:

```powershell
.\scripts\discover-modbus-tcp.ps1 -Cidr <your-lan-cidr>
```

With the optional read-only Modbus identification probe:

```powershell
.\scripts\discover-modbus-tcp.ps1 -Cidr <your-lan-cidr> -ModbusProbe
```

## Linux Or macOS

Run:

```bash
python scripts/discover-modbus-tcp.py --cidr <your-lan-cidr>
```

With the optional read-only Modbus identification probe:

```bash
python scripts/discover-modbus-tcp.py --cidr <your-lan-cidr> --modbus-probe
```

## Example Output

```text
IP address       Port  TCP open  Modbus device-id  Device information
---------------  ----  --------  ----------------  ------------------
<inverter-ip>    502   yes       not tested
```

This means a device at `<inverter-ip>` accepts connections on Modbus TCP port
502. It might be your inverter, energy meter, battery, gateway, or another
Modbus-capable device.

## What To Do Next

Once you found a candidate IP address:

1. Check your inverter manual for Modbus TCP support.
2. Check whether Modbus TCP must be enabled in the inverter app or web UI.
3. Add the IP address to your Home Assistant inverter integration.
4. Use the vendor documentation to choose the correct unit/slave ID.

Typical Home Assistant settings look like this:

```text
Host: <inverter-ip>
Port: 502
Type: TCP
Unit/Slave ID: depends on your inverter
```

## Important Warning

This discovery tool does not tell you which Modbus registers are safe or useful.
Register maps are vendor-specific. Reading the wrong register is usually safe,
but writing to registers can change inverter settings.

For dashboards, monitoring, and prediction models, you normally only need
read-only values.

Avoid write access unless you fully understand your inverter documentation.
