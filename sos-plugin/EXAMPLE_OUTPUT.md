# Example SOS Report Output for Ceph NVMe-oF Plugin

This document shows example output from the `ceph_nvmeof` SOS plugin to help understand what diagnostic information is collected.

## Report Structure

After running `sosreport -o ceph_nvmeof`, the report contains:

```
sosreport-hostname-20260428123456/
├── sos_commands/
│   └── ceph_nvmeof/
│       ├── nvme-devices
│       ├── nvme-fabrics
│       ├── nvme-ctrl-dev-nvme0
│       ├── nvme-ctrl-dev-nvme1
│       ├── nvme-perf-dev-nvme0
│       ├── block-devices
│       ├── multipath
│       ├── dmesg-nvme
│       ├── iostat
│       ├── cephadm-containers
│       ├── container-nvmeof.gateway.0
│       ├── gateway-status-nvmeof.gateway.0
│       ├── network-config
│       ├── network-stats
│       ├── firewall
│       ├── connectivity-192.168.1.100-4420
│       └── tcp-connections
├── sos_logs/
│   └── ceph_nvmeof.log
├── etc/
│   ├── nvme/
│   │   ├── hostnqn
│   │   ├── hostid
│   │   └── discovery.conf
│   ├── ceph/
│   │   ├── ceph-nvmeof.conf
│   │   └── ceph.conf
│   └── multipath.conf
├── sys/
│   └── class/
│       ├── nvme/
│       └── nvme-fabrics/
├── proc/
│   └── diskstats
└── var/
    └── log/
        └── ceph/
            └── nvmeof.gateway.0.log
```

## Example Command Outputs

### 1. NVMe Device List (`nvme-devices`)

```
Node                  Generic               SN                   Model                                    Namespace Usage                      Format           FW Rev  
--------------------- --------------------- -------------------- ---------------------------------------- --------- -------------------------- ---------------- --------
/dev/nvme0n1          /dev/ng0n1            SPDK00000000000001   Ceph bdev Controller                     1         107.37  GB / 107.37  GB    512   B +  0 B   1.0     
/dev/nvme1n1          /dev/ng1n1            SPDK00000000000002   Ceph bdev Controller                     1         107.37  GB / 107.37  GB    512   B +  0 B   1.0     
/dev/nvme2n1          /dev/ng2n1            SPDK00000000000003   Ceph bdev Controller                     1         214.75  GB / 214.75  GB    512   B +  0 B   1.0
```

### 2. NVMe Subsystem List (`nvme list-subsys`)

```
nvme-subsys0 - NQN=nqn.2016-06.io.spdk:cnode1
\
 +- nvme0 tcp traddr=192.168.1.100 trsvcid=4420 live
 +- nvme1 tcp traddr=192.168.1.101 trsvcid=4420 live

nvme-subsys1 - NQN=nqn.2016-06.io.spdk:cnode2
\
 +- nvme2 tcp traddr=192.168.1.100 trsvcid=4420 live
```

### 3. Controller Information (`nvme-ctrl-dev-nvme0`)

```
NVME Identify Controller:
vid       : 0x1af4
ssvid     : 0x1af4
sn        : SPDK00000000000001
mn        : Ceph bdev Controller
fr        : 1.0
rab       : 0
ieee      : 000000
cmic      : 0x3
  [1:1] : 0x1	Multi-port
  [0:0] : 0x1	Multi-host
mdts      : 5
cntlid    : 0x1
ver       : 0x10400
rtd3r     : 0
rtd3e     : 0
oaes      : 0
ctratt    : 0x2
  [1:1] : 0x1	128-bit Host Identifier Supported
rrls      : 0
sqes      : 0x66
cqes      : 0x44
maxcmd    : 0
nn        : 1
oncs      : 0x1f
  [4:4] : 0x1	Reservations Supported
  [3:3] : 0x1	Save and Select Supported
  [2:2] : 0x1	Write Zeroes Supported
  [1:1] : 0x1	Write Uncorrectable Supported
  [0:0] : 0x1	Compare Supported
fuses     : 0
fna       : 0
vwc       : 0x1
  [0:0] : 0x1	Volatile Write Cache Present
awun      : 0
awupf     : 0
nvscc     : 0
nwpc      : 0
acwu      : 0
sgls      : 0x50001
  [20:20] : 0x1	Transport SGL Data Block Descriptor Supported
  [16:16] : 0x1	SGL Bit Bucket Descriptor Supported
  [0:0] : 0x1	SGLs Supported
subnqn    : nqn.2016-06.io.spdk:cnode1
```

### 4. SMART Log (`nvme-perf-dev-nvme0`)

```
Smart Log for NVME device:nvme0 namespace-id:ffffffff
critical_warning                    : 0
temperature                         : 0 C
available_spare                     : 100%
available_spare_threshold           : 10%
percentage_used                     : 0%
data_units_read                     : 1,234,567
data_units_written                  : 2,345,678
host_read_commands                  : 12,345,678
host_write_commands                 : 23,456,789
controller_busy_time                : 123
power_cycles                        : 1
power_on_hours                      : 720
unsafe_shutdowns                    : 0
media_errors                        : 0
num_err_log_entries                 : 0
Warning Temperature Time            : 0
Critical Composite Temperature Time : 0
```

### 5. Block Devices (`block-devices`)

```
NAME        SIZE TYPE FSTYPE MOUNTPOINT                UUID                                 MODEL              SERIAL
nvme0n1   100G disk                                                                         Ceph bdev Controller SPDK00000000000001
nvme1n1   100G disk                                                                         Ceph bdev Controller SPDK00000000000002
nvme2n1   200G disk xfs    /mnt/data                 a1b2c3d4-e5f6-7890-abcd-ef1234567890 Ceph bdev Controller SPDK00000000000003
sda       500G disk                                                                         
├─sda1      1G part vfat   /boot/efi                 ABCD-1234
├─sda2      1G part xfs    /boot                     12345678-90ab-cdef-1234-567890abcdef
└─sda3    498G part LVM2_member                      aBcDeF12-3456-7890-aBcD-eFaBcDeF1234
```

### 6. Multipath Topology (`multipath`)

```
mpatha (36001405d27e3f9d7274e8c9b7c6e8c9e) dm-0 SPDK,Ceph bdev Controller
size=100G features='1 queue_if_no_path' hwhandler='0' wp=rw
|-+- policy='service-time 0' prio=50 status=active
| `- 0:0:1:0 nvme0n1 259:0 active ready running
`-+- policy='service-time 0' prio=10 status=enabled
  `- 1:0:1:0 nvme1n1 259:1 active ready running
```

### 7. Kernel Messages (`dmesg-nvme`)

```
[    5.123456] nvme nvme0: pci function 0000:00:04.0
[    5.234567] nvme 0000:00:04.0: enabling device (0000 -> 0002)
[    5.345678] nvme nvme0: Identify Controller failed (19)
[    5.456789] nvme nvme0: Removing after probe failure status: -5
[    6.123456] nvme_tcp: loading out-of-tree module taints kernel.
[    6.234567] nvme_tcp: module verification failed: signature and/or required key missing - tainting kernel
[   10.123456] nvme nvme0: new ctrl: NQN "nqn.2016-06.io.spdk:cnode1", addr 192.168.1.100:4420
[   10.234567] nvme nvme0: creating 4 I/O queues.
[   10.345678] nvme nvme0: mapped 4/0/0 default/read/poll queues.
[   10.456789] nvme nvme0: new ctrl: NQN "nqn.2016-06.io.spdk:cnode1", addr 192.168.1.100:4420, hostnqn: nqn.2014-08.org.nvmexpress:uuid:12345678-1234-1234-1234-123456789abc
[   15.123456] nvme nvme1: new ctrl: NQN "nqn.2016-06.io.spdk:cnode1", addr 192.168.1.101:4420
[   20.123456] nvme nvme2: new ctrl: NQN "nqn.2016-06.io.spdk:cnode2", addr 192.168.1.100:4420
```

### 8. I/O Statistics (`iostat`)

```
Device            r/s     w/s     rkB/s     wkB/s   rrqm/s   wrqm/s  %rrqm  %wrqm r_await w_await aqu-sz rareq-sz wareq-sz  svctm  %util
nvme0n1        123.45   67.89   1234.56    678.90     0.12     0.34   0.10   0.50    0.45    1.23   0.01    10.00    10.00   0.12   2.34
nvme1n1         98.76   54.32    987.65    543.21     0.09     0.28   0.09   0.51    0.48    1.28   0.01    10.00    10.00   0.13   1.98
nvme2n1        234.56  123.45   2345.67   1234.56     0.23     0.56   0.10   0.45    0.42    1.15   0.02    10.00    10.00   0.11   3.45
```

### 9. Gateway Container List (`cephadm-containers`)

```json
[
  {
    "style": "cephadm:v1",
    "name": "nvmeof.gateway.0",
    "fsid": "12345678-1234-1234-1234-123456789abc",
    "systemd_unit": "ceph-12345678-1234-1234-1234-123456789abc@nvmeof.gateway.0",
    "enabled": true,
    "state": "running",
    "container_id": "abcdef1234567890",
    "container_image_name": "quay.io/ceph/nvmeof:latest",
    "container_image_id": "1234567890abcdef",
    "version": "1.0.0",
    "started": "2026-04-28T10:00:00.000000Z",
    "created": "2026-04-28T09:55:00.000000Z"
  }
]
```

### 10. Gateway Status (`gateway-status-nvmeof.gateway.0`)

```json
{
  "gateways": [
    {
      "name": "gateway1",
      "group": "group1",
      "addr": "192.168.1.100",
      "port": 5500,
      "load_balancing_group": 1,
      "spdk_version": "23.01",
      "status": "Optimized",
      "hostname": "ceph-node1"
    }
  ],
  "subsystems": [
    {
      "nqn": "nqn.2016-06.io.spdk:cnode1",
      "serial_number": "SPDK00000000000001",
      "model_number": "Ceph bdev Controller",
      "max_namespaces": 256,
      "namespace_count": 1,
      "subtype": "NVMe"
    }
  ],
  "namespaces": [
    {
      "subsystem_nqn": "nqn.2016-06.io.spdk:cnode1",
      "nsid": 1,
      "bdev_name": "rbd_pool_image1",
      "rbd_pool_name": "rbd",
      "rbd_image_name": "image1",
      "block_size": 512,
      "size": 107374182400,
      "load_balancing_group": 1
    }
  ],
  "listeners": [
    {
      "subsystem_nqn": "nqn.2016-06.io.spdk:cnode1",
      "gateway_name": "gateway1",
      "trtype": "TCP",
      "traddr": "192.168.1.100",
      "trsvcid": 4420,
      "adrfam": "IPv4"
    }
  ],
  "hosts": [
    {
      "subsystem_nqn": "nqn.2016-06.io.spdk:cnode1",
      "host_nqn": "nqn.2014-08.org.nvmexpress:uuid:12345678-1234-1234-1234-123456789abc"
    }
  ],
  "connections": [
    {
      "nqn": "nqn.2016-06.io.spdk:cnode1",
      "host_nqn": "nqn.2014-08.org.nvmexpress:uuid:12345678-1234-1234-1234-123456789abc",
      "traddr": "192.168.1.50",
      "connected": true,
      "qpairs_count": 4
    }
  ]
}
```

### 11. Network Configuration (`network-config`)

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    link/ether 52:54:00:12:34:56 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.50/24 brd 192.168.1.255 scope global dynamic eth0
       valid_lft 86395sec preferred_lft 86395sec
    inet6 fe80::5054:ff:fe12:3456/64 scope link 
       valid_lft forever preferred_lft forever
```

### 12. TCP Connections (`tcp-connections`)

```
State      Recv-Q Send-Q Local Address:Port               Peer Address:Port              
ESTAB      0      0      192.168.1.50:45678              192.168.1.100:4420              
ESTAB      0      0      192.168.1.50:45679              192.168.1.100:4420              
ESTAB      0      0      192.168.1.50:45680              192.168.1.100:4420              
ESTAB      0      0      192.168.1.50:45681              192.168.1.100:4420              
ESTAB      0      0      192.168.1.50:45682              192.168.1.101:4420              
ESTAB      0      0      192.168.1.50:45683              192.168.1.101:4420
```

### 13. Connectivity Test (`connectivity-192.168.1.100-4420`)

```
Connection to 192.168.1.100 4420 port [tcp/*] succeeded!
```

## Configuration Files

### `/etc/nvme/hostnqn`

```
nqn.2014-08.org.nvmexpress:uuid:12345678-1234-1234-1234-123456789abc
```

### `/etc/nvme/discovery.conf`

```
# Used for extracting default parameters for discovery
#
# Example:
# --transport=<trtype> --traddr=<traddr> --trsvcid=<trsvcid> --host-traddr=<host-traddr> --host-iface=<host-iface>

--transport=tcp --traddr=192.168.1.100 --trsvcid=8009
--transport=tcp --traddr=192.168.1.101 --trsvcid=8009
```

### `/etc/ceph/ceph-nvmeof.conf` (Sanitized)

```
[gateway]
name = gateway1
group = group1
addr = 0.0.0.0
port = 5500
enable_auth = True
encryption_key = ********

[gateway-logs]
log_level = debug

[ceph]
pool = rbd
config_file = /etc/ceph/ceph.conf

[mtls]
server_key = ********
client_key = ********
server_cert = ./server.crt
client_cert = ./client.crt

[spdk]
cluster_connections = 32
tgt_path = /usr/local/bin/nvmf_tgt
timeout = 60.0
```

## System Information

### `/sys/class/nvme/nvme0/transport`

```
tcp
```

### `/sys/class/nvme/nvme0/address`

```
traddr=192.168.1.100,trsvcid=4420
```

### `/sys/class/nvme/nvme0/state`

```
live
```

### `/proc/diskstats`

```
 259       0 nvme0n1 123456 0 9876543 12345 67890 0 5432109 6789 0 12345 19134 0 0 0 0
 259       1 nvme1n1 98765 0 7654321 9876 54321 0 4321098 5432 0 9876 15308 0 0 0 0
 259       2 nvme2n1 234567 0 18765432 23456 123456 0 9876543 12345 0 23456 35801 0 0 0 0
```

## Log Excerpts

### Gateway Log (Sanitized)

```
2026-04-28 10:00:00,123 INFO Starting Ceph NVMe-oF Gateway version 1.0.0
2026-04-28 10:00:01,234 INFO Loading configuration from /etc/ceph/ceph-nvmeof.conf
2026-04-28 10:00:02,345 INFO Connecting to Ceph cluster
2026-04-28 10:00:03,456 INFO Connected to Ceph cluster, fsid: 12345678-1234-1234-1234-123456789abc
2026-04-28 10:00:04,567 INFO Starting SPDK target
2026-04-28 10:00:05,678 INFO SPDK target started successfully
2026-04-28 10:00:06,789 INFO Creating subsystem nqn.2016-06.io.spdk:cnode1
2026-04-28 10:00:07,890 INFO Adding namespace 1 to subsystem nqn.2016-06.io.spdk:cnode1
2026-04-28 10:00:08,901 INFO Adding listener 192.168.1.100:4420 to subsystem nqn.2016-06.io.spdk:cnode1
2026-04-28 10:00:09,012 INFO Gateway ready, listening on 192.168.1.100:5500
```

## Summary Statistics

This example shows a typical collection from an initiator with:
- 3 NVMe-oF devices connected
- 2 gateway targets (multipath)
- Active I/O operations
- Healthy connection status
- No errors or warnings

The complete sosreport tarball would be approximately 20-50 MB compressed, containing all the diagnostic information needed for troubleshooting Ceph NVMe-oF deployments.