# Ceph NVMe-oF SOS Report Plugin

## Overview

The `ceph_nvmeof` plugin is a comprehensive diagnostic collection tool for Ceph NVMe over Fabrics (NVMe-oF) deployments. It is designed to be used with the `sosreport` utility to collect system information for troubleshooting purposes.

## Features

### Primary Focus: Initiator-Side Diagnostics

The plugin primarily collects diagnostic information from NVMe-oF initiators (clients) connecting to Ceph NVMe-oF gateways:

- **NVMe Device Information**
  - List of all NVMe devices and subsystems
  - Controller and namespace details
  - Device topology and relationships

- **Connection Status**
  - Active NVMe-oF connections
  - Discovery log pages
  - Connection parameters and QoS settings

- **Performance Metrics**
  - SMART data and health information
  - I/O statistics and throughput
  - Error logs and firmware logs
  - Block device queue information

- **Configuration Files**
  - Host NQN and Host ID
  - Discovery configuration
  - Multipath configuration (if applicable)

- **System Logs**
  - Kernel messages related to NVMe
  - Systemd journal entries
  - System log files

### Optional: Gateway-Side Diagnostics

When run on a Ceph NVMe-oF gateway node, the plugin can also collect:

- **Container Information**
  - Cephadm container listings
  - Container logs and inspection data
  - Container resource usage

- **Gateway Configuration**
  - Gateway configuration files
  - Ceph configuration
  - SPDK configuration

- **Gateway Status**
  - Subsystem, namespace, and listener information
  - Host and connection details
  - SPDK log levels and status
  - Prometheus metrics (if enabled)

### Network Diagnostics

The plugin always collects network-related information:

- Network interface configuration
- Routing tables and firewall rules
- Network statistics
- Connectivity tests to gateways (when address provided)
- TCP connection states for NVMe-oF ports

## Installation

### For Upstream SOS Project

1. Copy the plugin file to the SOS plugins directory:
   ```bash
   sudo cp ceph_nvmeof.py /usr/lib/python3.*/site-packages/sos/report/plugins/
   ```

2. Verify the plugin is recognized:
   ```bash
   sosreport -l | grep ceph_nvmeof
   ```

### For Development/Testing

1. Place the plugin in your local SOS development environment:
   ```bash
   cp ceph_nvmeof.py /path/to/sos/sos/report/plugins/
   ```

2. Run SOS from the development directory:
   ```bash
   cd /path/to/sos
   sudo ./bin/sosreport -o ceph_nvmeof
   ```

## Usage

### Basic Usage

Collect all available diagnostics (default behavior):
```bash
sudo sosreport -o ceph_nvmeof
```

### Selective Collection Options

#### Initiator-Only Mode
Collect only initiator-side diagnostics (skip gateway checks):
```bash
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.initiator-only=on
```

#### Gateway-Only Mode
Collect only gateway-side diagnostics (skip initiator checks):
```bash
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.gateway-only=on
```

#### Skip Performance Metrics
Skip performance-intensive collection (faster execution):
```bash
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.no-performance=on
```

#### Skip Log Files
Skip log file collection (reduce report size):
```bash
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.no-logs=on
```

#### Specify Gateway Address
Provide gateway address for connectivity tests:
```bash
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.gateway-address=192.168.1.100
```

### Combined Options

You can combine multiple options:
```bash
sudo sosreport -o ceph_nvmeof \
  -k ceph_nvmeof.no-performance=on \
  -k ceph_nvmeof.gateway-address=10.0.0.50
```

### Using with Other Plugins

Collect Ceph NVMe-oF diagnostics along with other storage plugins:
```bash
sudo sosreport -o ceph_nvmeof,ceph,block,storage
```

## What Gets Collected

### Initiator-Side Collection

#### Commands Executed
- `nvme list` - List all NVMe devices
- `nvme list-subsys` - Show subsystem topology
- `nvme discover` - Discovery log pages
- `nvme id-ctrl` - Controller identification
- `nvme id-ns` - Namespace identification
- `nvme smart-log` - SMART/health information
- `nvme error-log` - Error log pages
- `nvme fw-log` - Firmware log pages
- `lsblk` - Block device information
- `multipath -ll` - Multipath topology
- `iostat` - I/O statistics
- `dmesg | grep nvme` - Kernel messages

#### Files Collected
- `/etc/nvme/hostnqn` - Host NQN
- `/etc/nvme/hostid` - Host ID
- `/etc/nvme/discovery.conf` - Discovery configuration
- `/etc/multipath.conf` - Multipath configuration
- `/sys/class/nvme/` - NVMe sysfs information
- `/sys/class/nvme-fabrics/` - Fabrics-specific sysfs
- `/proc/diskstats` - Disk statistics
- `/var/log/messages` - System logs (limited)

#### Journal Units
- `nvme-connect@*` - NVMe connection services
- `nvmefc-boot-connections` - FC boot connections
- `nvmf-autoconnect` - Auto-connect service

### Gateway-Side Collection

#### Commands Executed
- `cephadm ls` - List Ceph containers
- `podman inspect` - Container details
- `podman logs` - Container logs
- `podman stats` - Container resource usage
- Gateway CLI commands (via container exec):
  - `gateway list` - Gateway information
  - `subsystem list` - Subsystem configuration
  - `namespace list` - Namespace details
  - `listener list` - Listener configuration
  - `host list` - Host access control
  - `connection list` - Active connections
  - `spdk get_spdk_log_level` - SPDK status

#### Files Collected
- `/etc/ceph/ceph-nvmeof.conf` - Gateway configuration
- `/etc/ceph/ceph.conf` - Ceph configuration
- `/var/log/ceph/*nvmeof*` - Gateway logs (limited to 100MB)

#### Prometheus Metrics
- HTTP request to gateway metrics endpoint (if accessible)

### Network Collection

#### Commands Executed
- `ip addr show` - Interface addresses
- `ip route show` - Routing table
- `netstat -s` - Network statistics
- `ss -tan` - TCP connections
- `iptables -L` - Firewall rules
- `ping` - Connectivity tests (if gateway address provided)
- `nc -zv` - Port connectivity tests

## Data Sanitization

The plugin automatically sanitizes sensitive information in the collected data:

- **DHCHAP Keys**: Authentication keys are replaced with `********`
- **Passwords**: All password fields are masked
- **TLS Private Keys**: Private key content is redacted
- **Authentication Tokens**: API tokens and auth strings are masked
- **KMIP Credentials**: Client keys and certificates are sanitized

## Troubleshooting

### Plugin Not Found

If the plugin is not recognized:
```bash
# Check if the file is in the correct location
ls -l /usr/lib/python3.*/site-packages/sos/report/plugins/ceph_nvmeof.py

# Verify Python version matches
python3 --version

# Check SOS version
sosreport --version
```

### Permission Errors

The plugin requires root privileges to access system information:
```bash
sudo sosreport -o ceph_nvmeof
```

### Missing Commands

If certain commands are not available:
- Install `nvme-cli` package for NVMe commands
- Install `multipath-tools` for multipath commands
- Install `podman` or `docker` for container inspection

### Large Report Size

To reduce report size:
```bash
# Skip logs
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.no-logs=on

# Skip performance metrics
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.no-performance=on

# Collect only initiator data
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.initiator-only=on
```

## Use Cases

### Scenario 1: Initiator Connection Issues

When an initiator cannot connect to the gateway:
```bash
sudo sosreport -o ceph_nvmeof \
  -k ceph_nvmeof.gateway-address=<gateway-ip>
```

This collects:
- NVMe device status
- Discovery logs
- Network connectivity to gateway
- Kernel messages about connection attempts

### Scenario 2: Performance Problems

When experiencing slow I/O or high latency:
```bash
sudo sosreport -o ceph_nvmeof
```

This collects:
- SMART data and health information
- I/O statistics
- Queue depths and settings
- Error logs

### Scenario 3: Gateway Diagnostics

When troubleshooting gateway issues:
```bash
# Run on the gateway node
sudo sosreport -o ceph_nvmeof
```

This collects:
- Gateway configuration
- Container logs
- Subsystem and namespace configuration
- Active connections
- SPDK status

### Scenario 4: Quick Diagnostic

For a quick diagnostic without logs:
```bash
sudo sosreport -o ceph_nvmeof \
  -k ceph_nvmeof.no-logs=on \
  -k ceph_nvmeof.no-performance=on
```

## Integration with Ceph Support

When opening a support case with Red Hat or the Ceph community:

1. Collect the sosreport:
   ```bash
   sudo sosreport -o ceph_nvmeof,ceph,storage
   ```

2. The report will be saved as a compressed tarball:
   ```
   /var/tmp/sosreport-hostname-YYYYMMDDHHMMSS.tar.xz
   ```

3. Upload the tarball to the support case or share it with the community.

## Contributing

To contribute improvements to this plugin:

1. Fork the SOS project: https://github.com/sosreport/sos
2. Make your changes to `sos/report/plugins/ceph_nvmeof.py`
3. Test thoroughly with various deployment scenarios
4. Submit a pull request with a clear description of changes

## Requirements

### Minimum Requirements
- Python 3.6 or later
- SOS 4.0 or later
- Root/sudo access

### Optional Requirements
- `nvme-cli` - For NVMe command execution
- `multipath-tools` - For multipath information
- `podman` or `docker` - For container inspection
- `cephadm` - For Ceph container management

## Version History

### Version 1.0 (Initial Release)
- Comprehensive initiator-side diagnostics
- Optional gateway-side diagnostics
- Network connectivity tests
- Data sanitization for sensitive information
- Configurable collection options

## License

This plugin is part of the SOS project and is licensed under the GNU General Public License v2.

## Support

For issues or questions:
- SOS Project: https://github.com/sosreport/sos
- Ceph Project: https://github.com/ceph/ceph
- Ceph NVMe-oF Gateway: https://github.com/ceph/ceph-nvmeof

## See Also

- `sosreport(1)` - Main sosreport documentation
- `nvme(1)` - NVMe command line interface
- Ceph NVMe-oF Gateway Documentation: https://docs.ceph.com/