# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an industrial automation project to develop a modern web-based HMI (Human-Machine Interface) for a **Trillor NEOCOUDE-HD-15 rebar bending machine** (manufactured in 2007) controlled by an **Atos Expert Series PLC (MPC4004)**. The goal is to replace the damaged physical HMI (model 4004.95C) with a web-based solution accessible from a tablet.

### Machine Specifications (NEOCOUDE-HD-15)

**Mechanical**:
- **Capacity**: Up to 50mm (2") diameter CA-25 steel, 44mm (1 3/4") CA-50 steel
- **Motor**: 15 HP, 4-pole, 1755 rpm, 23A @ 380V
- **Plate speeds**:
  - Low: 5 rpm (Class 1)
  - Medium: 10 rpm (Class 2)
  - High: 15 rpm (Class 3)

**Control System**:
- **PLC**: Atos Expert MPC4004 (designation "CJ")
- **Encoder**: Model 2.018.200 - measures angular position
- **VFD**: WEG frequency inverter (model 2.022.000)
- **Sensor**: Model 2.018.152 - reference position detection
- **Limit switch**: Model 2.003.300

**Gear Ratios** (CRITICAL for encoder calculations):
- Motor to reducer: 1:30 (58.5 reduction)
- Pinion to gear: 18 teeth → 62 teeth = 3.44 ratio
- **Total reduction**: 1755 rpm motor → 5/10/15 rpm plate

**Encoder-to-Speed Relationship** (from inverter manual):
- 5 RPM: 2000 internal CLP units = 10V input
- 10 RPM: 1583 internal units = 7.91V
- 15 RPM: 1055 internal units = 5.27V
- **Conversion factor**: 0.005 (CLP/voltage)

## System Architecture

The system consists of three layers:

1. **PLC (Slave)**: Atos MPC4004 - the machine controller
2. **Server (Master)**: Ubuntu 25.04 notebook running Python 3 application (prototype for ESP32 final solution)
3. **Client**: Web browser on tablet (acts as WiFi hotspot)

**Communication Stack**:
- PLC ↔ Server: RS485 (Channel B) via USB-RS485-FTDI converter → appears as `/dev/ttyUSB0` or `/dev/ttyUSB1`
- Server ↔ Tablet: WiFi (tablet acts as hotspot, notebook connects as client)
- Protocol: Modbus RTU (PLC configured as slave, state `0BE` already enabled)

## Technology Stack

**Backend**: Python 3 with `asyncio`, `websockets`, and `pymodbus`
**Frontend**: Pure HTML5/CSS3/JavaScript (vanilla, no frameworks) with WebSockets for real-time communication

**Development Philosophy**: Web-first prototyping on Ubuntu that will be ported to ESP32/MicroPython with minimal changes.

## Critical Implementation Requirements

### Modbus RTU Configuration
- Baudrate: 57600
- Parity: None (configurable if needed)
- Stop bits: 1 (configurable: 1 or 2)
- Data bits: 8
- PLC Slave Address: Stored in register `1988H` (6536 dec) - **to be read from PLC**
- State `00BE` (hex) = 190 (dec): **MUST be forced ON to enable Modbus slave mode**

**Supported Modbus Function Codes** (MPC4004):
- `0x01`: Read Coil Status
- `0x02`: Read Input Status
- `0x03`: Read Holding Registers
- `0x05`: Force Single Coil (used for button simulation)
- `0x06`: Preset Single Register
- `0x0F`: Force Multiple Coils
- `0x10`: Preset Multiple Registers

**Register Structure for 32-bit Values** (CRITICAL!):
The Atos PLC uses paired registers for 32-bit values:
- **Even address** = Most Significant Word (MSW) - high 16 bits
- **Odd address** = Least Significant Word (LSW) - low 16 bits
- **Example**: Encoder counter at `04D6`/`04D7`:
  - Read `04D6` (1238 dec) → MSW (bits 31-16)
  - Read `04D7` (1239 dec) → LSW (bits 15-0)
  - Final value = (`register[04D6]` << 16) | `register[04D7]`
  - **Note**: Each register is 16-bit (0000-FFFF hex)

**Communication Configuration Registers**:
- `1987H` (6535 dec): RS485-B channel baudrate
- `1982H` (6530 dec): Print channel baudrate
- `1980H` (6528 dec): RS232 channel A baudrate
- `1988H` (6536 dec): **Slave address for RS485-B (Modbus)**
- `1941H` (6465 dec): Slave address for RS232

**Critical States for Modbus**:
- `00BE` (190 dec): **Enable Modbus slave mode** (MUST be ON)
- `03D0` (976 dec): Enable Modbus master mode (should be OFF for this project)
- `00BD` (189 dec): Print channel selector (OFF=RS232, ON=RS485)

**Diagnostic States** (for troubleshooting):
- `022` (34 dec): Modbus slave mode active on RS232 (not used in this project)
- `3D1`-`3EF`: Communication failure indicators with remote stations (master mode)

### Physical HMI Button Mapping (Critical!)
The web interface MUST replicate 100% of the physical keypad. Commands are sent via Modbus `Force Single Coil (0x05)`:

| Physical Key | Hex Address | Decimal Address | Notes |
|--------------|-------------|-----------------|-------|
| K1           | 00A0        | 160             | Numeric keypad |
| K2           | 00A1        | 161             | Numeric keypad |
| K3           | 00A2        | 162             | Numeric keypad |
| K4           | 00A3        | 163             | Numeric keypad |
| K5           | 00A4        | 164             | Numeric keypad |
| K6           | 00A5        | 165             | Numeric keypad |
| K7           | 00A6        | 166             | Numeric keypad |
| K8           | 00A7        | 167             | Numeric keypad |
| K9           | 00A8        | 168             | Numeric keypad |
| K0           | 00A9        | 169             | Numeric keypad |
| S1           | 00DC        | 220             | Function button 1 |
| S2           | 00DD        | 221             | Function button 2 |
| Arrow Up     | 00AC        | 172             | Navigation |
| Arrow Down   | 00AD        | 173             | Navigation |
| ESC          | 00BC        | 188             | Cancel/Exit |
| ENTER        | 0025        | 37              | Confirm |
| EDIT         | 0026        | 38              | Edit mode |
| Lock         | 00F1        | 241             | Keyboard lock |

**Key Press Simulation Protocol**:
Each button press requires a 3-step sequence:
1. **Force Coil ON**: Write coil address to TRUE (value=0xFF00)
2. **Hold Time**: Wait 100ms (minimum)
3. **Force Coil OFF**: Write coil address to FALSE (value=0x0000)

**Panel Physical Buttons** (additional to HMI keys, to be mapped):
| Button Name | Function | Notes |
|-------------|----------|-------|
| COMANDO GERAL | Master power ON | Main enable switch |
| AVANÇAR | Forward/CCW | Counterclockwise plate rotation |
| RECUAR | Backward/CW | Clockwise plate rotation |
| PARADA | Stop/Direction select | In auto mode: selects K4/K5 direction |
| EMERGÊNCIA | Emergency stop | Red mushroom button (código 2.0030319) |

**Important Notes**:
- Addresses are in **Modbus coil space** (not register space)
- Use Modbus Function Code `0x05` (Force Single Coil)
- PLC scans at ~6ms/K typical, ensure 100ms hold for reliable detection
- Never send rapid-fire commands - wait for previous cycle to complete
- **Physical buttons** (AVANÇAR, RECUAR, PARADA) must be mapped by analyzing ladder logic
- HMI keys (K0-K9, S1, S2, etc.) use addresses listed above

### Known Modbus Register Map

**Addressing Convention**: Addresses below are in hexadecimal. In code (`modbus_map.py`), convert to decimal:
- `04D6` (hex) = 1238 (dec)
- `04D7` (hex) = 1239 (dec)
- `0100` (hex) = 256 (dec)

**Read Registers** (Function 0x03 - Read Holding Registers):

**High-Speed Counter (CPU built-in, max 3 kHz)**:
- `04D6`/`04D7` (1238/1239 dec): **Encoder effective value** - 32-bit counter (MSW/LSW pair)
- `04D0`/`04D1` (1232/1233 dec): RPM value (angle mode) or reserved (normal mode)
- `04D2`/`04D3` (1234/1235 dec): Setpoint (normal mode) or reserved (angle mode)
- `04D8`/`04D9` (1240/1241 dec): Zero mark value for increasing direction (angle mode)
- `04DA`/`04DB` (1242/1243 dec): Zero mark value for decreasing direction (angle mode)

**Digital I/O Status** (16-bit registers, use bit 0 for status):
- `0100`-`0107` (256-263 dec): Digital inputs E0-E7 status
- `0180`-`0187` (384-391 dec): Digital outputs S0-S7 status

**Memory Map Overview**:
- `0000`-`03FF` (0-1023 dec): Internal states (1024 bits)
- `0400`-`047F` (1024-1151 dec): Timer/Counter presets and effectives
- `04D0`-`04DF` (1232-1247 dec): High-speed counter area (CPU)
- `0500`-`053F` (1280-1343 dec): Angle initial/final setpoints (16 angles)
- `0550`-`058F` (1360-1423 dec): Analog input presets
- `05D0`-`05DF` (1488-1503 dec): Analog input effectives (channels 9-16)
- `05F0`-`05FF` (1520-1535 dec): Analog input effectives (channels 1-8)
- `06C0`-`06CF` (1728-1743 dec): Temperature effectives (channels 9-16)
- `06D0`-`06DF` (1744-1759 dec): Analog output effectives (channels 9-16)
- `06E0`-`06EF` (1760-1775 dec): Analog output effectives (channels 1-8)
- `06F0`-`06FF` (1776-1791 dec): Temperature effectives (channels 1-8)

**Application-Specific Registers** (to be mapped from `clp.sup` ladder analysis):

**Angle Setpoints** (3 bends left + 3 bends right):
- `REG_ANGULO_ESQ_1/2/3`: Left bend angles (K1, K2, K3 keys)
- `REG_ANGULO_DIR_1/2/3`: Right bend angles (K1, K2, K3 keys)
- Variable "AJ" in HMI: User-editable angle values (e.g., 90°, 120°, 35°)
- Variable "PV" in HMI: Internal calculation, auto-corrects (not user-editable)

**Speed Class Selection**:
- Current speed class: 1 (5 rpm), 2 (10 rpm), or 3 (15 rpm)
- Changed only in manual mode via K1+K7 simultaneous press

**Operating Mode**:
- `BIT_MODO_MANUAL`: Manual mode active (only 5 rpm allowed)
- `BIT_MODO_AUTO`: Automatic mode active (all speeds available)
- Mode change: S1 key (only when system is stopped)

**Direction Control**:
- `BIT_SENTIDO_ANTIHORARIO`: Counterclockwise rotation (K4 LED on)
- `BIT_SENTIDO_HORARIO`: Clockwise rotation (K5 LED on)
- Selected via "PARADA" button in auto mode

**Bend Sequence**:
- `BIT_DOBRA_ATUAL`: Current bend number (1, 2, or 3)
- K1 LED: 1st bend active
- K2 LED: 2nd bend active
- K3 LED: 3rd bend active
- **Note**: System does not allow returning to previous bend

**Machine Status**:
- `BIT_EMERGENCIA`: Emergency stop active
- `BIT_CICLO_ATIVO`: Bending cycle in progress
- `BIT_POSICAO_ZERO`: Plate at reference position (sensor detected)
- `REG_ENCODER_ATUAL`: Current encoder position (from 04D6/04D7)

## Backend Module Structure

### `modbus_map.py`
Central configuration dictionary with all Modbus addresses (decimal). Contains both known addresses and placeholders for ladder-specific registers.

**Critical Initial Setup**:
1. **Read PLC slave address** from register `1988H` (6536 dec) on first connection
2. **Verify state `00BE`** (190 dec) is ON - Modbus slave mode must be enabled
3. **Test communication** with Read Holding Registers (0x03) for encoder value
4. Store slave address in configuration for all subsequent communications

### `modbus_client.py`
- Must support **stub mode** (`stub_mode=True`) for web-first development without PLC
- Live mode uses `pymodbus.client.ModbusSerialClient`
- All read/write operations MUST have exception handling (ModbusException, timeouts)
- NEVER crash on communication failures - return `None`/`False`
- Implements `press_key(address)` for button simulation
- **32-bit register reading**: Must implement helper function to read paired registers:
  - Read 2 consecutive registers (even + odd addresses)
  - Combine as: `(msb_register << 16) | lsb_register`
  - Use for encoder counter (`04D6`/`04D7`) and any other 32-bit values

### `state_manager.py`
- Asyncio polling loop (250ms cycle)
- Reads all vital machine data and stores in `machine_state` dictionary
- Single source of truth for all machine state

### `main_server.py`
- WebSocket server on `localhost:8080`
- On connect: sends complete `machine_state` to client
- Push updates: sends only deltas when values change
- On message: receives JSON commands from tablet (e.g., `{'action': 'press', 'key': 'K1'}`)
- Includes stub functions for future features: `send_telegram_alert()`, `log_to_sheets()`

## Frontend Structure (`index.html`)

Single-file application with embedded CSS/JS. Must be responsive and modern.

**Error Handling Requirements**:
- Red "DESLIGADO" (OFFLINE) overlay on WebSocket disconnect
- "FALHA CLP" overlay on Modbus errors from backend
- All buttons disabled during failures

**UI Tabs**:
1. **Operação**:
   - Encoder angle display (real-time from PLC)
   - Current speed class indicator (5/10/15 rpm)
   - Operating mode indicator (Manual/Automatic)
   - Direction indicator (Left/Right with K4/K5 LED status)
   - Current bend number (K1/K2/K3 LED status)
   - Angle setpoint inputs for 6 bends (3 left + 3 right)
   - Full virtual keyboard (K0-K9, S1/S2, arrows, ESC, EDIT, ENTER)
   - Emergency stop status indicator

2. **Diagnóstico**:
   - Digital twin showing E0-E7 inputs and S0-S7 outputs as virtual LEDs
   - Encoder value raw display
   - Sensor status (reference position)
   - VFD status and current frequency
   - Placeholder for future ESP32 sensors

3. **Logs e Produção**:
   - Runtime counter (active when `BIT_CICLO_ATIVO` is ON)
   - Bend counter (total bends completed)
   - Alert log (emergency stops, sensor failures)
   - Production statistics

4. **Configuração**:
   - Speed class selection (manual mode only)
   - WiFi settings (disabled until ESP32 migration)
   - Modbus connection parameters
   - System diagnostics

### Machine Operation Logic (to implement in frontend)

**Manual Mode**:
1. Operates only at 5 rpm (Class 1)
2. User presses AVANÇAR (forward) or RECUAR (backward) button
3. Button must be **held down** during entire bend
4. Plate rotates to pre-programmed angle shown in display
5. At end of rotation, plate auto-returns to zero position
6. User must press PARADA + direction button simultaneously for precise stop
7. If display doesn't show zero, press S2 to reset
8. Ready for next bend

**Automatic Mode**:
1. Switch from manual: Press S1 (only when system stopped)
2. Select direction: Press PARADA, then K4 (left) or K5 (right) LED illuminates
3. Verify angle on display
4. Press AVANÇAR (counterclockwise) or RECUAR (clockwise) to start
5. System auto-executes bend and returns to zero
6. Advances to next bend (K1→K2→K3) automatically
7. Cannot return to previous bend without full system restart

**Speed Class Change** (Manual mode only):
- Press K1 + K7 simultaneously
- Display shows current class
- Cycle through: 5 rpm → 10 rpm → 15 rpm → 5 rpm
- Selection persists until changed

**Important Operational Rules** (enforce in UI):
- ⚠️ Mode change (Manual↔Auto) only allowed when K1 LED active (1st bend)
- ⚠️ Speed class change only in Manual mode
- ⚠️ Sequential bend restriction: K1→K2→K3, no backwards
- ⚠️ To restart sequence: Power cycle required (disconnect/reconnect)
- ⚠️ Sensor alignment critical: Keep sensor nuts tight, avoid damage
- ⚠️ Encoder coupling: Keep screws tight to maintain automation accuracy

## Development Workflow

1. Develop in stub mode first (no PLC required)
2. Test web interface functionality
3. Switch to live mode with PLC connected
4. Analyze ladder program (`clp.sup`) to fill placeholder register addresses
5. Final port to ESP32/MicroPython should require minimal changes

## Reference Documentation

### PLC Documentation
- `M400423w2p_ATOS.pdf`: Atos PLC hardware manual (binary PDF, requires local reading)
- `manual_MPC4004.pdf`: Complete MPC4004 technical manual with:
  - Memory mapping (pages 53-104)
  - Modbus implementation details (page 133-134)
  - High-speed counter specifications (pages 93-97)
  - Communication parameters (page 85-86)
- `pdfcoffee.com_atos-expertpdf-pdf-free.pdf`: Atos Expert Series programming guide

### Machine Documentation
- `NEOCOUDE-HD 15 - Camargo 2007 (1).pdf`: Complete machine manual with:
  - Technical specifications (page 3)
  - Operation procedures (pages 7-8)
  - Bending capacity tables (page 9)
  - Tool mounting diagrams (pages 11-13)
  - Electrical schematics (pages 34-42)
  - Encoder manual (page 43)
  - VFD parameters (page 30)
  - Panel layout (page 33)

### Project Specification
- `prompt_ihm_dobradeira_atos.md`: Complete project specification with manual references

### Key Manual Sections for Implementation

**Encoder Configuration** (NEOCOUDE manual, page 30):
- 2000 CLP units @ 5 RPM = 10V
- 1583 CLP units @ 10 RPM = 7.91V
- 1055 CLP units @ 15 RPM = 5.27V
- Conversion factor: 0.005

**VFD Parameters** (WEG inverter):
- P133 = 4Hz, P134 = 47Hz
- P400 = 380V, P401 = 22.8A
- P402 = 1755rpm, P403 = 60Hz
- P408 = Auto-tune motor parameters

**Critical Maintenance Notes** (pages 23-1, 23-2):
- Keep sensor nuts tight (avoid losing PLC references)
- Keep encoder coupling screws tight
- Maintain front/rear doors for cleaning and lubrication access

## Key Design Principles

- **Modularity**: Clean separation between Modbus layer, state management, and web server
- **Robustness**: Never crash on communication failures - degrade gracefully
- **Web-First**: Develop and test web interface before hardware integration
- **ESP32-Ready**: Code structure must facilitate easy porting to MicroPython

## Troubleshooting Guide

### PLC Communication Issues

**Cannot connect to PLC**:
1. Verify RS485 wiring: A/B pairs not inverted
2. Check baudrate setting (should be 57600)
3. Read register `1987H` (6535 dec) to verify PLC baudrate configuration
4. Ensure state `00BE` (190 dec) is ON in ladder logic

**Modbus timeout errors**:
- PLC scan time is ~6ms/K (K = program size in KB)
- Set Modbus timeout to minimum 100ms
- For large programs, increase timeout proportionally

**Slave address unknown**:
1. Try reading register `1988H` (6536 dec) with broadcast address (0)
2. Check ladder program file `clp.sup` for slave ID configuration
3. Default might be 1 - try addresses 1-10

### Button Press Not Working

**Coil write succeeds but no response**:
- Verify 100ms hold time between ON and OFF
- Check if state `00F1` (241 dec - Lock) is active
- Ensure using Function Code `0x05` (not `0x0F`)

**Encoder value not updating**:
- Counter may be in "blocked" state
- Check state `00D2` (210 dec) - should be OFF to allow counting
- Verify encoder wiring to inputs E100/E101

### Data Reading Issues

**32-bit values incorrect**:
- Remember: Even address = MSW, Odd address = LSW
- Byte order: Big-endian within each 16-bit word
- Example: Value 123456 (0x0001E240) → Reg[even]=0x0001, Reg[odd]=0xE240

**Digital I/O status wrong**:
- Registers `0100`-`0107` and `0180`-`0187` are 16-bit
- Only bit 0 (LSB) contains the actual I/O status
- Mask with 0x0001 to read status

## Hardware Specifications (from Manual)

**MPC4004 CPU**:
- Scan time: 5-6ms/K (typical)
- Internal states: 1024 (0000h-03FFh)
- Registers: 1536 (0400h-0FFFh)
- Program memory: 32KB (NVRAM) or 64KB (RAM+FLASH for XA models)
- High-speed counter: 3 kHz (CPU built-in)

**RS485 Specifications**:
- Maximum distance: 1000m @ 9600 bps
- Maximum nodes: 32 devices
- Cable: Twisted pair, 24 AWG minimum
- Termination: 120Ω resistors at both ends of network

**Power Supply Requirements**:
- MPC4004 CPU: 300mA @ +5VDC
- Additional 100mA per 16 digital outputs (all ON)
- Analog modules: 30-40mA @ +5V, 40-210mA @ ±12V (per module)
