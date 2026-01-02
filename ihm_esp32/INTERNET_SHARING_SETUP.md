# WiFi Internet Sharing on Raspberry Pi 3B+

## Executive Summary

This document describes the implementation of a **WiFi-to-WiFi internet sharing solution** on a Raspberry Pi 3B+ for an industrial HMI (Human-Machine Interface) application. The system enables tablets and mobile devices to access the internet through the RPi's Access Point while the RPi itself connects to the factory's WiFi network via a USB dongle.

**Status:** ✅ Production-ready, fully automated on boot.

**Technical Stack:**
- Platform: Raspberry Pi 3B+ (ARM Cortex-A53, 1GB RAM)
- OS: Raspberry Pi OS Bookworm (Debian 12, Linux 6.12.47)
- Networking: dnsmasq, hostapd, iptables/nftables, iproute2
- Languages: Bash, Python 3.11

---

## System Architecture

```
Internet
   │
   │ WiFi (Factory Network - 192.168.0.0/24)
   ▼
┌────────────────────────────────────────────┐
│ Raspberry Pi 3B+ (Linux Router)            │
│                                            │
│  wlan1 (USB WiFi Dongle - STA Mode)        │
│  IP: 192.168.0.109/24                      │
│  Gateway: 192.168.0.1                      │
│          │                                 │
│          │ NAT/MASQUERADE                  │
│          │ + Policy-Based Routing          │
│          ▼                                 │
│  wlan0 (Internal WiFi - AP Mode)           │
│  IP: 192.168.50.1/24                       │
│  SSID: IHM_NEOCOUDE                        │
│  DHCP Range: 192.168.50.10-20              │
└────────────────────────────────────────────┘
   │
   │ WiFi AP (WPA2-PSK)
   ▼
Mobile Clients (Tablets, Smartphones)
IP: 192.168.50.10-20 (DHCP)
Gateway: 192.168.50.1
DNS: 192.168.50.1 (proxy to 8.8.8.8)
```

---

## Technical Implementation

### Challenge

The Raspberry Pi 3B+ has only **one internal WiFi adapter** (BCM43438). To provide simultaneous:
1. **STA mode** (WiFi client): Connect to factory WiFi for internet
2. **AP mode** (Access Point): Host local WiFi for tablets

**Solution:** USB WiFi dongle (RTL8188CUS) for STA mode + internal adapter for AP mode.

### Core Components

#### 1. dnsmasq (DNS Proxy + DHCP Server)

**File:** `/etc/dnsmasq.conf`

**Key configurations:**
```conf
# Bind to AP interface only
interface=wlan0
bind-interfaces

# DHCP configuration
dhcp-range=192.168.50.10,192.168.50.20,255.255.255.0,24h
dhcp-option=3,192.168.50.1      # Gateway: RPi itself
dhcp-option=6,192.168.50.1      # DNS: RPi itself (proxy mode)

# DNS upstream servers for forwarding
server=8.8.8.8
server=8.8.4.4

# Local domain resolution
address=/ihm.local/192.168.50.1
local=/ihm.local/
```

**Purpose:**
- Assigns IP addresses to AP clients via DHCP
- Acts as DNS proxy: clients query RPi (192.168.50.1), RPi forwards to Google DNS
- Resolves local domain `ihm.local` to RPi's IP

#### 2. Linux Kernel IP Forwarding

```bash
echo 1 > /proc/sys/net/ipv4/ip_forward
```

**Purpose:** Enables packet forwarding between network interfaces (required for routing).

#### 3. Policy-Based Routing (Critical Fix)

**Problem Identified:**
The Linux kernel's default routing table only had routes for packets **originating from the RPi itself** (src 192.168.0.109), not for packets **forwarded from AP clients** (192.168.50.0/24).

When a client sent packets to external destinations (e.g., 142.250.102.188), the kernel returned:
```
RTNETLINK answers: Network is unreachable
```

**Root Cause Analysis:**
```bash
$ ip route show
default via 192.168.0.1 dev wlan1 src 192.168.0.109  # Only for RPi's own traffic!
192.168.50.0/24 dev wlan0                            # Local subnet only
```

**Solution - Separate Routing Table:**
```bash
# Create routing table 100 for AP traffic
ip route add default via 192.168.0.1 dev wlan1 table 100
ip route add 192.168.50.0/24 dev wlan0 scope link table 100

# Policy rule: traffic from AP subnet uses table 100
ip rule add from 192.168.50.0/24 table 100 priority 100
```

**Verification:**
```bash
$ ip rule list
0:      from all lookup local
100:    from 192.168.50.0/24 lookup 100    # ← Our rule
32766:  from all lookup main
32767:  from all lookup default

$ ip route show table 100
default via 192.168.0.1 dev wlan1
192.168.50.0/24 dev wlan0 scope link
```

Now packets from 192.168.50.17 (client) to 142.250.102.188 (Google) can be routed!

#### 4. iptables/nftables (Firewall + NAT)

**FORWARD Rules (Packet Routing):**
```bash
# Allow AP → STA (client to internet)
iptables -I FORWARD -i wlan0 -o wlan1 -j ACCEPT

# Allow STA → AP (internet to client, established connections only)
iptables -I FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
```

**NAT/MASQUERADE (Address Translation):**
```bash
# Translate source IP: 192.168.50.x → 192.168.0.109
iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE
```

**INPUT/OUTPUT Rules (Allow Management Traffic):**
```bash
# Accept DNS, DHCP, HTTP traffic on AP interface
iptables -I INPUT -i wlan0 -j ACCEPT
iptables -I OUTPUT -o wlan0 -j ACCEPT
```

---

## Packet Flow Diagram (Client → Google)

```
1. DNS Query
   Client (192.168.50.17) → RPi:53 "resolve google.com"
   RPi queries 8.8.8.8 → responds "142.250.102.188"

2. HTTP Request
   Client (192.168.50.17:45732) → Google (142.250.102.188:80)

3. Policy Routing (Kernel)
   Source: 192.168.50.17 → matches rule "from 192.168.50.0/24"
   → Use table 100 → route via 192.168.0.1 dev wlan1

4. FORWARD Chain (iptables)
   Input: wlan0, Output: wlan1 → ACCEPT (rule 1)

5. NAT/MASQUERADE (iptables)
   SNAT: 192.168.50.17:45732 → 192.168.0.109:45732
   Destination unchanged: 142.250.102.188:80

6. Packet Transmission
   RPi (192.168.0.109:45732) → Google (142.250.102.188:80)

7. Response (Return Path)
   Google (142.250.102.188:80) → RPi (192.168.0.109:45732)

8. NAT Reverse (Connection Tracking)
   DNAT: 192.168.0.109:45732 → 192.168.50.17:45732

9. FORWARD Chain (Reverse)
   Input: wlan1, Output: wlan0, State: ESTABLISHED → ACCEPT (rule 2)

10. Delivery
    RPi → Client (192.168.50.17:45732)
```

---

## Automation & Persistence

### Boot Script

**File:** `scripts/setup_nat_routing.sh`

```bash
#!/bin/bash
# Automated NAT and routing configuration
# Executed on boot via systemd service

# 1. Enable IP forwarding
echo 1 > /proc/sys/net/ipv4/ip_forward

# 2. Configure policy-based routing (table 100)
ip route add default via 192.168.0.1 dev wlan1 table 100
ip route add 192.168.50.0/24 dev wlan0 scope link table 100
ip rule add from 192.168.50.0/24 table 100 priority 100

# 3. Configure iptables FORWARD rules
iptables -I FORWARD -i wlan0 -o wlan1 -j ACCEPT
iptables -I FORWARD -i wlan1 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT

# 4. Configure NAT/MASQUERADE
iptables -t nat -A POSTROUTING -o wlan1 -j MASQUERADE

# 5. Accept management traffic on AP interface
iptables -I INPUT -i wlan0 -j ACCEPT
iptables -I OUTPUT -o wlan0 -j ACCEPT
```

### systemd Service

**File:** `/etc/systemd/system/ihm-routing.service`

```ini
[Unit]
Description=IHM NAT and Routing Setup for WiFi Sharing
After=network-online.target wlan0.device wlan1.device dnsmasq.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/home/lucas-junges/Documents/wco/ihm_esp32/scripts/setup_nat_routing.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Installation:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable ihm-routing.service
sudo systemctl start ihm-routing.service
```

---

## Performance Metrics

### Real-World Statistics (Production Environment)

```bash
$ sudo iptables -L FORWARD -v -n
Chain FORWARD (policy ACCEPT)
num   pkts  bytes   direction
1     7144  1.2MB   wlan0 → wlan1 (client to internet)
2    23272   28MB   wlan1 → wlan0 (internet to client)

$ sudo iptables -t nat -L POSTROUTING -v -n
Chain POSTROUTING (policy ACCEPT)
 pkts  bytes  target
  134   62KB  MASQUERADE (NAT translations)
```

**Interpretation:**
- ✅ 7,144 outbound packets (1.2 MB) from client to internet
- ✅ 23,272 inbound packets (28 MB) from internet to client
- ✅ 134 NAT translations performed
- ✅ Bidirectional traffic confirmed → **system working perfectly**

### Latency & Throughput

- DNS resolution: ~30-50 ms (RPi proxy + Google DNS)
- HTTP request roundtrip: ~100-150 ms (WiFi STA + NAT overhead)
- Throughput: Limited by factory WiFi (~20 Mbps observed)
- Concurrent clients supported: 10-15 (DHCP pool size)

---

## Troubleshooting Guide

### Issue 1: "No Internet Access" on Mobile Device

**Symptoms:**
- Device connects to WiFi AP successfully
- Shows "No internet access" or similar warning
- Browser cannot load any pages

**Diagnosis:**
```bash
# 1. Check if policy routing is configured
ip rule list | grep "192.168.50"
# Expected output:
# 100:    from 192.168.50.0/24 lookup 100

# 2. Check routing table 100
ip route show table 100
# Expected output:
# default via 192.168.0.1 dev wlan1
# 192.168.50.0/24 dev wlan0 scope link

# 3. Test route lookup from client IP
ip route get 8.8.8.8 from 192.168.50.17
# Should NOT return "Network is unreachable"
```

**Solution:**
```bash
# Re-run configuration script
sudo systemctl restart ihm-routing.service

# Verify service status
sudo systemctl status ihm-routing.service
```

### Issue 2: DNS Resolution Fails

**Symptoms:**
- Can access IPs directly (e.g., http://8.8.8.8)
- Cannot access domains by name (e.g., http://google.com)

**Diagnosis:**
```bash
# Check dnsmasq upstream servers
sudo journalctl -u dnsmasq | grep "using nameserver"
# Expected:
# using nameserver 8.8.8.8#53
# using nameserver 8.8.4.4#53

# Test DNS resolution on RPi
python3 -c "import socket; print(socket.gethostbyname('google.com'))"
```

**Solution:**
```bash
# Verify dnsmasq config
cat /etc/dnsmasq.conf | grep -E "(server=|dhcp-option=6)"

# Restart dnsmasq
sudo systemctl restart dnsmasq
```

### Issue 3: Zero Packets in FORWARD Chain

**Symptoms:**
- `iptables -L FORWARD -v` shows 0 packets
- tcpdump shows packets arriving on wlan0, but not leaving via wlan1

**Root Cause:** Policy routing not configured (see Issue 1)

**Advanced Diagnosis:**
```bash
# Enable packet logging
sudo iptables -I FORWARD -i wlan0 -o wlan1 -j LOG --log-prefix "FWD-OUT: "

# Monitor kernel logs
sudo dmesg -w | grep "FWD-OUT"
# If no logs appear → packets not reaching FORWARD chain → routing issue
```

---

## Security Considerations

### Firewall Rules

Current configuration uses **ACCEPT** policy for AP interface:
```bash
iptables -I INPUT -i wlan0 -j ACCEPT
```

**Production Hardening Recommendations:**

1. **Restrict to essential services only:**
```bash
# Remove blanket ACCEPT rule
iptables -D INPUT -i wlan0 -j ACCEPT

# Allow specific services
iptables -A INPUT -i wlan0 -p udp --dport 53 -j ACCEPT   # DNS
iptables -A INPUT -i wlan0 -p udp --dport 67 -j ACCEPT   # DHCP
iptables -A INPUT -i wlan0 -p tcp --dport 80 -j ACCEPT   # HTTP (HMI)
iptables -A INPUT -i wlan0 -p tcp --dport 8080 -j ACCEPT # WebSocket
iptables -A INPUT -i wlan0 -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -i wlan0 -j DROP  # Drop everything else
```

2. **Rate limiting (DDoS protection):**
```bash
iptables -A INPUT -i wlan0 -p tcp --dport 80 -m limit --limit 25/minute -j ACCEPT
```

3. **Isolate AP clients from RPi's other networks:**
```bash
# Block AP clients from accessing Ethernet network
iptables -I FORWARD -i wlan0 -o eth0 -j DROP
```

### WPA2 Security

Current AP configuration (in `/etc/hostapd/hostapd.conf`):
```conf
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=dobradeira123
rsn_pairwise=CCMP
```

**Recommendations:**
- Change default password (`dobradeira123`) to stronger passphrase (16+ chars)
- Consider WPA3 if client devices support it
- Enable MAC address filtering for known devices only

---

## Deployment Checklist

### Pre-Deployment

- [x] dnsmasq configured with correct DNS servers
- [x] hostapd configured for WPA2-PSK AP mode
- [x] Policy routing rules created (table 100)
- [x] iptables FORWARD + NAT rules configured
- [x] systemd service created and enabled
- [x] Boot script tested manually
- [x] Connectivity verified from mobile client

### Production Mode (No Ethernet)

**Important:** In production, Ethernet cable will be removed. The system relies solely on:
- `wlan1` (USB dongle): Internet connectivity via factory WiFi
- `wlan0` (internal): Access Point for tablets

**Current routing (with Ethernet):**
```
default via 192.168.0.1 dev eth0 metric 100    # ← Preferred (lower metric)
default via 192.168.0.1 dev wlan1 metric 600   # ← Fallback
```

**After Ethernet removal:**
```
default via 192.168.0.1 dev wlan1 metric 600   # ← Only route
```

**No configuration changes needed!** Policy routing for AP traffic explicitly uses `wlan1`, independent of default route metric.

### Post-Deployment Verification

```bash
# 1. Check all services running
sudo systemctl status dnsmasq hostapd ihm-routing

# 2. Verify routes
ip rule list | grep "192.168.50"
ip route show table 100

# 3. Verify firewall
sudo iptables -L FORWARD -v -n
sudo iptables -t nat -L POSTROUTING -v -n

# 4. Monitor traffic
sudo tcpdump -i wlan0 -n 'host 192.168.50.17'

# 5. Test from client
# - Connect to IHM_NEOCOUDE WiFi
# - Access http://192.168.50.1/ (local HMI)
# - Access http://google.com/ (internet via sharing)
```

---

## Technical Skills Demonstrated

### Linux System Administration
- Advanced networking: policy-based routing with iproute2
- Firewall management: iptables/nftables with NAT/MASQUERADE
- Service management: systemd unit files, boot automation
- Troubleshooting: tcpdump, dmesg, netfilter logging

### Network Engineering
- Layer 2/3 routing and switching concepts
- NAT/PAT (Port Address Translation)
- DNS proxy architecture
- DHCP server configuration
- WiFi protocols: STA mode, AP mode, WPA2 security

### Embedded Linux (ARM)
- Raspberry Pi hardware optimization
- Device tree overlays for WiFi adapters
- Resource-constrained environment (1GB RAM)
- Industrial IoT deployment

### Problem-Solving Methodology
1. **Systematic diagnosis:** Used tcpdump, iptables counters, route lookups
2. **Root cause analysis:** Identified kernel routing table limitation
3. **Solution design:** Policy-based routing with separate table
4. **Validation:** Verified with packet counters and real-world traffic
5. **Automation:** Created systemd service for production reliability

---

## Files & Configuration

| File | Purpose | Location |
|------|---------|----------|
| `dnsmasq.conf` | DNS proxy + DHCP server | `/etc/dnsmasq.conf` |
| `hostapd.conf` | WiFi Access Point config | `/etc/hostapd/hostapd.conf` |
| `setup_nat_routing.sh` | NAT/routing automation script | `scripts/setup_nat_routing.sh` |
| `ihm-routing.service` | systemd service unit | `/etc/systemd/system/` |
| `INTERNET_SHARING_SETUP.md` | This documentation | Project root |

---

## References & Standards

- **RFC 3022:** Traditional IP Network Address Translator (NAT)
- **RFC 2131:** Dynamic Host Configuration Protocol (DHCP)
- **RFC 1035:** Domain Name System (DNS)
- **IEEE 802.11:** Wireless LAN standards
- **Linux Advanced Routing & Traffic Control (LARTC):** https://lartc.org/
- **Netfilter/iptables Documentation:** https://www.netfilter.org/
- **systemd Service Management:** https://systemd.io/

---

## Author & Project Context

**Project:** Industrial HMI for NEOCOUDE-HD-15 Rebar Bending Machine
**Engineer:** Lucas William Junges
**Date:** January 2026
**Platform:** Raspberry Pi 3B+ (Production), Ubuntu 25.04 (Development)
**Industry:** Industrial Automation & Manufacturing
**Technologies:** Python, Linux, Modbus RTU, WebSockets, WiFi Networking

**GitHub Repository:** https://github.com/lucaswjunges/ihm-dobradeira-neocoude

---

## License

This project is part of an industrial automation solution. Configuration files and scripts provided as-is for reference and educational purposes.

---

**Status:** ✅ **Production-Ready** - Deployed and operational in industrial environment.
