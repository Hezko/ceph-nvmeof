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
Unit tests for the Ceph NVMe-oF SOS plugin.

These tests verify the plugin's functionality including:
- Plugin initialization and options
- NVMe controller detection
- Gateway node detection
- Data collection methods
- Data sanitization
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open
import os
import json

# Import the plugin (adjust path as needed for your test environment)
try:
    from sos.report.plugins.ceph_nvmeof import CephNvmeof
except ImportError:
    # For development/testing without full SOS installation
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ceph_nvmeof import CephNvmeof


class TestCephNvmeofPlugin(unittest.TestCase):
    """Test cases for the CephNvmeof plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.plugin = CephNvmeof(commons={
            'cmdlineopts': Mock(),
            'policy': Mock(),
        })
        
        # Mock common plugin methods
        self.plugin.add_cmd_output = Mock()
        self.plugin.add_copy_spec = Mock()
        self.plugin.add_journal = Mock()
        self.plugin.is_installed = Mock(return_value=True)
        self.plugin.exec_cmd = Mock()
        self.plugin.get_option = Mock(return_value=None)
        self.plugin._log_warn = Mock()
        self.plugin.do_cmd_output_sub = Mock()
        self.plugin.do_file_sub = Mock()

    def test_plugin_initialization(self):
        """Test plugin initializes with correct attributes."""
        self.assertEqual(self.plugin.plugin_name, 'ceph_nvmeof')
        self.assertEqual(self.plugin.short_desc, 'Ceph NVMe over Fabrics (NVMe-oF)')
        self.assertIn('storage', self.plugin.profiles)
        self.assertIn('ceph', self.plugin.profiles)
        self.assertIn('nvme', self.plugin.profiles)

    def test_plugin_options(self):
        """Test plugin has all expected options."""
        option_names = [opt[0] for opt in self.plugin.option_list]
        self.assertIn('initiator-only', option_names)
        self.assertIn('gateway-only', option_names)
        self.assertIn('no-performance', option_names)
        self.assertIn('no-logs', option_names)
        self.assertIn('gateway-address', option_names)

    def test_get_nvme_controllers_empty(self):
        """Test _get_nvme_controllers with no devices."""
        with patch('os.path.exists', return_value=False):
            controllers = self.plugin._get_nvme_controllers()
            self.assertEqual(controllers, [])

    def test_get_nvme_controllers_with_devices(self):
        """Test _get_nvme_controllers with multiple devices."""
        mock_devices = ['nvme0', 'nvme1', 'nvme2', 'nvme0n1', 'sda']
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_devices):
            controllers = self.plugin._get_nvme_controllers()
            
            # Should only return nvme controllers, not namespaces or other devices
            self.assertEqual(len(controllers), 3)
            self.assertIn('/dev/nvme0', controllers)
            self.assertIn('/dev/nvme1', controllers)
            self.assertIn('/dev/nvme2', controllers)
            self.assertNotIn('/dev/nvme0n1', controllers)
            self.assertNotIn('/dev/sda', controllers)

    def test_get_nvme_controllers_sorted(self):
        """Test _get_nvme_controllers returns sorted list."""
        mock_devices = ['nvme2', 'nvme0', 'nvme1']
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_devices):
            controllers = self.plugin._get_nvme_controllers()
            
            self.assertEqual(controllers, ['/dev/nvme0', '/dev/nvme1', '/dev/nvme2'])

    def test_get_nvme_controllers_exception_handling(self):
        """Test _get_nvme_controllers handles exceptions gracefully."""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', side_effect=PermissionError("Access denied")):
            controllers = self.plugin._get_nvme_controllers()
            
            self.assertEqual(controllers, [])
            self.plugin._log_warn.assert_called()

    def test_is_gateway_node_no_cephadm(self):
        """Test _is_gateway_node returns False when cephadm not installed."""
        self.plugin.is_installed = Mock(return_value=False)
        
        result = self.plugin._is_gateway_node()
        
        self.assertFalse(result)
        self.plugin.is_installed.assert_called_with('cephadm')

    def test_is_gateway_node_no_containers(self):
        """Test _is_gateway_node returns False when no gateway containers."""
        self.plugin.is_installed = Mock(return_value=True)
        self.plugin.exec_cmd = Mock(return_value={
            'status': 0,
            'output': '[]'
        })
        
        result = self.plugin._is_gateway_node()
        
        self.assertFalse(result)

    def test_is_gateway_node_with_containers(self):
        """Test _is_gateway_node returns True when gateway containers exist."""
        self.plugin.is_installed = Mock(return_value=True)
        mock_cephadm_output = json.dumps([
            {'service_name': 'nvmeof.gateway.0', 'container_id': 'abc123'},
            {'service_name': 'mon.a', 'container_id': 'def456'}
        ])
        self.plugin.exec_cmd = Mock(return_value={
            'status': 0,
            'output': mock_cephadm_output
        })
        
        result = self.plugin._is_gateway_node()
        
        self.assertTrue(result)

    def test_get_gateway_containers_empty(self):
        """Test _get_gateway_containers with no containers."""
        self.plugin.exec_cmd = Mock(return_value={
            'status': 0,
            'output': '[]'
        })
        
        containers = self.plugin._get_gateway_containers()
        
        self.assertEqual(containers, [])

    def test_get_gateway_containers_with_nvmeof(self):
        """Test _get_gateway_containers finds nvmeof containers."""
        mock_cephadm_output = json.dumps([
            {'service_name': 'nvmeof.gateway.0', 'container_id': 'abc123'},
            {'service_name': 'nvmeof.gateway.1', 'container_name': 'nvmeof-gw-1'},
            {'service_name': 'mon.a', 'container_id': 'def456'}
        ])
        self.plugin.exec_cmd = Mock(return_value={
            'status': 0,
            'output': mock_cephadm_output
        })
        
        containers = self.plugin._get_gateway_containers()
        
        self.assertEqual(len(containers), 2)
        self.assertIn('abc123', containers)
        self.assertIn('nvmeof-gw-1', containers)

    def test_get_gateway_containers_exception_handling(self):
        """Test _get_gateway_containers handles exceptions."""
        self.plugin.exec_cmd = Mock(return_value={
            'status': 1,
            'output': 'Error'
        })
        
        containers = self.plugin._get_gateway_containers()
        
        self.assertEqual(containers, [])

    def test_collect_initiator_diagnostics_basic(self):
        """Test _collect_initiator_diagnostics collects basic commands."""
        with patch.object(self.plugin, '_get_nvme_controllers', return_value=[]):
            self.plugin._collect_initiator_diagnostics(
                collect_performance=False,
                collect_logs=False
            )
        
        # Verify basic NVMe commands were added
        self.plugin.add_cmd_output.assert_called()
        calls = self.plugin.add_cmd_output.call_args_list
        
        # Check for nvme list commands
        cmd_lists = [call[0][0] for call in calls]
        nvme_list_found = any('nvme list' in str(cmds) for cmds in cmd_lists)
        self.assertTrue(nvme_list_found, "nvme list command should be collected")

    def test_collect_initiator_diagnostics_with_controllers(self):
        """Test _collect_initiator_diagnostics with NVMe controllers."""
        mock_controllers = ['/dev/nvme0', '/dev/nvme1']
        
        with patch.object(self.plugin, '_get_nvme_controllers', 
                         return_value=mock_controllers):
            self.plugin._collect_initiator_diagnostics(
                collect_performance=True,
                collect_logs=False
            )
        
        # Verify controller-specific commands were added
        calls = self.plugin.add_cmd_output.call_args_list
        cmd_lists = [call[0][0] for call in calls]
        
        # Check for controller-specific commands
        id_ctrl_found = any('nvme id-ctrl /dev/nvme0' in str(cmds) 
                           for cmds in cmd_lists)
        smart_log_found = any('nvme smart-log /dev/nvme0' in str(cmds) 
                             for cmds in cmd_lists)
        
        self.assertTrue(id_ctrl_found, "Controller ID command should be collected")
        self.assertTrue(smart_log_found, "SMART log should be collected")

    def test_collect_initiator_diagnostics_skip_performance(self):
        """Test _collect_initiator_diagnostics skips performance when disabled."""
        mock_controllers = ['/dev/nvme0']
        
        with patch.object(self.plugin, '_get_nvme_controllers', 
                         return_value=mock_controllers):
            self.plugin._collect_initiator_diagnostics(
                collect_performance=False,
                collect_logs=False
            )
        
        # Verify performance commands were NOT added
        calls = self.plugin.add_cmd_output.call_args_list
        cmd_lists = [call[0][0] for call in calls]
        
        smart_log_found = any('nvme smart-log' in str(cmds) 
                             for cmds in cmd_lists)
        iostat_found = any('iostat' in str(cmds) for cmds in cmd_lists)
        
        self.assertFalse(smart_log_found, "SMART log should be skipped")
        self.assertFalse(iostat_found, "iostat should be skipped")

    def test_collect_initiator_diagnostics_with_logs(self):
        """Test _collect_initiator_diagnostics collects logs when enabled."""
        with patch.object(self.plugin, '_get_nvme_controllers', return_value=[]):
            self.plugin._collect_initiator_diagnostics(
                collect_performance=False,
                collect_logs=True
            )
        
        # Verify log collection methods were called
        self.plugin.add_journal.assert_called()
        
        # Check for dmesg commands
        calls = self.plugin.add_cmd_output.call_args_list
        cmd_lists = [call[0][0] for call in calls]
        dmesg_found = any('dmesg' in str(cmds) for cmds in cmd_lists)
        
        self.assertTrue(dmesg_found, "dmesg should be collected")

    def test_collect_gateway_diagnostics_not_gateway(self):
        """Test _collect_gateway_diagnostics skips when not a gateway node."""
        with patch.object(self.plugin, '_is_gateway_node', return_value=False):
            self.plugin._collect_gateway_diagnostics(collect_logs=True)
        
        # Should return early without collecting anything
        # Verify no container-specific commands were added
        if self.plugin.add_cmd_output.called:
            calls = self.plugin.add_cmd_output.call_args_list
            cmd_lists = [call[0][0] for call in calls]
            cephadm_found = any('cephadm' in str(cmds) for cmds in cmd_lists)
            self.assertFalse(cephadm_found, 
                           "cephadm commands should not be collected")

    def test_collect_gateway_diagnostics_with_containers(self):
        """Test _collect_gateway_diagnostics collects container info."""
        mock_containers = ['nvmeof-gw-0', 'nvmeof-gw-1']
        
        with patch.object(self.plugin, '_is_gateway_node', return_value=True), \
             patch.object(self.plugin, '_get_gateway_containers', 
                         return_value=mock_containers):
            self.plugin._collect_gateway_diagnostics(collect_logs=True)
        
        # Verify container commands were added
        calls = self.plugin.add_cmd_output.call_args_list
        cmd_lists = [call[0][0] for call in calls]
        
        # Check for container-specific commands
        podman_inspect_found = any('podman inspect' in str(cmds) 
                                  for cmds in cmd_lists)
        gateway_cli_found = any('control.cli' in str(cmds) 
                               for cmds in cmd_lists)
        
        self.assertTrue(podman_inspect_found, 
                       "Container inspect should be collected")
        self.assertTrue(gateway_cli_found, 
                       "Gateway CLI commands should be collected")

    def test_collect_network_diagnostics(self):
        """Test _collect_network_diagnostics collects network info."""
        self.plugin._collect_network_diagnostics()
        
        # Verify network commands were added
        calls = self.plugin.add_cmd_output.call_args_list
        cmd_lists = [call[0][0] for call in calls]
        
        # Check for network commands
        ip_addr_found = any('ip addr' in str(cmds) for cmds in cmd_lists)
        netstat_found = any('netstat' in str(cmds) or 'ss' in str(cmds) 
                           for cmds in cmd_lists)
        
        self.assertTrue(ip_addr_found, "IP address info should be collected")
        self.assertTrue(netstat_found, "Network stats should be collected")

    def test_collect_network_diagnostics_with_gateway_address(self):
        """Test _collect_network_diagnostics with gateway address."""
        self.plugin.get_option = Mock(return_value='192.168.1.100')
        
        self.plugin._collect_network_diagnostics()
        
        # Verify connectivity tests were added
        calls = self.plugin.add_cmd_output.call_args_list
        cmd_lists = [call[0][0] for call in calls]
        
        # Check for connectivity commands
        ping_found = any('ping' in str(cmds) and '192.168.1.100' in str(cmds) 
                        for cmds in cmd_lists)
        nc_found = any('nc' in str(cmds) and '192.168.1.100' in str(cmds) 
                      for cmds in cmd_lists)
        
        self.assertTrue(ping_found or nc_found, 
                       "Connectivity tests should be collected")

    def test_setup_default_options(self):
        """Test setup() with default options."""
        self.plugin.get_option = Mock(return_value=False)
        
        with patch.object(self.plugin, '_collect_initiator_diagnostics'), \
             patch.object(self.plugin, '_collect_gateway_diagnostics'), \
             patch.object(self.plugin, '_collect_network_diagnostics'):
            
            self.plugin.setup()
            
            # Verify all collection methods were called
            self.plugin._collect_initiator_diagnostics.assert_called_once()
            self.plugin._collect_gateway_diagnostics.assert_called_once()
            self.plugin._collect_network_diagnostics.assert_called_once()

    def test_setup_initiator_only(self):
        """Test setup() with initiator-only option."""
        def get_option_side_effect(opt):
            return opt == 'initiator-only'
        
        self.plugin.get_option = Mock(side_effect=get_option_side_effect)
        
        with patch.object(self.plugin, '_collect_initiator_diagnostics'), \
             patch.object(self.plugin, '_collect_gateway_diagnostics'), \
             patch.object(self.plugin, '_collect_network_diagnostics'):
            
            self.plugin.setup()
            
            # Verify only initiator and network were called
            self.plugin._collect_initiator_diagnostics.assert_called_once()
            self.plugin._collect_gateway_diagnostics.assert_not_called()
            self.plugin._collect_network_diagnostics.assert_called_once()

    def test_setup_gateway_only(self):
        """Test setup() with gateway-only option."""
        def get_option_side_effect(opt):
            return opt == 'gateway-only'
        
        self.plugin.get_option = Mock(side_effect=get_option_side_effect)
        
        with patch.object(self.plugin, '_collect_initiator_diagnostics'), \
             patch.object(self.plugin, '_collect_gateway_diagnostics'), \
             patch.object(self.plugin, '_collect_network_diagnostics'):
            
            self.plugin.setup()
            
            # Verify only gateway and network were called
            self.plugin._collect_initiator_diagnostics.assert_not_called()
            self.plugin._collect_gateway_diagnostics.assert_called_once()
            self.plugin._collect_network_diagnostics.assert_called_once()

    def test_postproc_sanitizes_dhchap_keys(self):
        """Test postproc() sanitizes DHCHAP keys."""
        self.plugin.postproc()
        
        # Verify sanitization methods were called
        self.plugin.do_cmd_output_sub.assert_called()
        
        # Check for DHCHAP key sanitization
        calls = self.plugin.do_cmd_output_sub.call_args_list
        dhchap_sanitized = any('dhchap' in str(call).lower() 
                              for call in calls)
        
        self.assertTrue(dhchap_sanitized, 
                       "DHCHAP keys should be sanitized")

    def test_postproc_sanitizes_config_keys(self):
        """Test postproc() sanitizes configuration keys."""
        self.plugin.postproc()
        
        # Verify file substitution was called
        self.plugin.do_file_sub.assert_called()
        
        # Check for config key sanitization
        calls = self.plugin.do_file_sub.call_args_list
        key_sanitized = any('key' in str(call).lower() 
                           for call in calls)
        
        self.assertTrue(key_sanitized, 
                       "Configuration keys should be sanitized")

    def test_postproc_sanitizes_tokens(self):
        """Test postproc() sanitizes authentication tokens."""
        self.plugin.postproc()
        
        # Check for token sanitization
        calls = self.plugin.do_cmd_output_sub.call_args_list
        token_sanitized = any('token' in str(call).lower() or 
                             'auth' in str(call).lower() 
                             for call in calls)
        
        self.assertTrue(token_sanitized, 
                       "Authentication tokens should be sanitized")


class TestCephNvmeofPluginIntegration(unittest.TestCase):
    """Integration tests for the CephNvmeof plugin."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.plugin = CephNvmeof(commons={
            'cmdlineopts': Mock(),
            'policy': Mock(),
        })
        
        # Mock plugin methods but allow real logic to run
        self.plugin.add_cmd_output = Mock()
        self.plugin.add_copy_spec = Mock()
        self.plugin.add_journal = Mock()
        self.plugin.is_installed = Mock(return_value=True)
        self.plugin.get_option = Mock(return_value=False)
        self.plugin._log_warn = Mock()

    def test_full_initiator_collection(self):
        """Test full initiator collection workflow."""
        mock_controllers = ['/dev/nvme0', '/dev/nvme1']
        
        with patch.object(self.plugin, '_get_nvme_controllers', 
                         return_value=mock_controllers), \
             patch.object(self.plugin, '_is_gateway_node', 
                         return_value=False):
            
            self.plugin.setup()
            
            # Verify comprehensive collection
            self.assertGreater(self.plugin.add_cmd_output.call_count, 10,
                             "Should collect multiple commands")
            self.assertGreater(self.plugin.add_copy_spec.call_count, 5,
                             "Should collect multiple file specs")

    def test_full_gateway_collection(self):
        """Test full gateway collection workflow."""
        mock_containers = ['nvmeof-gw-0']
        mock_cephadm_output = json.dumps([
            {'service_name': 'nvmeof.gateway.0', 'container_id': 'nvmeof-gw-0'}
        ])
        
        self.plugin.exec_cmd = Mock(return_value={
            'status': 0,
            'output': mock_cephadm_output
        })
        
        with patch.object(self.plugin, '_get_nvme_controllers', 
                         return_value=[]), \
             patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=[]):
            
            self.plugin.setup()
            
            # Verify gateway collection
            calls = self.plugin.add_cmd_output.call_args_list
            cmd_lists = [call[0][0] for call in calls]
            
            cephadm_found = any('cephadm' in str(cmds) 
                               for cmds in cmd_lists)
            self.assertTrue(cephadm_found, 
                           "Gateway commands should be collected")


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test cases
    suite.addTests(loader.loadTestsFromTestCase(TestCephNvmeofPlugin))
    suite.addTests(loader.loadTestsFromTestCase(TestCephNvmeofPluginIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)

# Made with Bob
