#!/usr/bin/env python3
# Copyright (C) 2024 Red Hat, Inc.
#
# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

"""
SOS Plugin for Ceph NVMe-oF (NVMe over Fabrics)

This plugin collects diagnostic information for Ceph NVMe-oF deployments,
primarily focusing on initiator-side diagnostics with optional gateway-side
collection when run on gateway nodes.

The plugin collects:
- NVMe device and subsystem information
- NVMe-oF connection status and discovery logs
- Performance metrics and I/O statistics
- Configuration files
- Kernel and system logs related to NVMe
- Gateway diagnostics (when applicable)
- Network connectivity information
"""

from sos.report.plugins import Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin
import os
import re


class CephNvmeof(Plugin, RedHatPlugin, DebianPlugin, UbuntuPlugin):
    """
    Ceph NVMe-oF (NVMe over Fabrics) diagnostic collection plugin.
    
    This plugin collects comprehensive diagnostic information for troubleshooting
    Ceph NVMe-oF deployments, including initiator and gateway diagnostics.
    """

    short_desc = 'Ceph NVMe over Fabrics (NVMe-oF)'
    plugin_name = 'ceph_nvmeof'
    profiles = ('storage', 'ceph', 'nvme')
    
    # Plugin options for selective collection
    option_list = [
        ('initiator-only', 'Only collect initiator-side diagnostics', 
         'fast', False),
        ('gateway-only', 'Only collect gateway-side diagnostics',
         'fast', False),
        ('no-performance', 'Skip performance metrics collection',
         'fast', False),
        ('no-logs', 'Skip log file collection',
         'fast', False),
        ('gateway-address', 'Gateway address for connectivity tests',
         'fast', ''),
    ]

    def setup(self):
        """
        Main collection method that orchestrates all diagnostic collection.
        """
        # Determine what to collect based on options
        collect_initiator = not self.get_option('gateway-only')
        collect_gateway = not self.get_option('initiator-only')
        collect_performance = not self.get_option('no-performance')
        collect_logs = not self.get_option('no-logs')

        if collect_initiator:
            self._collect_initiator_diagnostics(collect_performance, collect_logs)
        
        if collect_gateway:
            self._collect_gateway_diagnostics(collect_logs)
        
        # Always collect network diagnostics
        self._collect_network_diagnostics()

    def _collect_initiator_diagnostics(self, collect_performance=True, 
                                       collect_logs=True):
        """
        Collect initiator-side (client) NVMe-oF diagnostics.
        
        Args:
            collect_performance: Whether to collect performance metrics
            collect_logs: Whether to collect log files
        """
        # NVMe device and subsystem information
        self.add_cmd_output([
            "nvme list",
            "nvme list-subsys",
            "nvme list -v",
            "nvme list -o json",
            "nvme version",
        ], suggest_filename="nvme-devices")

        # NVMe-oF specific commands
        self.add_cmd_output([
            "nvme discover -t tcp -a 127.0.0.1 -s 8009",  # Local discovery
            "nvme show-regs /dev/nvme0",  # Show controller registers
        ], suggest_filename="nvme-fabrics")

        # Collect discovery information for each NVMe controller
        nvme_ctrls = self._get_nvme_controllers()
        for ctrl in nvme_ctrls:
            self.add_cmd_output([
                f"nvme id-ctrl {ctrl}",
                f"nvme id-ns {ctrl}",
                f"nvme list-ns {ctrl}",
                f"nvme get-feature {ctrl} -f 0x0c",  # Get number of queues
                f"nvme get-log {ctrl} -i 0x70 -l 4096",  # Discovery log
            ], suggest_filename=f"nvme-ctrl-{ctrl.replace('/', '-')}")

        # Performance and I/O statistics
        if collect_performance:
            for ctrl in nvme_ctrls:
                self.add_cmd_output([
                    f"nvme smart-log {ctrl}",
                    f"nvme error-log {ctrl}",
                    f"nvme fw-log {ctrl}",
                    f"nvme effects-log {ctrl}",
                ], suggest_filename=f"nvme-perf-{ctrl.replace('/', '-')}")

        # Configuration files
        self.add_copy_spec([
            "/etc/nvme/hostnqn",
            "/etc/nvme/hostid",
            "/etc/nvme/discovery.conf",
            "/etc/nvme/config.json",
            "/etc/multipath.conf",
            "/etc/multipath/conf.d/",
        ])

        # System information related to NVMe
        self.add_copy_spec([
            "/sys/class/nvme/",
            "/sys/class/nvme-fabrics/",
            "/sys/class/nvme-subsystem/",
            "/sys/module/nvme/",
            "/sys/module/nvme_core/",
            "/sys/module/nvme_fabrics/",
            "/sys/module/nvme_tcp/",
            "/sys/module/nvme_rdma/",
            "/sys/module/nvme_fc/",
        ], sizelimit=10)  # Limit to 10MB per file

        # Block device information
        self.add_cmd_output([
            "lsblk -a",
            "lsblk -f",
            "lsblk -t",
            "lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,UUID,MODEL,SERIAL",
        ], suggest_filename="block-devices")

        # Multipath information (if applicable)
        self.add_cmd_output([
            "multipath -ll",
            "multipath -v3 -ll",
            "multipathd show config",
            "multipathd show paths",
            "multipathd show maps",
        ], suggest_filename="multipath")

        # Kernel and system logs
        if collect_logs:
            self.add_cmd_output([
                "dmesg | grep -i nvme",
                "dmesg | grep -i 'nvme.*error'",
                "dmesg -T | grep -i nvme",
            ], suggest_filename="dmesg-nvme")

            self.add_journal(units=[
                "nvme-connect@*",
                "nvmefc-boot-connections",
                "nvmf-autoconnect",
            ])

            # Collect relevant log files
            self.add_copy_spec([
                "/var/log/messages",
                "/var/log/syslog",
            ], sizelimit=50)  # Limit to 50MB

        # I/O statistics
        if collect_performance:
            self.add_copy_spec([
                "/proc/diskstats",
                "/sys/block/nvme*/stat",
                "/sys/block/nvme*/queue/*",
            ])

            self.add_cmd_output([
                "iostat -x 1 5",
                "iostat -xm 1 5",
            ], suggest_filename="iostat")

    def _collect_gateway_diagnostics(self, collect_logs=True):
        """
        Collect gateway-side diagnostics when running on a gateway node.
        
        Args:
            collect_logs: Whether to collect log files
        """
        # Check if this is a gateway node
        if not self._is_gateway_node():
            return

        # Cephadm container information
        self.add_cmd_output([
            "cephadm ls",
            "cephadm ls --no-detail",
        ], suggest_filename="cephadm-containers")

        # Find NVMe-oF gateway containers
        gateway_containers = self._get_gateway_containers()
        
        for container in gateway_containers:
            # Container inspection
            self.add_cmd_output([
                f"podman inspect {container}",
                f"podman logs {container}",
                f"podman stats {container} --no-stream",
            ], suggest_filename=f"container-{container}")

            # Gateway configuration files from container
            self.add_cmd_output([
                f"podman exec {container} cat /etc/ceph/ceph-nvmeof.conf",
                f"podman exec {container} cat /etc/ceph/ceph.conf",
            ], suggest_filename=f"config-{container}")

            # Gateway CLI commands
            self.add_cmd_output([
                f"podman exec {container} python3 -m control.cli --format json gateway list",
                f"podman exec {container} python3 -m control.cli --format json subsystem list",
                f"podman exec {container} python3 -m control.cli --format json namespace list",
                f"podman exec {container} python3 -m control.cli --format json listener list",
                f"podman exec {container} python3 -m control.cli --format json host list",
                f"podman exec {container} python3 -m control.cli --format json connection list",
            ], suggest_filename=f"gateway-status-{container}")

            # SPDK information
            self.add_cmd_output([
                f"podman exec {container} python3 -m control.cli --format json spdk get_spdk_log_level",
            ], suggest_filename=f"spdk-status-{container}")

        # Gateway configuration files (if accessible)
        self.add_copy_spec([
            "/etc/ceph/ceph-nvmeof.conf",
            "/etc/ceph/ceph.conf",
            "/var/lib/ceph/*/nvmeof.*/ceph-nvmeof.conf",
        ])

        # Gateway logs
        if collect_logs:
            self.add_copy_spec([
                "/var/log/ceph/*nvmeof*",
                "/var/log/ceph/*/nvmeof.*/*.log",
            ], sizelimit=100)  # Limit to 100MB

            # Systemd journal for gateway services
            self.add_journal(units=[
                "ceph-*@nvmeof.*",
            ])

        # Prometheus metrics (if enabled)
        gateway_addr = self.get_option('gateway-address') or 'localhost'
        self.add_cmd_output([
            f"curl -s http://{gateway_addr}:10008/metrics",
        ], suggest_filename="prometheus-metrics")

    def _collect_network_diagnostics(self):
        """
        Collect network configuration and connectivity diagnostics.
        """
        # Network interface configuration
        self.add_cmd_output([
            "ip addr show",
            "ip link show",
            "ip route show",
            "ip -s link",
        ], suggest_filename="network-config")

        # Network statistics
        self.add_cmd_output([
            "netstat -s",
            "netstat -i",
            "ss -s",
            "ss -tan",
            "ss -tln",
        ], suggest_filename="network-stats")

        # Firewall rules
        self.add_cmd_output([
            "iptables -L -n -v",
            "iptables -t nat -L -n -v",
            "ip6tables -L -n -v",
            "nft list ruleset",
        ], suggest_filename="firewall")

        # Connectivity tests to gateway
        gateway_addr = self.get_option('gateway-address')
        if gateway_addr:
            # Test common NVMe-oF ports
            ports = [4420, 5500, 8009, 10008]
            for port in ports:
                self.add_cmd_output([
                    f"nc -zv -w 2 {gateway_addr} {port}",
                    f"timeout 2 bash -c 'cat < /dev/null > /dev/tcp/{gateway_addr}/{port}'",
                ], suggest_filename=f"connectivity-{gateway_addr}-{port}")

            # Ping test
            self.add_cmd_output([
                f"ping -c 5 {gateway_addr}",
                f"ping6 -c 5 {gateway_addr}",
            ], suggest_filename=f"ping-{gateway_addr}")

        # TCP connection states
        self.add_cmd_output([
            "ss -tan state established '( dport = :4420 or sport = :4420 )'",
            "ss -tan state established '( dport = :5500 or sport = :5500 )'",
        ], suggest_filename="tcp-connections")

    def _get_nvme_controllers(self):
        """
        Get list of NVMe controller devices.
        
        Returns:
            list: List of NVMe controller device paths (e.g., ['/dev/nvme0', '/dev/nvme1'])
        """
        controllers = []
        try:
            if os.path.exists('/dev'):
                for device in os.listdir('/dev'):
                    # Match nvme controllers (nvme0, nvme1, etc.) but not namespaces (nvme0n1)
                    if re.match(r'^nvme\d+$', device):
                        controllers.append(f'/dev/{device}')
        except Exception as e:
            self._log_error(f"Error getting NVMe controllers: {e}")
        
        return sorted(controllers)

    def _is_gateway_node(self):
        """
        Check if this system is a Ceph NVMe-oF gateway node.
        
        Returns:
            bool: True if this is a gateway node, False otherwise
        """
        # Check for cephadm
        if not self.is_installed('cephadm'):
            return False
        
        # Check for nvmeof containers
        gateway_containers = self._get_gateway_containers()
        return len(gateway_containers) > 0

    def _get_gateway_containers(self):
        """
        Get list of NVMe-oF gateway container names.
        
        Returns:
            list: List of container names
        """
        containers = []
        try:
            # Try to get container list from cephadm
            result = self.exec_cmd("cephadm ls --no-detail")
            if result['status'] == 0:
                import json
                cephadm_data = json.loads(result['output'])
                for container in cephadm_data:
                    if container.get('service_name', '').startswith('nvmeof'):
                        container_name = container.get('container_id') or container.get('container_name')
                        if container_name:
                            containers.append(container_name)
        except Exception as e:
            self._log_error(f"Error getting gateway containers: {e}")
        
        return containers

    def postproc(self):
        """
        Post-process collected data to sanitize sensitive information.
        """
        # Sanitize DHCHAP keys and passwords
        self.do_cmd_output_sub(
            "nvme",
            r"(dhchap[_-]?key|password|secret)[\s:=]+\S+",
            r"\1: ********"
        )

        # Sanitize TLS private keys
        self.do_file_sub(
            "/etc/ceph/ceph-nvmeof.conf",
            r"(.*key\s*=\s*).*",
            r"\1********"
        )

        # Sanitize authentication tokens
        self.do_cmd_output_sub(
            "gateway",
            r"(token|auth|key)[\s:=]+['\"]?[a-zA-Z0-9+/=]{20,}['\"]?",
            r"\1: ********"
        )

        # Sanitize KMIP credentials
        self.do_file_sub(
            "/etc/ceph/ceph-nvmeof.conf",
            r"(client_key|client_cert|ca_cert)\s*=\s*.*",
            r"\1 = ********"
        )

    def _log_error(self, message):
        """
        Log an error message.
        
        Args:
            message: Error message to log
        """
        self._log_warn(message)


# vim: set et ts=4 sw=4 :

# Made with Bob
