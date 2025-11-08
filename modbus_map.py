"""
modbus_map.py

Central configuration dictionary with all Modbus addresses (decimal format).
Based on Atos MPC4004 PLC documentation and NEOCOUDE-HD-15 machine specifications.

Address format:
- Coils: Function 0x05 (Force Single Coil)
- Registers: Function 0x03 (Read Holding Registers)
- 32-bit values: MSW (even address) + LSW (odd address)
"""

# ============================================================================
# PHYSICAL HMI BUTTON MAPPING (Coils for Force Single Coil 0x05)
# ============================================================================
BUTTONS = {
    # Numeric keypad (K1-K9, K0)
    'K1': 160,      # 0x00A0
    'K2': 161,      # 0x00A1
    'K3': 162,      # 0x00A2
    'K4': 163,      # 0x00A3
    'K5': 164,      # 0x00A4
    'K6': 165,      # 0x00A5
    'K7': 166,      # 0x00A6
    'K8': 167,      # 0x00A7
    'K9': 168,      # 0x00A8
    'K0': 169,      # 0x00A9

    # Function buttons
    'S1': 220,      # 0x00DC
    'S2': 221,      # 0x00DD

    # Navigation arrows
    'ARROW_UP': 172,    # 0x00AC
    'ARROW_DOWN': 173,  # 0x00AD

    # Control keys
    'ESC': 188,     # 0x00BC
    'LOCK': 241,    # 0x00F1
    'EDIT': 38,     # 0x0026
    'ENTER': 37,    # 0x0025
}

# Panel physical buttons (to be mapped from ladder logic analysis)
PANEL_BUTTONS = {
    'COMANDO_GERAL': None,  # Master power ON
    'AVANCAR': None,        # Forward/CCW - Counterclockwise plate rotation
    'RECUAR': None,         # Backward/CW - Clockwise plate rotation
    'PARADA': None,         # Stop/Direction select
    'EMERGENCIA': None,     # Emergency stop
}

# ============================================================================
# HIGH-SPEED COUNTER (CPU built-in, max 3 kHz)
# ============================================================================
ENCODER = {
    'ANGLE_MSW': 1238,  # 0x04D6 - Most Significant Word (even address)
    'ANGLE_LSW': 1239,  # 0x04D7 - Least Significant Word (odd address)
    'RPM_MSW': 1232,    # 0x04D0 - RPM value (angle mode)
    'RPM_LSW': 1233,    # 0x04D1
    'SETPOINT_MSW': 1234,  # 0x04D2 - Setpoint (normal mode)
    'SETPOINT_LSW': 1235,  # 0x04D3
}

# ============================================================================
# DIGITAL INPUTS/OUTPUTS
# ============================================================================
DIGITAL_INPUTS = {
    'E0': 256,  # 0x0100
    'E1': 257,  # 0x0101
    'E2': 258,  # 0x0102
    'E3': 259,  # 0x0103
    'E4': 260,  # 0x0104
    'E5': 261,  # 0x0105
    'E6': 262,  # 0x0106
    'E7': 263,  # 0x0107
}

DIGITAL_OUTPUTS = {
    'S0': 384,  # 0x0180
    'S1': 385,  # 0x0181
    'S2': 386,  # 0x0182
    'S3': 387,  # 0x0183
    'S4': 388,  # 0x0184
    'S5': 389,  # 0x0185
    'S6': 390,  # 0x0186
    'S7': 391,  # 0x0187
}

# ============================================================================
# SYSTEM STATES (Internal PLC bits)
# ============================================================================
SYSTEM_STATES = {
    'MODBUS_ENABLE': 190,  # 0x00BE - MUST be ON for Modbus slave mode
}

# ============================================================================
# PLC CONFIGURATION REGISTERS
# ============================================================================
CONFIG_REGISTERS = {
    'SLAVE_ADDRESS': 6536,  # 0x1988 - PLC slave address storage
    'BAUDRATE': 6535,       # 0x1987 - Communication baudrate setting
}

# ============================================================================
# APPLICATION-SPECIFIC REGISTERS (Placeholders - to be mapped from ladder logic)
# ============================================================================
# These addresses will be determined by analyzing the clp.sup ladder program

# Angle setpoints for 3 bends (mapped from ladder ROT4)
ANGLE_SETPOINTS = {
    'BEND_1_A': 2112,   # 0x0840 - K1 bend angle A
    'BEND_1_B': 2114,   # 0x0842 - K1 bend angle B
    'BEND_2_A': 2118,   # 0x0846 - K2 bend angle A
    'BEND_2_B': 2120,   # 0x0848 - K2 bend angle B
    'BEND_3_A': 2128,   # 0x0850 - K3 bend angle A
    'BEND_3_B': 2130,   # 0x0852 - K3 bend angle B
}

# Quantity setpoints for production (mapped from ladder ROT4)
QUANTITY_SETPOINTS = {
    'QTY_1': 2400,  # 0x0960 - REG_SETPOINT_QUANTIDADE_1
    'QTY_2': 2402,  # 0x0962 - REG_SETPOINT_QUANTIDADE_2
    'QTY_3': 2404,  # 0x0964 - REG_SETPOINT_QUANTIDADE_3
    'QTY_4': 2406,  # 0x0966 - REG_SETPOINT_QUANTIDADE_4
}

# Production counters
COUNTERS = {
    'CURRENT_PIECES': None,  # REG_CONTADOR_PECAS_ATUAL - Current piece count
}

# Operating mode and status bits (mapped from ladder analysis)
MODE_BITS = {
    # Machine cycle states (from Principal.lad)
    'CYCLE_STATE_0': 768,    # 0x0300 - Cycle state 0
    'CYCLE_STATE_1': 769,    # 0x0301 - Cycle state 1
    'CYCLE_STATE_2': 770,    # 0x0302 - Cycle state 2
    'CYCLE_STATE_3': 771,    # 0x0303 - Cycle state 3
    'CYCLE_STATE_4': 772,    # 0x0304 - Cycle state 4
    'CYCLE_STATE_5': 773,    # 0x0305 - Cycle state 5
    'CYCLE_STATE_8': 776,    # 0x0308 - Cycle state 8

    # Bend active bits (from ROT4.lad)
    'BEND_1_ACTIVE': 896,    # 0x0380 - Bend 1 (K1) active
    'BEND_2_ACTIVE': 897,    # 0x0381 - Bend 2 (K2) active
    'BEND_3_ACTIVE': 898,    # 0x0382 - Bend 3 (K3) active
    'BEND_COMPLETE': 899,    # 0x0383 - Bend sequence complete
    'ROT4_OUTPUT': 901,      # 0x0385 - ROT4 subroutine output
}

# Speed class settings (5/10/15 RPM)
SPEED_CLASS = {
    'CLASS_1': None,  # 5 RPM - Manual mode only
    'CLASS_2': None,  # 10 RPM - Auto mode
    'CLASS_3': None,  # 15 RPM - Auto mode
}

# ============================================================================
# ANALOG INPUTS/OUTPUTS (if needed)
# ============================================================================
ANALOG_INPUTS = {
    'CH1': 1520,  # 0x05F0
    'CH2': 1521,  # 0x05F1
    'CH3': 1522,  # 0x05F2
    'CH4': 1523,  # 0x05F3
    'CH5': 1524,  # 0x05F4
    'CH6': 1525,  # 0x05F5
    'CH7': 1526,  # 0x05F6
    'CH8': 1527,  # 0x05F7
}

ANALOG_OUTPUTS = {
    'CH1': 1760,  # 0x06E0
    'CH2': 1761,  # 0x06E1
    'CH3': 1762,  # 0x06E2
    'CH4': 1763,  # 0x06E3
    'CH5': 1764,  # 0x06E4
    'CH6': 1765,  # 0x06E5
    'CH7': 1766,  # 0x06E6
    'CH8': 1767,  # 0x06E7
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_button_address(button_name: str) -> int:
    """
    Get Modbus coil address for a button by name.

    Args:
        button_name: Button identifier (e.g., 'K1', 'ENTER', 'ESC')

    Returns:
        Decimal Modbus address

    Raises:
        KeyError: If button name not found
    """
    return BUTTONS[button_name.upper()]


def combine_32bit_registers(msw: int, lsw: int) -> int:
    """
    Combine MSW and LSW into 32-bit value.

    Args:
        msw: Most Significant Word (from even address)
        lsw: Least Significant Word (from odd address)

    Returns:
        32-bit integer value
    """
    return (msw << 16) | lsw


def get_all_mapped_addresses() -> dict:
    """
    Get all currently mapped (non-None) addresses for diagnostics.

    Returns:
        Dictionary with all mapped addresses grouped by category
    """
    mapped = {
        'buttons': BUTTONS,
        'digital_inputs': DIGITAL_INPUTS,
        'digital_outputs': DIGITAL_OUTPUTS,
        'encoder': ENCODER,
        'system_states': SYSTEM_STATES,
        'config_registers': CONFIG_REGISTERS,
    }

    # Filter out None values from placeholder dictionaries
    for key in ['angle_setpoints', 'quantity_setpoints', 'counters', 'mode_bits', 'speed_class']:
        source = globals()[key.upper()]
        filtered = {k: v for k, v in source.items() if v is not None}
        if filtered:
            mapped[key] = filtered

    return mapped


if __name__ == '__main__':
    # Display all mapped addresses for verification
    print("=" * 80)
    print("MODBUS ADDRESS MAP - NEOCOUDE-HD-15 HMI")
    print("=" * 80)

    all_mapped = get_all_mapped_addresses()

    for category, addresses in all_mapped.items():
        print(f"\n{category.upper().replace('_', ' ')}:")
        for name, addr in addresses.items():
            hex_addr = f"0x{addr:04X}" if addr is not None else "N/A"
            print(f"  {name:20s}: {addr:6d} ({hex_addr})")

    print("\n" + "=" * 80)
    print(f"Total mapped addresses: {sum(len(v) for v in all_mapped.values())}")
    print("=" * 80)
