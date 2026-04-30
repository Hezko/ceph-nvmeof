# Installation and Testing Guide for Ceph NVMe-oF SOS Plugin

## Quick Start

### Installation

1. **Copy the plugin to the SOS plugins directory:**

   ```bash
   # For system-wide installation (requires root)
   sudo cp ceph_nvmeof.py /usr/lib/python3.*/site-packages/sos/report/plugins/
   
   # Or find the exact path
   PLUGIN_DIR=$(python3 -c "import sos.report.plugins; import os; print(os.path.dirname(sos.report.plugins.__file__))")
   sudo cp ceph_nvmeof.py "$PLUGIN_DIR/"
   ```

2. **Verify installation:**

   ```bash
   sosreport -l | grep ceph_nvmeof
   ```

   Expected output:
   ```
   ceph_nvmeof          Ceph NVMe over Fabrics (NVMe-oF)
   ```

### Basic Testing

#### Test 1: Verify Plugin Loads

```bash
sudo sosreport --list-plugins | grep -A 5 ceph_nvmeof
```

This should show the plugin with its description and options.

#### Test 2: Dry Run (List What Would Be Collected)

```bash
sudo sosreport -o ceph_nvmeof --dry-run
```

This shows what commands and files would be collected without actually running them.

#### Test 3: Collect Diagnostics

```bash
# Basic collection
sudo sosreport -o ceph_nvmeof --batch

# With specific options
sudo sosreport -o ceph_nvmeof --batch \
  -k ceph_nvmeof.gateway-address=192.168.1.100
```

The `--batch` flag skips interactive prompts.

## Testing Scenarios

### Scenario 1: Testing on an Initiator Node

**Prerequisites:**
- NVMe-oF initiator with active connections
- `nvme-cli` package installed

**Test Steps:**

1. Check current NVMe devices:
   ```bash
   nvme list
   ```

2. Run sosreport:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch \
     -k ceph_nvmeof.gateway-address=<your-gateway-ip>
   ```

3. Extract and verify the report:
   ```bash
   cd /var/tmp
   tar -xf sosreport-*.tar.xz
   cd sosreport-*/
   
   # Check collected data
   ls -la sos_commands/ceph_nvmeof/
   cat sos_commands/ceph_nvmeof/nvme-devices
   ```

**Expected Results:**
- NVMe device listings
- Connection information
- Discovery logs
- Network connectivity tests
- System logs with NVMe entries

### Scenario 2: Testing on a Gateway Node

**Prerequisites:**
- Ceph NVMe-oF gateway deployed via cephadm
- `cephadm` and `podman` installed

**Test Steps:**

1. Check gateway containers:
   ```bash
   cephadm ls | grep nvmeof
   ```

2. Run sosreport:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch
   ```

3. Verify gateway data collection:
   ```bash
   cd /var/tmp/sosreport-*/
   
   # Check container information
   ls -la sos_commands/ceph_nvmeof/cephadm-containers
   
   # Check gateway status
   ls -la sos_commands/ceph_nvmeof/gateway-status-*
   
   # Check configuration
   cat etc/ceph/ceph-nvmeof.conf
   ```

**Expected Results:**
- Container listings and logs
- Gateway configuration files
- Subsystem and namespace information
- Connection details
- SPDK status

### Scenario 3: Testing with Limited Permissions

**Test Steps:**

1. Try without sudo (should fail gracefully):
   ```bash
   sosreport -o ceph_nvmeof
   ```

2. Verify error message is clear and helpful.

### Scenario 4: Testing with Missing Dependencies

**Test Steps:**

1. Temporarily rename nvme-cli:
   ```bash
   sudo mv /usr/sbin/nvme /usr/sbin/nvme.bak
   ```

2. Run sosreport:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch
   ```

3. Verify plugin handles missing commands gracefully.

4. Restore nvme-cli:
   ```bash
   sudo mv /usr/sbin/nvme.bak /usr/sbin/nvme
   ```

**Expected Results:**
- Plugin should not crash
- Should collect what it can
- Should log warnings about missing commands

### Scenario 5: Testing Data Sanitization

**Test Steps:**

1. Create a test configuration with sensitive data:
   ```bash
   sudo mkdir -p /etc/ceph
   sudo cat > /tmp/test-nvmeof.conf << 'EOF'
   [gateway]
   encryption_key = /etc/ceph/secret.key
   
   [mtls]
   server_key = ./server.key
   client_key = ./client.key
   EOF
   ```

2. Run sosreport:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch
   ```

3. Verify sanitization:
   ```bash
   cd /var/tmp/sosreport-*/
   grep -r "secret.key" . || echo "PASS: Keys sanitized"
   grep -r "server.key" . || echo "PASS: Keys sanitized"
   ```

**Expected Results:**
- Sensitive key paths should be masked with `********`
- No actual key content should be present

## Validation Checklist

After running sosreport, verify the following:

### Initiator-Side Data

- [ ] `sos_commands/ceph_nvmeof/nvme-devices` exists and contains device list
- [ ] `sos_commands/ceph_nvmeof/nvme-fabrics` contains discovery information
- [ ] `sos_commands/ceph_nvmeof/nvme-ctrl-*` files exist for each controller
- [ ] `sos_commands/ceph_nvmeof/block-devices` contains lsblk output
- [ ] `sos_commands/ceph_nvmeof/dmesg-nvme` contains kernel messages
- [ ] `etc/nvme/hostnqn` exists (if configured)
- [ ] `sys/class/nvme/` directory structure is captured

### Gateway-Side Data (if applicable)

- [ ] `sos_commands/ceph_nvmeof/cephadm-containers` lists containers
- [ ] `sos_commands/ceph_nvmeof/container-*` files exist for each gateway
- [ ] `sos_commands/ceph_nvmeof/gateway-status-*` contains gateway information
- [ ] `etc/ceph/ceph-nvmeof.conf` exists
- [ ] Container logs are collected

### Network Data

- [ ] `sos_commands/ceph_nvmeof/network-config` contains interface info
- [ ] `sos_commands/ceph_nvmeof/network-stats` contains statistics
- [ ] `sos_commands/ceph_nvmeof/connectivity-*` files exist (if gateway address provided)
- [ ] `sos_commands/ceph_nvmeof/tcp-connections` shows NVMe-oF connections

### Data Sanitization

- [ ] No plaintext passwords or keys in collected data
- [ ] DHCHAP keys are masked
- [ ] TLS private keys are redacted
- [ ] Authentication tokens are sanitized

## Troubleshooting

### Plugin Not Loading

**Problem:** Plugin doesn't appear in `sosreport -l`

**Solutions:**
1. Check file permissions:
   ```bash
   ls -l /usr/lib/python3.*/site-packages/sos/report/plugins/ceph_nvmeof.py
   sudo chmod 644 /usr/lib/python3.*/site-packages/sos/report/plugins/ceph_nvmeof.py
   ```

2. Check for syntax errors:
   ```bash
   python3 -m py_compile ceph_nvmeof.py
   ```

3. Check SOS version:
   ```bash
   sosreport --version  # Should be 4.0 or later
   ```

### Collection Failures

**Problem:** Some commands fail during collection

**Solutions:**
1. Check command availability:
   ```bash
   which nvme
   which cephadm
   which podman
   ```

2. Install missing packages:
   ```bash
   # RHEL/CentOS/Fedora
   sudo dnf install nvme-cli cephadm podman
   
   # Ubuntu/Debian
   sudo apt install nvme-cli cephadm podman
   ```

3. Check permissions:
   ```bash
   # Ensure running with sudo
   sudo sosreport -o ceph_nvmeof
   ```

### Large Report Size

**Problem:** Report is too large

**Solutions:**
1. Use selective collection:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch \
     -k ceph_nvmeof.no-logs=on \
     -k ceph_nvmeof.no-performance=on
   ```

2. Collect only initiator data:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch \
     -k ceph_nvmeof.initiator-only=on
   ```

### Timeout Issues

**Problem:** Collection takes too long

**Solutions:**
1. Skip performance metrics:
   ```bash
   sudo sosreport -o ceph_nvmeof --batch \
     -k ceph_nvmeof.no-performance=on
   ```

2. Increase timeout (if needed):
   ```bash
   sudo sosreport -o ceph_nvmeof --batch --plugin-timeout=600
   ```

## Performance Benchmarks

Typical collection times (approximate):

| Scenario | Time | Report Size |
|----------|------|-------------|
| Initiator only (no logs) | 10-30s | 1-5 MB |
| Initiator with logs | 30-60s | 10-50 MB |
| Gateway only | 20-40s | 5-20 MB |
| Full collection | 60-120s | 20-100 MB |

## Integration Testing

### With CI/CD

Example GitHub Actions workflow:

```yaml
name: Test SOS Plugin

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y sos nvme-cli
      
      - name: Install plugin
        run: |
          PLUGIN_DIR=$(python3 -c "import sos.report.plugins; import os; print(os.path.dirname(sos.report.plugins.__file__))")
          sudo cp ceph_nvmeof.py "$PLUGIN_DIR/"
      
      - name: Verify plugin loads
        run: |
          sosreport -l | grep ceph_nvmeof
      
      - name: Test dry run
        run: |
          sudo sosreport -o ceph_nvmeof --dry-run
```

## Next Steps

After successful testing:

1. **Submit to upstream SOS project:**
   - Fork https://github.com/sosreport/sos
   - Add plugin to `sos/report/plugins/`
   - Submit pull request

2. **Package for distribution:**
   - Include in Ceph packages
   - Add to system package repositories

3. **Documentation:**
   - Add to Ceph documentation
   - Create knowledge base articles
   - Update troubleshooting guides

## Support

For issues or questions:
- File issues at: https://github.com/sosreport/sos/issues
- Ceph community: https://ceph.io/community/
- Mailing list: ceph-users@ceph.io