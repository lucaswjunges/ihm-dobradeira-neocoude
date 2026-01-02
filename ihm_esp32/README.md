# Industrial HMI for NEOCOUDE-HD-15 Rebar Bending Machine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi%203B%2B-red.svg)](https://www.raspberrypi.com/)
[![Status: Production](https://img.shields.io/badge/status-production-green.svg)](https://github.com/lucaswjunges/ihm-dobradeira-neocoude)

> **Modern web-based Human-Machine Interface (HMI) for industrial automation, replacing a damaged physical control panel with a tablet-accessible solution running on Raspberry Pi 3B+.**

---

## 🎯 Project Overview

This project modernizes a 2007 **NEOCOUDE-HD-15 rebar bending machine** (capacity: 50mm/2" diameter steel bars) by replacing its damaged physical HMI panel (Atos MPC4004) with a **responsive web-based interface** accessible from tablets via WiFi.

### Key Features

- ✅ **Modbus RTU Communication** - RS485 interface to Atos Expert MPC4004 PLC
- ✅ **WebSocket Real-Time Updates** - Bidirectional communication (Python backend ↔ JavaScript frontend)
- ✅ **WiFi Dual-Mode Networking** - Simultaneous Access Point + Station mode
- ✅ **NAT/Policy Routing** - Internet sharing from factory WiFi to mobile clients
- ✅ **Production-Ready** - Automated boot configuration, error recovery, systemd services

---

## 🛠️ Technical Stack

### Hardware
- **Controller:** Raspberry Pi 3B+ (ARM Cortex-A53 1.4GHz, 1GB RAM)
- **PLC:** Atos Expert Series MPC4004 (legacy industrial controller)
- **Interfaces:**
  - USB-RS485 converter (FTDI/CH340 chipset)
  - USB WiFi dongle (RTL8188CUS) for factory network
  - Built-in WiFi (BCM43438) for Access Point mode

### Software & Frameworks
- **Backend:** Python 3.11 (asyncio, websockets, pymodbus)
- **Frontend:** Vanilla JavaScript (ES6+), HTML5, CSS3 (no frameworks - lightweight)
- **Networking:**
  - dnsmasq (DNS proxy + DHCP server)
  - hostapd (WiFi Access Point)
  - iptables/nftables (NAT/MASQUERADE)
  - iproute2 (policy-based routing)
- **System:** systemd services, bash automation scripts

---

## 🚀 Key Technical Achievements

### 1. WiFi-to-WiFi Internet Sharing (Advanced Networking)

**Challenge:** Raspberry Pi has only one internal WiFi adapter. How to simultaneously:
- Connect to factory WiFi (Station mode) for internet access
- Host WiFi Access Point for tablets

**Solution:**
- USB WiFi dongle (wlan1) in **STA mode** → factory network (192.168.0.0/24)
- Internal WiFi (wlan0) in **AP mode** → tablets (192.168.50.0/24)
- **Policy-based routing** with iproute2 (separate routing table for AP traffic)
- **NAT/MASQUERADE** with iptables for address translation

**Technical Details:** See [INTERNET_SHARING_SETUP.md](INTERNET_SHARING_SETUP.md)

**Performance Metrics:**
```bash
$ sudo iptables -L FORWARD -v -n
7,144 packets (1.2 MB) forwarded: client → internet
23,272 packets (28 MB) forwarded: internet → client
```

### 2. Modbus RTU Industrial Protocol

**Challenge:** Communicate with a 2007-era PLC using legacy Modbus RTU protocol over RS485.

**Implementation:**
- **32-bit register reading:** Paired registers (MSW/LSW) for encoder values
- **Button simulation:** Force Single Coil (0x05) with 100ms hold time
- **Error recovery:** Automatic reconnection, timeout handling
- **Stub mode:** Development without hardware (mock PLC responses)

---

## 📊 Performance & Scalability

| Metric | Value | Notes |
|--------|-------|-------|
| **Boot Time** | ~40s | RPi startup + services initialization |
| **Modbus Latency** | ~30ms | PLC read/write roundtrip |
| **WebSocket Latency** | ~300ms | State update propagation |
| **Button Response** | ~50ms | Click → PLC command |
| **Concurrent Clients** | 10-15 | Limited by WiFi AP capacity |
| **Network Throughput** | ~20 Mbps | Factory WiFi bottleneck |

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [INTERNET_SHARING_SETUP.md](INTERNET_SHARING_SETUP.md) | Advanced networking guide (WiFi NAT/routing) |
| [COMPARTILHAMENTO_INTERNET.md](COMPARTILHAMENTO_INTERNET.md) | Portuguese documentation |
| [CLAUDE.md](CLAUDE.md) | Project specifications & context |

---

## 👨‍💻 Author

**Lucas William Junges**  
Electrical Engineer | Industrial Automation & Control Systems

[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/lucaswjunges/)
[![GitHub](https://img.shields.io/badge/GitHub-black?style=flat&logo=github)](https://github.com/lucaswjunges)

**Industry Experience:**
- Industrial IoT & HMI Development
- Embedded Linux on ARM platforms
- PLC Programming (Ladder Logic, Modbus RTU)
- Network Engineering (WiFi, NAT, Policy Routing)
- Real-time control systems

**Contact:** Open to collaboration and job opportunities in Europe.

---

## 📌 Project Status

| Milestone | Status | Date |
|-----------|--------|------|
| Hardware Setup | ✅ Complete | Nov 2025 |
| Modbus Communication | ✅ Complete | Nov 2025 |
| Web Interface (Basic) | ✅ Complete | Nov 2025 |
| WiFi Networking (NAT) | ✅ Complete | Jan 2026 |
| Production Deployment | ✅ Complete | Jan 2026 |
| Data Logging | 🔄 In Progress | - |
| Remote Monitoring | 📋 Planned | - |

---

<p align="center">
  <strong>⭐ If you find this project useful, please consider starring it on GitHub! ⭐</strong>
</p>

<p align="center">
  <sub>Built with ❤️ for the industrial automation community</sub>
</p>
