# Web-Based HMI for Industrial Hydraulic Rebar Bending Machine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi%203B%2B-red.svg)](https://www.raspberrypi.org/)
[![Modbus RTU](https://img.shields.io/badge/protocol-Modbus%20RTU-green.svg)](https://modbus.org/)

> **Industrial Modernization Project**: Complete replacement of a damaged physical HMI panel (€2000+) with a modern, tablet-based web interface for a 2007 NEOCOUDE-HD-15 hydraulic rebar bending machine controlled by an Atos MPC4004 PLC.

---

## 🎯 Project Overview

This project provides a **production-ready industrial HMI** (Human-Machine Interface) system that modernizes a legacy rebar bending machine by:

- Replacing a damaged €2000+ physical HMI panel with a **web-based solution**
- Enabling **tablet-based operation** for improved ergonomics
- Adding **remote monitoring** via WiFi and VPN (Tailscale)
- Implementing **intelligent auto-calibration** for zero-point detection
- Providing **real-time production tracking** and maintenance logs

### Target Machine Specifications

- **Machine**: NEOCOUDE-HD-15 (Trillor, 2007)
- **Controller**: Atos Expert MPC4004 PLC
- **Motor**: 15 HP, 1755 RPM @ 380V, 23A
- **Capacity**: Up to 50mm (2") CA-25 steel, 44mm CA-50 steel
- **Encoder**: 400 PPR incremental (model 2.018.200)
- **Communication**: Modbus RTU @ 57600 baud (RS485-B channel)

---

## ✨ Key Features

### 🚀 Real-Time Control
- **< 50ms latency** from user input to PLC command
- **4 Hz polling rate** for smooth encoder position tracking
- **±0.9° precision** (400 PPR encoder resolution)
- **WebSocket-based** real-time data streaming to web clients

### 🤖 Intelligent Auto-Calibration
7-step calibration sequence:
1. Exit sensor zone
2. Hydraulic warm-up (30s optional)
3. Sensor mapping
4. Zero calculation
5. Ballistic inertia test
6. Physics modeling
7. Parameter storage

See [CLAUDE.md](CLAUDE.md) for detailed documentation.

---

## 🚀 Quick Start

### Installation

\`\`\`bash
# Clone repository
git clone https://github.com/lucaswjunges/ihm-dobradeira-neocoude.git
cd ihm-dobradeira-neocoude

# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run server
python3 main_server.py
\`\`\`

### Access

Open browser: \`http://localhost:8080\`

---

## 📖 Documentation

- **[CLAUDE.md](CLAUDE.md)** - Complete technical documentation (English)
- **[README_PT-BR.md](README_PT-BR.md)** - Documentação em Português

---

## 👤 Author

**Lucas William Junges**  
Control & Automation Engineer | Industrial AI Specialist  
🌍 EU Work Authorization (Italian Citizenship)  
📧 [lucaswjunges@gmail.com](mailto:lucaswjunges@gmail.com)  
💼 [LinkedIn](https://www.linkedin.com/in/lucas-william-junges-a95b00143)  
🌐 [Portfolio](https://lucaswjunges.github.io)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
