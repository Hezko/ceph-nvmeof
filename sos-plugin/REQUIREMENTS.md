# Requirements and Installation Guide

## Overview

This document describes the requirements for using and testing the Ceph NVMe-oF SOS plugin.

## System Requirements

### For Using the Plugin (Production)

**Minimum Requirements:**
- Python 3.6 or later
- `sos` package (sosreport) version 4.0 or later
- Root/sudo access

**Optional Requirements (for full functionality):**
- `nvme-cli` - For NVMe command execution
- `multipath-tools` - For multipath information
- `podman` or `docker` - For container inspection (gateway nodes)
- `cephadm` - For Ceph container management (gateway nodes)

### For Testing the Plugin (Development)

**Required:**
- Python 3.6 or later
- `unittest` (built-in with Python 3.3+)
- `mock` (built-in with Python 3.3+ as `unittest.mock`)

**Optional:**
- `coverage` - For code coverage reports
- `pytest` - Alternative test runner

## Installation Instructions

### 1. Install System Requirements

#### On RHEL/CentOS/Fedora:

```bash
# Install SOS
sudo dnf install sos

# Install optional tools
sudo dnf install nvme-cli multipath-tools podman

# For Ceph deployments
sudo dnf install cephadm
```

#### On Ubuntu/Debian:

```bash
# Install SOS
sudo apt-get update
sudo apt-get install sosreport

# Install optional tools
sudo apt-get install nvme-cli multipath-tools podman

# For Ceph deployments
sudo apt-get install cephadm
```

### 2. Install the SOS Plugin

```bash
# Navigate to the plugin directory
cd /path/to/ceph-nvmeof/sos-plugin

# Find your Python site-packages directory
PLUGIN_DIR=$(python3 -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])")/sos/report/plugins

# Copy the plugin (requires sudo)
sudo cp ceph_nvmeof.py "$PLUGIN_DIR/"

# Verify installation
sosreport -l | grep ceph_nvmeof
```

**Expected output:**
```
ceph_nvmeof          Ceph NVMe over Fabrics (NVMe-oF)
```

### 3. Install Testing Requirements (Optional)

For running unit tests:

```bash
# Install coverage tool (optional but recommended)
pip3 install coverage

# Or using system package manager
sudo dnf install python3-coverage  # RHEL/Fedora
sudo apt-get install python3-coverage  # Ubuntu/Debian
```

## Verification

### Verify SOS Installation

```bash
# Check SOS version (should be 4.0+)
sosreport --version

# List available plugins
sosreport -l | head -20
```

### Verify Plugin Installation

```bash
# Check if plugin is recognized
sosreport -l | grep ceph_nvmeof

# Check plugin options
sosreport --list-plugins | grep -A 10 ceph_nvmeof
```

### Verify Optional Tools

```bash
# Check nvme-cli
nvme version

# Check multipath
multipath -v

# Check podman
podman --version

# Check cephadm
cephadm version
```

## Testing the Installation

### 1. Run Unit Tests

```bash
cd /path/to/ceph-nvmeof/sos-plugin

# Run all tests
python3 test_ceph_nvmeof.py

# Expected output: "Ran 28 tests ... OK"
```

### 2. Test Plugin Loading

```bash
# Dry run (doesn't actually collect data)
sudo sosreport -o ceph_nvmeof --dry-run

# This should show what would be collected without errors
```

### 3. Test Basic Collection

```bash
# Collect minimal data (fast test)
sudo sosreport -o ceph_nvmeof --batch \
  -k ceph_nvmeof.no-logs=on \
  -k ceph_nvmeof.no-performance=on

# Check the generated report
ls -lh /var/tmp/sosreport-*.tar.xz
```

## Troubleshooting

### Issue: "sosreport: command not found"

**Solution:**
```bash
# Install SOS package
sudo dnf install sos  # RHEL/Fedora
sudo apt-get install sosreport  # Ubuntu/Debian
```

### Issue: "Plugin not found"

**Solution:**
```bash
# Check if file was copied correctly
ls -l /usr/lib/python3.*/site-packages/sos/report/plugins/ceph_nvmeof.py

# Check file permissions
sudo chmod 644 /usr/lib/python3.*/site-packages/sos/report/plugins/ceph_nvmeof.py

# Check Python version matches
python3 --version
```

### Issue: "Import errors in tests"

**Solution:**
```bash
# The plugin imports SOS modules which may not be in your PYTHONPATH
# This is normal for development. Tests use mocks to work around this.

# To run tests without SOS installed:
cd /path/to/ceph-nvmeof/sos-plugin
python3 test_ceph_nvmeof.py

# The tests are designed to work without SOS installed
```

### Issue: "Permission denied"

**Solution:**
```bash
# SOS requires root privileges
sudo sosreport -o ceph_nvmeof
```

### Issue: "nvme: command not found"

**Solution:**
```bash
# Install nvme-cli
sudo dnf install nvme-cli  # RHEL/Fedora
sudo apt-get install nvme-cli  # Ubuntu/Debian

# The plugin will work without nvme-cli but won't collect NVMe-specific data
```

## Python Package Requirements

The plugin has **NO additional Python package requirements** beyond what's included with Python 3.6+ and the SOS package.

### Built-in Modules Used:
- `os` - File system operations
- `re` - Regular expressions
- `json` - JSON parsing (for cephadm output)

### SOS Framework Modules:
- `sos.report.plugins.Plugin` - Base plugin class
- `sos.report.plugins.RedHatPlugin` - RHEL-specific functionality
- `sos.report.plugins.DebianPlugin` - Debian-specific functionality
- `sos.report.plugins.UbuntuPlugin` - Ubuntu-specific functionality

### Testing Modules:
- `unittest` - Test framework (built-in)
- `unittest.mock` - Mocking framework (built-in with Python 3.3+)

## Quick Start Checklist

- [ ] Python 3.6+ installed
- [ ] SOS package installed (`sosreport --version`)
- [ ] Plugin copied to SOS plugins directory
- [ ] Plugin recognized (`sosreport -l | grep ceph_nvmeof`)
- [ ] Optional: nvme-cli installed (for NVMe commands)
- [ ] Optional: coverage installed (for test coverage)
- [ ] Tests pass (`python3 test_ceph_nvmeof.py`)
- [ ] Dry run works (`sudo sosreport -o ceph_nvmeof --dry-run`)

## Minimal Installation (Testing Only)

If you just want to test the plugin without installing SOS:

```bash
cd /path/to/ceph-nvmeof/sos-plugin

# Run unit tests (works without SOS installed)
python3 test_ceph_nvmeof.py

# The tests use mocks and don't require SOS to be installed
```

## Full Installation (Production Use)

For production use on systems with NVMe-oF:

```bash
# 1. Install all requirements
sudo dnf install sos nvme-cli multipath-tools podman cephadm

# 2. Install the plugin
cd /path/to/ceph-nvmeof/sos-plugin
PLUGIN_DIR=$(python3 -c "import sys; print([p for p in sys.path if 'site-packages' in p][0])")/sos/report/plugins
sudo cp ceph_nvmeof.py "$PLUGIN_DIR/"

# 3. Verify
sosreport -l | grep ceph_nvmeof

# 4. Test
sudo sosreport -o ceph_nvmeof --batch
```

## Summary

**For Development/Testing:**
- Only Python 3.6+ required
- No additional packages needed
- Tests work without SOS installed

**For Production Use:**
- Python 3.6+ and SOS 4.0+ required
- Optional tools enhance functionality but aren't required
- Plugin works with partial tool availability

The plugin is designed to gracefully handle missing tools and continue collecting what it can.