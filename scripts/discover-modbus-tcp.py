#!/usr/bin/env python3
"""Safely discover local Modbus TCP candidates.

Default mode only checks whether TCP port 502 is open on local/private IP
addresses. It does not read registers and it never writes anything.

Optional --modbus-probe sends a Modbus "Read Device Identification" request.
This is still read-only, but it is disabled by default because some old devices
are fragile or badly implemented.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import ipaddress
import json
import socket
import struct
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


SAFE_PORTS = {502}
RFC1918_V4 = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
]


@dataclass
class Candidate:
    ip: str
    port: int
    tcp_open: bool
    modbus_device_id_ok: bool | None = None
    device_id: str | None = None
    error: str | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Safely find local devices with Modbus TCP port 502 open.",
    )
    parser.add_argument(
        "--cidr",
        action="append",
        required=True,
        help="Private local network to scan, for example <your-lan-cidr>. "
        "May be used multiple times.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=502,
        help="TCP port to check. Default: 502.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0.7,
        help="TCP timeout in seconds. Default: 0.7.",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=64,
        help="Maximum parallel connection checks. Default: 64.",
    )
    parser.add_argument(
        "--modbus-probe",
        action="store_true",
        help="Also send a read-only Modbus device identification request.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a table.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional file path for JSON results.",
    )
    return parser.parse_args()


def validate_networks(cidrs: list[str], port: int) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
    if port not in SAFE_PORTS:
        raise SystemExit(
            f"Refusing to scan port {port}. This tool is intentionally limited to {sorted(SAFE_PORTS)}."
        )

    networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network] = []
    for cidr in cidrs:
        try:
            network = ipaddress.ip_network(cidr, strict=False)
        except ValueError as exc:
            raise SystemExit(f"Invalid CIDR {cidr!r}: {exc}") from exc

        allowed_lan = False
        if isinstance(network, ipaddress.IPv4Network):
            allowed_lan = any(network.subnet_of(allowed) for allowed in RFC1918_V4)
        else:
            allowed_lan = network.is_private and not network.is_loopback and not network.is_link_local

        if not allowed_lan:
            raise SystemExit(
                f"Refusing to scan non-LAN network {network}. "
                "Use only your own local LAN range, for example <your-lan-cidr>."
            )
        if network.num_addresses > 1024:
            raise SystemExit(
                f"Refusing to scan {network}: {network.num_addresses} addresses is too broad. "
                "Use a /24 or smaller range."
            )
        networks.append(network)
    return networks


def iter_hosts(networks: list[ipaddress.IPv4Network | ipaddress.IPv6Network]) -> list[str]:
    hosts: list[str] = []
    seen: set[str] = set()
    for network in networks:
        for host in network.hosts():
            ip = str(host)
            if ip not in seen:
                seen.add(ip)
                hosts.append(ip)
    return hosts


def check_tcp(ip: str, port: int, timeout: float) -> Candidate:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return Candidate(ip=ip, port=port, tcp_open=True)
    except TimeoutError:
        return Candidate(ip=ip, port=port, tcp_open=False, error="timeout")
    except OSError as exc:
        return Candidate(ip=ip, port=port, tcp_open=False, error=str(exc))


def modbus_device_id(ip: str, port: int, timeout: float) -> tuple[bool, str | None, str | None]:
    # MBAP: transaction id, protocol id, length, unit id.
    # PDU: function 43/14, MEI type 14, read device id code 1, object id 0.
    request = struct.pack(">HHHBBB B B", 1, 0, 5, 1, 0x2B, 0x0E, 0x01, 0x00)
    try:
        with socket.create_connection((ip, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            sock.sendall(request)
            data = sock.recv(512)
    except OSError as exc:
        return False, None, str(exc)

    if len(data) < 9:
        return False, None, "short response"
    if data[7] & 0x80:
        return False, None, f"modbus exception {data[8] if len(data) > 8 else 'unknown'}"
    if data[7] != 0x2B or len(data) < 14:
        return False, None, "not a device-id response"

    try:
        objects = []
        count = data[13]
        offset = 14
        for _ in range(count):
            if offset + 2 > len(data):
                break
            object_id = data[offset]
            length = data[offset + 1]
            offset += 2
            value = data[offset:offset + length].decode("ascii", errors="replace")
            offset += length
            objects.append(f"{object_id}:{value}")
        label = "; ".join(objects) if objects else "device-id response without objects"
        return True, label, None
    except Exception as exc:  # noqa: BLE001 - parsing defensive diagnostics only
        return True, None, f"response parse warning: {exc}"


def main() -> int:
    args = parse_args()
    networks = validate_networks(args.cidr, args.port)
    hosts = iter_hosts(networks)

    print(
        f"Scanning {len(hosts)} local addresses on TCP/{args.port}. "
        "No registers will be read or written.",
        file=sys.stderr,
    )

    candidates: list[Candidate] = []
    workers = max(1, min(args.workers, 256))
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(check_tcp, ip, args.port, args.timeout) for ip in hosts]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result.tcp_open:
                candidates.append(result)

    candidates.sort(key=lambda item: ipaddress.ip_address(item.ip))

    if args.modbus_probe:
        for candidate in candidates:
            ok, label, error = modbus_device_id(candidate.ip, candidate.port, args.timeout)
            candidate.modbus_device_id_ok = ok
            candidate.device_id = label
            candidate.error = error

    data = [asdict(candidate) for candidate in candidates]
    if args.output:
        args.output.write_text(json.dumps(data, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(data, indent=2))
        return 0

    if not candidates:
        print("No open Modbus TCP candidates found.")
        return 0

    print("IP address       Port  TCP open  Modbus device-id  Device information")
    print("---------------  ----  --------  ----------------  ------------------")
    for item in candidates:
        probe = "not tested"
        if item.modbus_device_id_ok is True:
            probe = "yes"
        elif item.modbus_device_id_ok is False:
            probe = "no"
        print(
            f"{item.ip:<15}  {item.port:<4}  {'yes':<8}  {probe:<16}  "
            f"{item.device_id or item.error or ''}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
