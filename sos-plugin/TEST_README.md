# Unit Tests for Ceph NVMe-oF SOS Plugin

## Overview

This document describes the unit tests for the `ceph_nvmeof` SOS plugin. The test suite provides comprehensive coverage of the plugin's functionality.

## Test Files

- **`test_ceph_nvmeof.py`** - Main test suite (567 lines)

## Test Coverage

### Test Classes

#### 1. `TestCephNvmeofPlugin`
Unit tests for individual plugin methods and functionality.

**Test Cases:**

1. **Plugin Initialization**
   - `test_plugin_initialization()` - Verifies plugin attributes
   - `test_plugin_options()` - Checks all plugin options exist

2. **NVMe Controller Detection**
   - `test_get_nvme_controllers_empty()` - No devices present
   - `test_get_nvme_controllers_with_devices()` - Multiple devices
   - `test_get_nvme_controllers_sorted()` - Proper sorting
   - `test_get_nvme_controllers_exception_handling()` - Error handling

3. **Gateway Node Detection**
   - `test_is_gateway_node_no_cephadm()` - No cephadm installed
   - `test_is_gateway_node_no_containers()` - No gateway containers
   - `test_is_gateway_node_with_containers()` - Gateway containers present

4. **Gateway Container Discovery**
   - `test_get_gateway_containers_empty()` - No containers
   - `test_get_gateway_containers_with_nvmeof()` - NVMe-oF containers found
   - `test_get_gateway_containers_exception_handling()` - Error handling

5. **Initiator Diagnostics Collection**
   - `test_collect_initiator_diagnostics_basic()` - Basic collection
   - `test_collect_initiator_diagnostics_with_controllers()` - With devices
   - `test_collect_initiator_diagnostics_skip_performance()` - Skip performance
   - `test_collect_initiator_diagnostics_with_logs()` - Log collection

6. **Gateway Diagnostics Collection**
   - `test_collect_gateway_diagnostics_not_gateway()` - Not a gateway node
   - `test_collect_gateway_diagnostics_with_containers()` - Container collection

7. **Network Diagnostics Collection**
   - `test_collect_network_diagnostics()` - Basic network info
   - `test_collect_network_diagnostics_with_gateway_address()` - Connectivity tests

8. **Setup Method**
   - `test_setup_default_options()` - Default behavior
   - `test_setup_initiator_only()` - Initiator-only mode
   - `test_setup_gateway_only()` - Gateway-only mode

9. **Data Sanitization**
   - `test_postproc_sanitizes_dhchap_keys()` - DHCHAP key sanitization
   - `test_postproc_sanitizes_config_keys()` - Config key sanitization
   - `test_postproc_sanitizes_tokens()` - Token sanitization

#### 2. `TestCephNvmeofPluginIntegration`
Integration tests for complete workflows.

**Test Cases:**

1. **Full Collection Workflows**
   - `test_full_initiator_collection()` - Complete initiator collection
   - `test_full_gateway_collection()` - Complete gateway collection

## Running the Tests

### Prerequisites

```bash
# Install required packages
pip install unittest mock

# For full SOS integration testing
pip install sos
```

### Run All Tests

```bash
# Run with Python unittest
python3 test_ceph_nvmeof.py

# Run with verbose output
python3 test_ceph_nvmeof.py -v

# Run with pytest (if installed)
pytest test_ceph_nvmeof.py -v

# Run with coverage (if installed)
coverage run test_ceph_nvmeof.py
coverage report
coverage html
```

### Run Specific Test Classes

```bash
# Run only unit tests
python3 -m unittest test_ceph_nvmeof.TestCephNvmeofPlugin

# Run only integration tests
python3 -m unittest test_ceph_nvmeof.TestCephNvmeofPluginIntegration
```

### Run Specific Test Methods

```bash
# Run a single test
python3 -m unittest test_ceph_nvmeof.TestCephNvmeofPlugin.test_plugin_initialization

# Run tests matching a pattern
python3 -m unittest test_ceph_nvmeof.TestCephNvmeofPlugin.test_get_nvme_*
```

## Test Output

### Successful Run

```
test_collect_gateway_diagnostics_not_gateway (__main__.TestCephNvmeofPlugin) ... ok
test_collect_gateway_diagnostics_with_containers (__main__.TestCephNvmeofPlugin) ... ok
test_collect_initiator_diagnostics_basic (__main__.TestCephNvmeofPlugin) ... ok
test_collect_initiator_diagnostics_skip_performance (__main__.TestCephNvmeofPlugin) ... ok
test_collect_initiator_diagnostics_with_controllers (__main__.TestCephNvmeofPlugin) ... ok
test_collect_initiator_diagnostics_with_logs (__main__.TestCephNvmeofPlugin) ... ok
test_collect_network_diagnostics (__main__.TestCephNvmeofPlugin) ... ok
test_collect_network_diagnostics_with_gateway_address (__main__.TestCephNvmeofPlugin) ... ok
test_full_gateway_collection (__main__.TestCephNvmeofPluginIntegration) ... ok
test_full_initiator_collection (__main__.TestCephNvmeofPluginIntegration) ... ok
test_get_gateway_containers_empty (__main__.TestCephNvmeofPlugin) ... ok
test_get_gateway_containers_exception_handling (__main__.TestCephNvmeofPlugin) ... ok
test_get_gateway_containers_with_nvmeof (__main__.TestCephNvmeofPlugin) ... ok
test_get_nvme_controllers_empty (__main__.TestCephNvmeofPlugin) ... ok
test_get_nvme_controllers_exception_handling (__main__.TestCephNvmeofPlugin) ... ok
test_get_nvme_controllers_sorted (__main__.TestCephNvmeofPlugin) ... ok
test_get_nvme_controllers_with_devices (__main__.TestCephNvmeofPlugin) ... ok
test_is_gateway_node_no_cephadm (__main__.TestCephNvmeofPlugin) ... ok
test_is_gateway_node_no_containers (__main__.TestCephNvmeofPlugin) ... ok
test_is_gateway_node_with_containers (__main__.TestCephNvmeofPlugin) ... ok
test_plugin_initialization (__main__.TestCephNvmeofPlugin) ... ok
test_plugin_options (__main__.TestCephNvmeofPlugin) ... ok
test_postproc_sanitizes_config_keys (__main__.TestCephNvmeofPlugin) ... ok
test_postproc_sanitizes_dhchap_keys (__main__.TestCephNvmeofPlugin) ... ok
test_postproc_sanitizes_tokens (__main__.TestCephNvmeofPlugin) ... ok
test_setup_default_options (__main__.TestCephNvmeofPlugin) ... ok
test_setup_gateway_only (__main__.TestCephNvmeofPlugin) ... ok
test_setup_initiator_only (__main__.TestCephNvmeofPlugin) ... ok

----------------------------------------------------------------------
Ran 28 tests in 0.123s

OK
```

## Test Coverage

The test suite provides coverage for:

- ✅ Plugin initialization and configuration
- ✅ Option handling
- ✅ NVMe device detection and enumeration
- ✅ Gateway node detection
- ✅ Container discovery
- ✅ Initiator diagnostics collection
- ✅ Gateway diagnostics collection
- ✅ Network diagnostics collection
- ✅ Data sanitization
- ✅ Error handling
- ✅ Edge cases (no devices, no containers, etc.)

### Coverage Report

To generate a coverage report:

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run --source=. test_ceph_nvmeof.py

# Generate report
coverage report -m

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

Expected coverage: **>85%** of plugin code

## Continuous Integration

### GitHub Actions Example

```yaml
name: Test Ceph NVMe-oF Plugin

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.6', '3.8', '3.10', '3.11']
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install unittest-xml-reporting coverage
      
      - name: Run tests
        run: |
          python test_ceph_nvmeof.py
      
      - name: Generate coverage report
        run: |
          coverage run test_ceph_nvmeof.py
          coverage xml
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Test') {
            steps {
                sh 'python3 test_ceph_nvmeof.py'
            }
        }
        
        stage('Coverage') {
            steps {
                sh 'coverage run test_ceph_nvmeof.py'
                sh 'coverage report'
                sh 'coverage html'
            }
        }
    }
    
    post {
        always {
            publishHTML([
                reportDir: 'htmlcov',
                reportFiles: 'index.html',
                reportName: 'Coverage Report'
            ])
        }
    }
}
```

## Troubleshooting

### Import Errors

If you get import errors when running tests:

```bash
# Option 1: Install SOS package
pip install sos

# Option 2: Add current directory to PYTHONPATH
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 test_ceph_nvmeof.py

# Option 3: Run from the same directory
cd /path/to/plugin
python3 test_ceph_nvmeof.py
```

### Mock Errors

If you get errors about Mock objects:

```bash
# Install mock for Python < 3.3
pip install mock

# For Python >= 3.3, mock is built-in
python3 -c "from unittest.mock import Mock"
```

### Test Failures

If tests fail:

1. **Check Python version**: Tests require Python 3.6+
2. **Check dependencies**: Ensure unittest and mock are available
3. **Check file paths**: Ensure plugin file is in the correct location
4. **Run with verbose output**: `python3 test_ceph_nvmeof.py -v`
5. **Check individual tests**: Run failing tests individually

## Adding New Tests

### Test Template

```python
def test_new_feature(self):
    """Test description."""
    # Setup
    self.plugin.some_method = Mock(return_value='expected')
    
    # Execute
    result = self.plugin.method_under_test()
    
    # Verify
    self.assertEqual(result, 'expected')
    self.plugin.some_method.assert_called_once()
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Clear test names** describing what is tested
3. **Use mocks** to isolate functionality
4. **Test edge cases** (empty, None, errors)
5. **Test error handling** explicitly
6. **Keep tests independent** (no shared state)
7. **Use setUp/tearDown** for common initialization

## Integration with SOS Test Suite

To integrate with the upstream SOS test suite:

1. Place `test_ceph_nvmeof.py` in `tests/report_tests/plugin_tests/`
2. Follow SOS naming conventions
3. Inherit from SOS test base classes if available
4. Run with SOS test runner: `./tests/simple.sh`

## Maintenance

### When to Update Tests

- When adding new plugin features
- When fixing bugs
- When changing plugin behavior
- When adding new options
- When modifying data collection

### Test Review Checklist

- [ ] All new code has corresponding tests
- [ ] Tests pass on all supported Python versions
- [ ] Coverage remains above 85%
- [ ] No test warnings or deprecations
- [ ] Tests are documented
- [ ] Edge cases are covered

## Resources

- Python unittest documentation: https://docs.python.org/3/library/unittest.html
- Mock documentation: https://docs.python.org/3/library/unittest.mock.html
- SOS project tests: https://github.com/sosreport/sos/tree/main/tests
- Coverage.py: https://coverage.readthedocs.io/

## Support

For questions about the tests:
- Review test code comments
- Check SOS project test examples
- Open an issue on GitHub
- Contact the plugin maintainer