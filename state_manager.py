"""
state_manager.py

Asynchronous state management for NEOCOUDE-HD-15 HMI.
Polls PLC at 250ms intervals and maintains machine_state dictionary as single source of truth.

Features:
- Asyncio polling loop (250ms cycle time)
- Reads all vital machine data from PLC
- Detects changes and provides deltas for efficient updates
- Thread-safe state access
- Error recovery and connection monitoring
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, Callable
from copy import deepcopy

from modbus_client import ModbusClient, ModbusConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages machine state with asynchronous PLC polling.

    Single source of truth for all machine data.
    """

    def __init__(self, modbus_client: ModbusClient, poll_interval: float = 0.25):
        """
        Initialize state manager.

        Args:
            modbus_client: ModbusClient instance (stub or live)
            poll_interval: Polling interval in seconds (default 250ms)
        """
        self.client = modbus_client
        self.poll_interval = poll_interval

        # Machine state dictionary - single source of truth
        self.machine_state: Dict[str, Any] = {
            # Connection status
            'connected': False,
            'last_update': None,
            'poll_count': 0,
            'error_count': 0,

            # Encoder data
            'encoder_angle': 0,
            'encoder_rpm': 0,

            # Digital I/O
            'digital_inputs': {f'E{i}': False for i in range(8)},
            'digital_outputs': {f'S{i}': False for i in range(8)},

            # Operating mode (placeholders until ladder mapped)
            'mode_manual': None,
            'mode_auto': None,
            'current_bend': None,  # 1, 2, or 3
            'cycle_active': None,
            'emergency': None,

            # Setpoints (populated from ladder mappings)
            'angle_setpoints': {},
            'quantity_setpoints': {},
            'mode_bits': {},

            # Counters
            'piece_counter': None,

            # Speed class
            'speed_class': None,  # 1=5rpm, 2=10rpm, 3=15rpm

            # System diagnostics
            'plc_slave_address': None,
            'modbus_enabled': None,
        }

        # Previous state for change detection
        self._previous_state: Dict[str, Any] = {}

        # State change callbacks
        self._callbacks: list[Callable] = []

        # Control flags
        self._running = False
        self._task: Optional[asyncio.Task] = None

    def register_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Register callback to be called when state changes.

        Args:
            callback: Async function that receives state deltas
        """
        self._callbacks.append(callback)

    async def start(self):
        """Start the polling loop"""
        if self._running:
            logger.warning("State manager already running")
            return

        logger.info(f"Starting state manager (poll interval: {self.poll_interval}s)")

        # Connect to PLC
        if not self.client.connected:
            connected = await asyncio.to_thread(self.client.connect)
            if not connected:
                logger.error("Failed to connect to PLC")
                return

        self._running = True
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        """Stop the polling loop"""
        if not self._running:
            return

        logger.info("Stopping state manager")
        self._running = False

        if self._task:
            await self._task

        # Disconnect from PLC
        await asyncio.to_thread(self.client.disconnect)

    async def _poll_loop(self):
        """Main polling loop - runs continuously"""
        logger.info("Poll loop started")

        while self._running:
            try:
                start_time = time.time()

                # Read all data from PLC
                await self._update_state()

                # Calculate elapsed time and sleep remainder
                elapsed = time.time() - start_time
                sleep_time = max(0, self.poll_interval - elapsed)

                if elapsed > self.poll_interval:
                    logger.warning(f"Poll cycle took {elapsed:.3f}s (exceeds {self.poll_interval}s)")

                await asyncio.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in poll loop: {e}", exc_info=True)
                self.machine_state['error_count'] += 1
                await asyncio.sleep(self.poll_interval)

        logger.info("Poll loop stopped")

    async def _update_state(self):
        """Update machine state by reading from PLC"""
        try:
            # Read encoder angle (32-bit)
            angle = await asyncio.to_thread(self.client.get_encoder_angle)
            if angle is not None:
                self.machine_state['encoder_angle'] = angle

            # Read digital inputs
            inputs = await asyncio.to_thread(self.client.get_digital_inputs)
            if inputs:
                for name, value in inputs.items():
                    if value is not None:
                        self.machine_state['digital_inputs'][name] = value

            # Read digital outputs
            outputs = await asyncio.to_thread(self.client.get_digital_outputs)
            if outputs:
                for name, value in outputs.items():
                    if value is not None:
                        self.machine_state['digital_outputs'][name] = value

            # Read system diagnostics
            # Store the configured slave address (not reading from PLC)
            self.machine_state['plc_slave_address'] = self.client.config.slave_address

            # Read application-specific registers (mapped from ladder)
            import modbus_map as mm

            # Read angle setpoints
            for name, addr in mm.ANGLE_SETPOINTS.items():
                value = await asyncio.to_thread(self.client.read_register, addr)
                if value is not None:
                    if 'angle_setpoints' not in self.machine_state:
                        self.machine_state['angle_setpoints'] = {}
                    self.machine_state['angle_setpoints'][name.lower()] = value

            # Read mode/cycle bits
            for name, addr in mm.MODE_BITS.items():
                value = await asyncio.to_thread(self.client.read_coil, addr)
                if value is not None:
                    if 'mode_bits' not in self.machine_state:
                        self.machine_state['mode_bits'] = {}
                    self.machine_state['mode_bits'][name.lower()] = value

            # Read quantity setpoints
            for name, addr in mm.QUANTITY_SETPOINTS.items():
                value = await asyncio.to_thread(self.client.read_register, addr)
                if value is not None:
                    if 'quantity_setpoints' not in self.machine_state:
                        self.machine_state['quantity_setpoints'] = {}
                    self.machine_state['quantity_setpoints'][name.lower()] = value

            # Update metadata
            self.machine_state['connected'] = self.client.connected
            self.machine_state['last_update'] = time.time()
            self.machine_state['poll_count'] += 1

            # Detect changes and notify callbacks
            deltas = self._get_state_deltas()
            if deltas:
                await self._notify_callbacks(deltas)

            # Update previous state
            self._previous_state = deepcopy(self.machine_state)

        except Exception as e:
            logger.error(f"Error updating state: {e}", exc_info=True)
            self.machine_state['error_count'] += 1
            self.machine_state['connected'] = False

    def _get_state_deltas(self) -> Dict[str, Any]:
        """
        Compare current state with previous state and return only changes.

        Returns:
            Dictionary containing only changed values
        """
        if not self._previous_state:
            # First poll - return entire state
            return deepcopy(self.machine_state)

        deltas = {}

        for key, value in self.machine_state.items():
            prev_value = self._previous_state.get(key)

            if isinstance(value, dict):
                # Handle nested dictionaries (digital_inputs, digital_outputs, etc.)
                changed_items = {}
                for sub_key, sub_value in value.items():
                    prev_sub_value = prev_value.get(sub_key) if prev_value else None
                    if sub_value != prev_sub_value:
                        changed_items[sub_key] = sub_value

                if changed_items:
                    deltas[key] = changed_items

            elif value != prev_value:
                deltas[key] = value

        return deltas

    async def _notify_callbacks(self, deltas: Dict[str, Any]):
        """
        Notify all registered callbacks of state changes.

        Args:
            deltas: Dictionary containing changed values
        """
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(deltas)
                else:
                    callback(deltas)
            except Exception as e:
                logger.error(f"Error in callback: {e}", exc_info=True)

    def get_state(self) -> Dict[str, Any]:
        """
        Get complete current machine state.

        Returns:
            Deep copy of machine_state dictionary
        """
        return deepcopy(self.machine_state)

    async def press_button(self, button_name: str) -> bool:
        """
        Press a button on the virtual HMI.

        Args:
            button_name: Button identifier (e.g., 'K1', 'ENTER')

        Returns:
            True if successful, False otherwise
        """
        try:
            result = await asyncio.to_thread(self.client.press_key, button_name)
            return result
        except Exception as e:
            logger.error(f"Error pressing button {button_name}: {e}")
            return False


async def main():
    """Test state manager with stub mode"""
    print("=" * 80)
    print("STATE MANAGER TEST - STUB MODE")
    print("=" * 80)

    # Create stub mode client
    client = ModbusClient(stub_mode=True)

    # Create state manager
    manager = StateManager(client, poll_interval=0.5)

    # Register a callback to print state changes
    async def on_state_change(deltas):
        print(f"\n[STATE CHANGE] {deltas}")

    manager.register_callback(on_state_change)

    # Start polling
    await manager.start()

    print("\n✓ State manager started")
    print("Polling every 500ms...\n")

    # Let it poll a few times
    await asyncio.sleep(2)

    # Simulate button press
    print("\nSimulating button press (K1)...")
    success = await manager.press_button('K1')
    print(f"Button press result: {success}")

    await asyncio.sleep(1)

    # Simulate encoder movement (stub mode only)
    print("\nSimulating encoder movement to 90°...")
    await asyncio.to_thread(client.simulate_encoder_movement, 90, 2.0)

    await asyncio.sleep(3)

    # Get current state
    state = manager.get_state()
    print(f"\nCurrent encoder angle: {state['encoder_angle']}°")
    print(f"Total polls: {state['poll_count']}")
    print(f"Errors: {state['error_count']}")

    # Stop
    await manager.stop()
    print("\n✓ State manager stopped")

    print("=" * 80)


if __name__ == '__main__':
    asyncio.run(main())
