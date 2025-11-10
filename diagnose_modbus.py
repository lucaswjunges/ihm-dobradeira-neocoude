#!/usr/bin/env python3
"""
Comprehensive Modbus diagnostic tool
Tests different slave IDs, function codes, and addresses
"""

from pymodbus.client import ModbusSerialClient
import time

def test_slave_addresses():
    """Test different slave addresses to find the correct one"""

    print("=" * 80)
    print("MODBUS DIAGNOSTIC TOOL")
    print("=" * 80)
    print()

    # Test configuration
    port = '/dev/ttyUSB1'
    baudrates = [57600]
    stopbits_options = [1, 2]
    parities = ['N', 'E']
    slave_ids = [1, 2, 3, 5, 10, 247]  # Common slave addresses + broadcast fallback

    # Test address that should work (encoder LSW)
    test_address = 1239  # 0x04D7

    for baudrate in baudrates:
        for stopbits in stopbits_options:
            for parity in parities:
                print(f"\n📡 Testing config: {baudrate} baud, {stopbits} stopbits, parity={parity}")
                print("-" * 80)

                try:
                    client = ModbusSerialClient(
                        port=port,
                        baudrate=baudrate,
                        parity=parity,
                        stopbits=stopbits,
                        bytesize=8,
                        timeout=1.0
                    )

                    if not client.connect():
                        print(f"  ❌ Failed to open port {port}")
                        continue

                    print(f"  ✓ Port {port} opened")

                    for slave_id in slave_ids:
                        # Test Function 0x03 (Read Holding Registers)
                        try:
                            response = client.read_holding_registers(
                                address=test_address,
                                count=1,
                                device_id=slave_id
                            )

                            if not response.isError():
                                value = response.registers[0]
                                print(f"  ✅ Slave ID {slave_id}: FC 0x03 @ {test_address} = {value} (0x{value:04X})")
                            else:
                                print(f"  ⚠️  Slave ID {slave_id}: FC 0x03 @ {test_address} - Error: {response}")
                        except Exception as e:
                            print(f"  ❌ Slave ID {slave_id}: FC 0x03 @ {test_address} - Exception: {e}")

                        time.sleep(0.1)

                        # Test Function 0x04 (Read Input Registers)
                        try:
                            response = client.read_input_registers(
                                address=test_address,
                                count=1,
                                device_id=slave_id
                            )

                            if not response.isError():
                                value = response.registers[0]
                                print(f"  ✅ Slave ID {slave_id}: FC 0x04 @ {test_address} = {value} (0x{value:04X})")
                            else:
                                print(f"  ⚠️  Slave ID {slave_id}: FC 0x04 @ {test_address} - Error: {response}")
                        except Exception as e:
                            print(f"  ❌ Slave ID {slave_id}: FC 0x04 @ {test_address} - Exception: {e}")

                        time.sleep(0.1)

                    client.close()

                except Exception as e:
                    print(f"  ❌ Configuration error: {e}")

    print()
    print("=" * 80)
    print("Diagnostic complete")
    print("=" * 80)

if __name__ == '__main__':
    test_slave_addresses()
