"""Network Hardware Monitor Module.

Collects network interface IO bytes sent/received, IP addresses, active connections,
and hostname telemetry using psutil and socket.
"""

import socket
from typing import Any, Dict, List
import psutil
import structlog

logger = structlog.get_logger(__name__)


def get_hostname() -> str:
    """Returns local host machine fully qualified domain hostname."""
    try:
        return socket.gethostname()
    except Exception as exc:
        logger.warning("failed_to_get_hostname", error=str(exc))
        return "localhost"


def get_ip_addresses() -> Dict[str, str]:
    """Returns IPv4 and IPv6 primary host address mappings."""
    addresses = {"ipv4": "127.0.0.1", "ipv6": "::1"}
    try:
        hostname = socket.gethostname()
        addresses["ipv4"] = socket.gethostbyname(hostname)
    except Exception as exc:
        logger.debug("failed_to_resolve_host_ip", error=str(exc))
    return addresses


def get_network_io() -> Dict[str, Any]:
    """Returns total network bytes sent, bytes received, packets, and error counters."""
    try:
        net_io = psutil.net_io_counters()
        if net_io:
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
            }
    except Exception as exc:
        logger.warning("failed_to_get_network_io", error=str(exc))
    return {
        "bytes_sent": 0,
        "bytes_recv": 0,
        "packets_sent": 0,
        "packets_recv": 0,
        "errin": 0,
        "errout": 0,
        "dropin": 0,
        "dropout": 0,
    }


def get_network_interfaces() -> List[Dict[str, Any]]:
    """Returns list of network interface addresses and stats."""
    interfaces = []
    try:
        if_addrs = psutil.net_if_addrs()
        if_stats = psutil.net_if_stats()
        for name, addrs in if_addrs.items():
            stat = if_stats.get(name)
            addr_list = []
            for addr in addrs:
                addr_list.append(
                    {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    }
                )
            interfaces.append(
                {
                    "interface": name,
                    "is_up": stat.isup if stat else True,
                    "speed_mbps": stat.speed if stat else 0,
                    "mtu": stat.mtu if stat else 0,
                    "addresses": addr_list,
                }
            )
    except Exception as exc:
        logger.warning("failed_to_get_network_interfaces", error=str(exc))
    return interfaces


def get_active_connections() -> List[Dict[str, Any]]:
    """Returns list of open network socket connections (with permission fallback)."""
    connections = []
    try:
        for conn in psutil.net_connections(kind="inet"):
            laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
            connections.append(
                {
                    "fd": conn.fd,
                    "family": str(conn.family),
                    "type": str(conn.type),
                    "local_address": laddr,
                    "remote_address": raddr,
                    "status": conn.status,
                    "pid": conn.pid,
                }
            )
    except Exception as exc:
        logger.debug("net_connections_permission_denied_or_unsupported", error=str(exc))
    return connections


class NetworkMonitor:
    """Class wrapper for Network telemetry hardware metrics."""

    def __init__(self) -> None:
        logger.info("network_monitor_initialized")

    def get_hostname(self) -> str:
        return get_hostname()

    def get_ip_addresses(self) -> Dict[str, str]:
        return get_ip_addresses()

    def get_network_io(self) -> Dict[str, Any]:
        return get_network_io()

    def get_network_interfaces(self) -> List[Dict[str, Any]]:
        return get_network_interfaces()

    def get_active_connections(self) -> List[Dict[str, Any]]:
        return get_active_connections()

    def get_metrics(self) -> Dict[str, Any]:
        """Collects complete network metrics dictionary."""
        io = get_network_io()
        return {
            "hostname": get_hostname(),
            "ip_addresses": get_ip_addresses(),
            "bytes_sent": io["bytes_sent"],
            "bytes_recv": io["bytes_recv"],
            "packets_sent": io["packets_sent"],
            "packets_recv": io["packets_recv"],
            "interfaces": get_network_interfaces(),
        }
