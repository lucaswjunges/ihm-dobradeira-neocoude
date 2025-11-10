"""
modbus_client.py

Modbus RTU client with stub mode support for web-first development.
Handles all communication with the Atos MPC4004 PLC.

Features:
- Stub mode: Simulates PLC responses without hardware
- Live mode: Real Modbus RTU communication via RS485
- Robust error handling: Never crashes on communication failures
- Button press simulation: Automatic 100ms hold time
"""

import time
import logging
from typing import Optional, Union
from dataclasses import dataclass

try:
    from pymodbus.client import ModbusSerialClient
    from pymodbus.exceptions import ModbusException
    PYMODBUS_AVAILABLE = True
except ImportError:
    PYMODBUS_AVAILABLE = False
    ModbusSerialClient = None
    ModbusException = Exception

import modbus_map as mm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ModbusConfig:
    """Modbus RTU configuration parameters"""
    port: str = '/dev/ttyUSB0'
    baudrate: int = 57600
    parity: str = 'N'  # None
    stopbits: int = 2  # CRITICAL: Atos MPC4004 requires 2 stop bits!
    bytesize: int = 8
    timeout: float = 1.0
    slave_address: int = 1  # Default, will be read from PLC register 0x1988


class ModbusClient:
    """
    Modbus RTU client for NEOCOUDE-HD-15 HMI.

    Supports both stub mode (for development) and live mode (real PLC).
    """

    def __init__(self, stub_mode: bool = True, config: Optional[ModbusConfig] = None):
        """
        Initialize Modbus client.

        Args:
            stub_mode: If True, simulate PLC without hardware
            config: Modbus configuration (uses defaults if None)
        """
        self.stub_mode = stub_mode
        self.config = config or ModbusConfig()
        self.client = None
        self.connected = False

        # Stub mode storage (simulates PLC memory)
        self._stub_coils = {}  # Coil states
        self._stub_registers = {}  # Register values

        if not stub_mode and not PYMODBUS_AVAILABLE:
            logger.error("pymodbus not installed! Install with: pip install pymodbus")
            logger.warning("Falling back to stub mode")
            self.stub_mode = True

        if stub_mode:
            logger.info("Modbus client initialized in STUB MODE")
            self._initialize_stub_data()
        else:
            logger.info(f"Modbus client initialized in LIVE MODE: {self.config.port} @ {self.config.baudrate}")

    def _initialize_stub_data(self):
        """Initialize stub mode with realistic default values"""
        # Encoder angle starts at 0
        self._stub_registers[mm.ENCODER['ANGLE_MSW']] = 0
        self._stub_registers[mm.ENCODER['ANGLE_LSW']] = 0

        # RPM at 5 (low speed)
        self._stub_registers[mm.ENCODER['RPM_MSW']] = 0
        self._stub_registers[mm.ENCODER['RPM_LSW']] = 5

        # Digital inputs/outputs all OFF
        for addr in mm.DIGITAL_INPUTS.values():
            self._stub_registers[addr] = 0
        for addr in mm.DIGITAL_OUTPUTS.values():
            self._stub_registers[addr] = 0

        # System state: Modbus enabled
        self._stub_coils[mm.SYSTEM_STATES['MODBUS_ENABLE']] = True

        # All buttons released
        for addr in mm.BUTTONS.values():
            self._stub_coils[addr] = False

        # Slave address
        self._stub_registers[mm.CONFIG_REGISTERS['SLAVE_ADDRESS']] = self.config.slave_address

        logger.info("Stub mode initialized with default values")

    def connect(self) -> bool:
        """
        Connect to PLC (or initialize stub mode).

        Returns:
            True if connected successfully, False otherwise
        """
        if self.stub_mode:
            self.connected = True
            logger.info("Stub mode: Connection simulated")
            return True

        try:
            self.client = ModbusSerialClient(
                port=self.config.port,
                baudrate=self.config.baudrate,
                parity=self.config.parity,
                stopbits=self.config.stopbits,
                bytesize=self.config.bytesize,
                timeout=self.config.timeout,
                # RTS control for RS485 (toggle with 1ms delay as per working Windows config)
                handle_local_echo=False
            )

            self.connected = self.client.connect()

            if self.connected:
                logger.info(f"Connected to PLC on {self.config.port}")
                # Try to read actual slave address from PLC
                slave_addr = self.read_register(mm.CONFIG_REGISTERS['SLAVE_ADDRESS'])
                if slave_addr is not None:
                    self.config.slave_address = slave_addr
                    logger.info(f"PLC slave address: {slave_addr}")
            else:
                logger.error(f"Failed to connect to PLC on {self.config.port}")

            return self.connected

        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from PLC"""
        if self.stub_mode:
            self.connected = False
            logger.info("Stub mode: Disconnection simulated")
            return

        if self.client and self.connected:
            try:
                self.client.close()
                logger.info("Disconnected from PLC")
            except Exception as e:
                logger.error(f"Disconnection error: {e}")
            finally:
                self.connected = False

    def read_coil(self, address: int) -> Optional[bool]:
        """
        Read single coil status (Function 0x01).

        Args:
            address: Coil address (decimal)

        Returns:
            Coil state (True/False) or None on error
        """
        if self.stub_mode:
            return self._stub_coils.get(address, False)

        if not self.connected:
            logger.warning("Cannot read coil: Not connected")
            return None

        try:
            response = self.client.read_coils(
                address,
                count=1,
                device_id=self.config.slave_address
            )

            if response.isError():
                logger.error(f"Error reading coil {address}: {response}")
                return None

            return response.bits[0]

        except ModbusException as e:
            logger.error(f"Modbus error reading coil {address}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading coil {address}: {e}")
            return None

    def read_register(self, address: int) -> Optional[int]:
        """
        Read single holding register (Function 0x03).

        Args:
            address: Register address (decimal)

        Returns:
            Register value (16-bit) or None on error
        """
        if self.stub_mode:
            return self._stub_registers.get(address, 0)

        if not self.connected:
            logger.warning("Cannot read register: Not connected")
            return None

        try:
            response = self.client.read_holding_registers(
                address,
                count=1,
                device_id=self.config.slave_address
            )

            if response.isError():
                logger.error(f"Error reading register {address}: {response}")
                return None

            return response.registers[0]

        except ModbusException as e:
            logger.error(f"Modbus error reading register {address}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading register {address}: {e}")
            return None

    def read_register_32bit(self, msw_address: int, lsw_address: int) -> Optional[int]:
        """
        Read 32-bit value from two consecutive registers.

        Args:
            msw_address: Most Significant Word address (even)
            lsw_address: Least Significant Word address (odd)

        Returns:
            32-bit integer or None on error
        """
        msw = self.read_register(msw_address)
        lsw = self.read_register(lsw_address)

        if msw is None or lsw is None:
            return None

        return mm.combine_32bit_registers(msw, lsw)

    def write_coil(self, address: int, value: bool) -> bool:
        """
        Write single coil (Function 0x05).

        Args:
            address: Coil address (decimal)
            value: True for ON, False for OFF

        Returns:
            True if successful, False otherwise
        """
        if self.stub_mode:
            self._stub_coils[address] = value
            logger.debug(f"Stub: Coil {address} set to {value}")
            return True

        if not self.connected:
            logger.warning("Cannot write coil: Not connected")
            return False

        try:
            response = self.client.write_coil(
                address,
                value,
                device_id=self.config.slave_address
            )

            if response.isError():
                logger.error(f"Error writing coil {address}: {response}")
                return False

            return True

        except ModbusException as e:
            logger.error(f"Modbus error writing coil {address}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing coil {address}: {e}")
            return False

    def write_register(self, address: int, value: int) -> bool:
        """
        Write single holding register (Function 0x06).

        Args:
            address: Register address (decimal)
            value: Value to write (16-bit, 0-65535)

        Returns:
            True if successful, False otherwise
        """
        if self.stub_mode:
            self._stub_registers[address] = value & 0xFFFF
            logger.debug(f"Stub: Register {address} set to {value}")
            return True

        if not self.connected:
            logger.warning("Cannot write register: Not connected")
            return False

        try:
            response = self.client.write_register(
                address,
                value,
                device_id=self.config.slave_address
            )

            if response.isError():
                logger.error(f"Error writing register {address}: {response}")
                return False

            return True

        except ModbusException as e:
            logger.error(f"Modbus error writing register {address}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing register {address}: {e}")
            return False

    def press_key(self, button_name: str, hold_time: float = 0.1) -> bool:
        """
        Simulate physical button press on HMI.

        Performs the sequence:
        1. Write coil to TRUE
        2. Wait hold_time (default 100ms)
        3. Write coil to FALSE

        Args:
            button_name: Button identifier from modbus_map.BUTTONS (e.g., 'K1', 'ENTER')
            hold_time: Time to hold button in seconds (default 0.1 = 100ms)

        Returns:
            True if successful, False otherwise
        """
        try:
            address = mm.get_button_address(button_name)
        except KeyError:
            logger.error(f"Unknown button: {button_name}")
            return False

        logger.info(f"Pressing button {button_name} (address {address})")

        # Press (write TRUE)
        if not self.write_coil(address, True):
            logger.error(f"Failed to press button {button_name}")
            return False

        # Hold
        time.sleep(hold_time)

        # Release (write FALSE)
        if not self.write_coil(address, False):
            logger.error(f"Failed to release button {button_name}")
            return False

        logger.info(f"Button {button_name} press completed")
        return True

    def write_register_32bit(self, msw_address: int, lsw_address: int, value: int) -> bool:
        """
        Write 32-bit value to two consecutive registers.

        Args:
            msw_address: Most Significant Word address (even)
            lsw_address: Least Significant Word address (odd)
            value: 32-bit integer to write

        Returns:
            True if successful, False otherwise
        """
        # Split 32-bit value into MSW (high 16 bits) and LSW (low 16 bits)
        msw = (value >> 16) & 0xFFFF
        lsw = value & 0xFFFF

        # Write MSW first
        if not self.write_register(msw_address, msw):
            logger.error(f"Failed to write MSW at {msw_address}")
            return False

        # Write LSW
        if not self.write_register(lsw_address, lsw):
            logger.error(f"Failed to write LSW at {lsw_address}")
            return False

        logger.info(f"32-bit value {value} written to registers {msw_address}/{lsw_address}")
        return True

    def get_encoder_angle(self) -> Optional[int]:
        """
        Read current encoder angle (32-bit value).

        Returns:
            Encoder angle or None on error
        """
        return self.read_register_32bit(
            mm.ENCODER['ANGLE_MSW'],
            mm.ENCODER['ANGLE_LSW']
        )

    def write_angle_1(self, angle: int) -> bool:
        """
        Write angle setpoint 1 (Tela 4).

        Args:
            angle: Angle in degrees (0-360)

        Returns:
            True if successful, False otherwise
        """
        if angle < 0 or angle > 360:
            logger.error(f"Angle {angle} out of range (0-360)")
            return False

        # Registers: 2114 (MSW) / 2112 (LSW)
        success = self.write_register_32bit(2114, 2112, angle)
        if success:
            logger.info(f"Angle 1 set to {angle}°")
        return success

    def write_angle_2(self, angle: int) -> bool:
        """
        Write angle setpoint 2 (Tela 5).

        Args:
            angle: Angle in degrees (0-360)

        Returns:
            True if successful, False otherwise
        """
        if angle < 0 or angle > 360:
            logger.error(f"Angle {angle} out of range (0-360)")
            return False

        # Registers: 2120 (MSW) / 2118 (LSW)
        success = self.write_register_32bit(2120, 2118, angle)
        if success:
            logger.info(f"Angle 2 set to {angle}°")
        return success

    def write_angle_3(self, angle: int) -> bool:
        """
        Write angle setpoint 3 (Tela 6).

        Args:
            angle: Angle in degrees (0-360)

        Returns:
            True if successful, False otherwise
        """
        if angle < 0 or angle > 360:
            logger.error(f"Angle {angle} out of range (0-360)")
            return False

        # Registers: 2130 (MSW) / 2128 (LSW)
        success = self.write_register_32bit(2130, 2128, angle)
        if success:
            logger.info(f"Angle 3 set to {angle}°")
        return success

    def read_angle_1(self) -> Optional[int]:
        """Read angle setpoint 1"""
        return self.read_register_32bit(2114, 2112)

    def read_angle_2(self) -> Optional[int]:
        """Read angle setpoint 2"""
        return self.read_register_32bit(2120, 2118)

    def read_angle_3(self) -> Optional[int]:
        """Read angle setpoint 3"""
        return self.read_register_32bit(2130, 2128)

    def read_discrete_input(self, address: int) -> Optional[bool]:
        """
        Read single discrete input status (Function 0x02).

        Args:
            address: Discrete input address (decimal)

        Returns:
            Input state (True/False) or None on error
        """
        if self.stub_mode:
            return self._stub_registers.get(address, 0) & 0x0001

        if not self.connected:
            logger.warning("Cannot read discrete input: Not connected")
            return None

        try:
            response = self.client.read_discrete_inputs(
                address=address,
                count=1,
                device_id=self.config.slave_address
            )

            if response.isError():
                logger.error(f"Error reading discrete input {address}: {response}")
                return None

            return response.bits[0]

        except Exception as e:
            logger.error(f"Unexpected error reading discrete input {address}: {e}")
            return None

    def get_digital_inputs(self) -> dict:
        """
        Read all digital inputs (E0-E7) using Read Discrete Inputs (0x02).

        Returns:
            Dictionary with input states {name: bool}
        """
        inputs = {}
        for name, addr in mm.DIGITAL_INPUTS.items():
            value = self.read_discrete_input(addr)
            inputs[name] = value if value is not None else None

        return inputs

    def get_digital_outputs(self) -> dict:
        """
        Read all digital outputs (S0-S7) using Read Coils (0x01).

        Returns:
            Dictionary with output states {name: bool}
        """
        outputs = {}
        for name, addr in mm.DIGITAL_OUTPUTS.items():
            value = self.read_coil(addr)  # Coils is correct for outputs
            outputs[name] = value if value is not None else None

        return outputs

    def simulate_encoder_movement(self, target_angle: int, duration: float = 2.0):
        """
        STUB MODE ONLY: Simulate gradual encoder movement to target angle.

        Args:
            target_angle: Target angle to reach
            duration: Time to reach target in seconds
        """
        if not self.stub_mode:
            logger.warning("simulate_encoder_movement only works in stub mode")
            return

        current = self.get_encoder_angle() or 0
        steps = 20
        step_size = (target_angle - current) // steps
        sleep_time = duration / steps

        logger.info(f"Simulating encoder movement: {current} -> {target_angle}")

        for i in range(steps):
            current += step_size
            # Split into MSW/LSW
            msw = (current >> 16) & 0xFFFF
            lsw = current & 0xFFFF
            self._stub_registers[mm.ENCODER['ANGLE_MSW']] = msw
            self._stub_registers[mm.ENCODER['ANGLE_LSW']] = lsw
            time.sleep(sleep_time)

        # Ensure final value is exact
        msw = (target_angle >> 16) & 0xFFFF
        lsw = target_angle & 0xFFFF
        self._stub_registers[mm.ENCODER['ANGLE_MSW']] = msw
        self._stub_registers[mm.ENCODER['ANGLE_LSW']] = lsw

        logger.info(f"Encoder simulation complete: {target_angle}")


if __name__ == '__main__':
    # Test stub mode
    print("=" * 80)
    print("MODBUS CLIENT TEST - STUB MODE")
    print("=" * 80)

    client = ModbusClient(stub_mode=True)

    # Connect
    if client.connect():
        print("\n✓ Connection successful")

        # Test encoder reading
        angle = client.get_encoder_angle()
        print(f"\nEncoder angle: {angle}")

        # Test digital inputs
        inputs = client.get_digital_inputs()
        print(f"\nDigital Inputs: {inputs}")

        # Test digital outputs
        outputs = client.get_digital_outputs()
        print(f"\nDigital Outputs: {outputs}")

        # Test button press
        print("\nTesting button press (K1)...")
        if client.press_key('K1'):
            print("✓ Button K1 pressed successfully")

        # Test encoder simulation
        print("\nSimulating encoder movement to 45°...")
        client.simulate_encoder_movement(45, duration=1.0)
        angle = client.get_encoder_angle()
        print(f"Encoder angle after simulation: {angle}")

        # Disconnect
        client.disconnect()
        print("\n✓ Disconnected")

    print("=" * 80)
