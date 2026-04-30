# SOS Report Plugin for Ceph NVMe-oF

This directory contains the SOS (sosreport) plugin for collecting diagnostic information from Ceph NVMe over Fabrics (NVMe-oF) deployments.

## Contents

- **`ceph_nvmeof.py`** - Main SOS plugin implementation
- **`test_ceph_nvmeof.py`** - Comprehensive unit test suite
- **`README_ceph_nvmeof_plugin.md`** - User documentation
- **`INSTALL_AND_TEST.md`** - Installation and testing guide
- **`TEST_README.md`** - Unit test documentation
- **`EXAMPLE_OUTPUT.md`** - Example output documentation

## Quick Start

### Installation

```bash
# Copy plugin to SOS plugins directory
sudo cp ceph_nvmeof.py /usr/lib/python3.*/site-packages/sos/report/plugins/

# Verify installation
sosreport -l | grep ceph_nvmeof
```

### Usage

```bash
# Basic collection
sudo sosreport -o ceph_nvmeof

# Initiator-only mode
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.initiator-only=on

# With gateway connectivity tests
sudo sosreport -o ceph_nvmeof -k ceph_nvmeof.gateway-address=192.168.1.100
```

### Running Tests

```bash
# Run unit tests
python3 test_ceph_nvmeof.py

# Run with coverage
coverage run test_ceph_nvmeof.py
coverage report
```

## Documentation

For detailed information, see:

- **[User Documentation](README_ceph_nvmeof_plugin.md)** - Complete usage guide
- **[Installation Guide](INSTALL_AND_TEST.md)** - Installation and testing procedures
- **[Test Documentation](TEST_README.md)** - Unit test details
- **[Example Output](EXAMPLE_OUTPUT.md)** - Sample sosreport output

## Features

### Data Collection

- **Initiator-Side (Primary)**
  - NVMe device and subsystem information
  - Connection status and discovery logs
  - Performance metrics (SMART, I/O stats)
  - Configuration files
  - Kernel and system logs

- **Gateway-Side (Optional)**
  - Cephadm container information
  - Gateway configuration and logs
  - Subsystem and namespace details
  - Active connections
  - SPDK status

- **Network Diagnostics**
  - Interface configuration
  - Connectivity tests
  - Firewall rules
  - TCP connection states

### Security

- GPL v2 licensed (compatible with SOS project)
- Automatic sanitization of sensitive data:
  - DHCHAP keys and passwords
  - TLS private keys
  - Authentication tokens
  - KMIP credentials

### Data Protection

- File size limits (10MB, 50MB, 100MB)
- Configurable collection options
- Graceful error handling
- Selective data collection

## Plugin Options

- `--initiator-only` - Collect only initiator diagnostics
- `--gateway-only` - Collect only gateway diagnostics
- `--no-performance` - Skip performance metrics
- `--no-logs` - Skip log file collection
- `--gateway-address=<addr>` - Specify gateway for connectivity tests

## Requirements

### Minimum
- Python 3.6+
- SOS 4.0+
- Root/sudo access

### Optional
- nvme-cli (for NVMe commands)
- multipath-tools (for multipath info)
- podman/docker (for container inspection)
- cephadm (for Ceph container management)

## Compatibility

- Red Hat Enterprise Linux 8+
- CentOS Stream 8+
- Fedora 37+
- Ubuntu 20.04+
- Debian 11+

## Contributing

### To Upstream SOS Project

1. Fork https://github.com/sosreport/sos
2. Add `ceph_nvmeof.py` to `sos/report/plugins/`
3. Add tests to `tests/report_tests/plugin_tests/`
4. Submit pull request

### To Ceph NVMe-oF Project

1. Fork https://github.com/ceph/ceph-nvmeof
2. Make changes in `sos-plugin/` directory
3. Run tests: `python3 test_ceph_nvmeof.py`
4. Submit pull request

## Testing

The plugin includes comprehensive unit tests:

```bash
# Run all tests
python3 test_ceph_nvmeof.py

# Run specific test class
python3 -m unittest test_ceph_nvmeof.TestCephNvmeofPlugin

# Run with verbose output
python3 test_ceph_nvmeof.py -v

# Generate coverage report
coverage run test_ceph_nvmeof.py
coverage report -m
coverage html
```

Expected test coverage: >85%

## Support

### Documentation
- SOS Project: https://github.com/sosreport/sos
- Ceph Documentation: https://docs.ceph.com/
- NVMe-oF Gateway: https://github.com/ceph/ceph-nvmeof

### Community
- Ceph Users: ceph-users@ceph.io
- Ceph Dev: dev@ceph.io
- Ceph Slack: https://ceph.io/slack

### Issues
- SOS Plugin Issues: https://github.com/sosreport/sos/issues
- Ceph NVMe-oF Issues: https://github.com/ceph/ceph-nvmeof/issues

## License

GNU General Public License v2

See the LICENSE file in the source distribution for further information.

## Version History

### Version 1.0 (Initial Release)
- Complete initiator-side diagnostics
- Optional gateway-side diagnostics
- Network connectivity tests
- Data sanitization
- Configurable collection options
- Comprehensive unit tests
- Full documentation

## Authors

Created for the Ceph NVMe-oF project to assist with troubleshooting and support.

## See Also

- `sosreport(1)` - Main sosreport documentation
- `nvme(1)` - NVMe command line interface
- Ceph NVMe-oF Gateway Documentation