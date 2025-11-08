"""
main_server.py

WebSocket server for NEOCOUDE-HD-15 HMI.
Bridges PLC state (via state_manager) with web frontend (via WebSocket).

Features:
- WebSocket server on localhost:8080
- Sends complete state on client connect
- Pushes only deltas on state changes
- Receives JSON commands from frontend (button presses, etc.)
- Stub functions for future features (Telegram, Google Sheets)
"""

import asyncio
import json
import logging
import argparse
from typing import Set
from datetime import datetime

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = None

from modbus_client import ModbusClient, ModbusConfig
from state_manager import StateManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HMIServer:
    """
    WebSocket server for HMI frontend communication.
    """

    def __init__(self, state_manager: StateManager, host: str = 'localhost', port: int = 8080):
        """
        Initialize HMI server.

        Args:
            state_manager: StateManager instance
            host: WebSocket server host (default: localhost)
            port: WebSocket server port (default: 8080)
        """
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError("websockets not installed! Install with: pip install websockets")

        self.state_manager = state_manager
        self.host = host
        self.port = port

        # Connected WebSocket clients
        self.clients: Set[WebSocketServerProtocol] = set()

        # Alert log (for "Logs e Produção" tab)
        self.alert_log = []

    async def start(self):
        """Start WebSocket server and state manager"""
        logger.info(f"Starting HMI server on ws://{self.host}:{self.port}")

        # Register state change callback
        self.state_manager.register_callback(self._on_state_change)

        # Start state manager
        await self.state_manager.start()

        # Start WebSocket server
        async with websockets.serve(self._handle_client, self.host, self.port):
            logger.info(f"✓ HMI server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

    async def _handle_client(self, websocket: WebSocketServerProtocol):
        """
        Handle new WebSocket client connection.

        Args:
            websocket: WebSocket connection
        """
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        logger.info(f"Client connected: {client_id}")

        # Add to clients set
        self.clients.add(websocket)

        try:
            # Send complete state on connect
            initial_state = self.state_manager.get_state()
            await self._send_message(websocket, {
                'type': 'initial_state',
                'data': initial_state
            })

            # Send alert log
            await self._send_message(websocket, {
                'type': 'alert_log',
                'data': self.alert_log
            })

            # Listen for commands from client
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")

        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}", exc_info=True)

        finally:
            # Remove from clients set
            self.clients.discard(websocket)

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """
        Handle incoming message from client.

        Expected message format (JSON):
        {
            "action": "press_button",
            "button": "K1"
        }

        Args:
            websocket: WebSocket connection
            message: JSON message string
        """
        try:
            data = json.loads(message)
            action = data.get('action')

            logger.info(f"Received command: {data}")

            if action == 'press_button':
                button = data.get('button')
                if not button:
                    await self._send_error(websocket, "Missing button parameter")
                    return

                # Press button via state manager
                success = await self.state_manager.press_button(button)

                # Send response
                await self._send_message(websocket, {
                    'type': 'button_response',
                    'success': success,
                    'button': button
                })

                # Log to alert log
                if success:
                    self._add_alert(f"Botão {button} pressionado", 'info')

            elif action == 'ping':
                # Health check
                await self._send_message(websocket, {
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })

            else:
                await self._send_error(websocket, f"Unknown action: {action}")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON received: {message}")
            await self._send_error(websocket, "Invalid JSON format")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await self._send_error(websocket, str(e))

    async def _on_state_change(self, deltas: dict):
        """
        Callback for state changes - broadcast deltas to all clients.

        Args:
            deltas: Dictionary with changed state values
        """
        if not self.clients:
            return

        message = {
            'type': 'state_update',
            'data': deltas
        }

        # Broadcast to all connected clients
        await asyncio.gather(
            *[self._send_message(client, message) for client in self.clients],
            return_exceptions=True
        )

    async def _send_message(self, websocket: WebSocketServerProtocol, message: dict):
        """
        Send JSON message to client.

        Args:
            websocket: WebSocket connection
            message: Dictionary to send as JSON
        """
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def _send_error(self, websocket: WebSocketServerProtocol, error: str):
        """
        Send error message to client.

        Args:
            websocket: WebSocket connection
            error: Error message
        """
        await self._send_message(websocket, {
            'type': 'error',
            'message': error
        })

    def _add_alert(self, message: str, level: str = 'info'):
        """
        Add alert to log.

        Args:
            message: Alert message
            level: Alert level (info, warning, error)
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }

        self.alert_log.append(alert)

        # Keep only last 100 alerts
        if len(self.alert_log) > 100:
            self.alert_log.pop(0)

        # Broadcast alert to all clients
        asyncio.create_task(self._broadcast_alert(alert))

    async def _broadcast_alert(self, alert: dict):
        """
        Broadcast alert to all connected clients.

        Args:
            alert: Alert dictionary
        """
        if not self.clients:
            return

        message = {
            'type': 'alert',
            'data': alert
        }

        await asyncio.gather(
            *[self._send_message(client, message) for client in self.clients],
            return_exceptions=True
        )


# ============================================================================
# FUTURE FEATURES (Stubs)
# ============================================================================

async def send_telegram_alert(message: str):
    """
    Send alert via Telegram bot.

    TODO: Implement when Telegram integration is needed.

    Args:
        message: Alert message to send
    """
    logger.info(f"[STUB] Telegram alert: {message}")
    # Future: Use python-telegram-bot library
    pass


async def log_to_sheets(data: dict):
    """
    Log production data to Google Sheets.

    TODO: Implement when Google Sheets integration is needed.

    Args:
        data: Production data dictionary
    """
    logger.info(f"[STUB] Google Sheets log: {data}")
    # Future: Use gspread library
    pass


# ============================================================================
# MAIN
# ============================================================================

async def main(stub_mode: bool = True, serial_port: str = '/dev/ttyUSB0'):
    """
    Main entry point for HMI server.

    Args:
        stub_mode: Use stub mode (no PLC hardware)
        serial_port: Serial port for RS485 converter
    """
    logger.info("=" * 80)
    logger.info("NEOCOUDE-HD-15 HMI SERVER")
    logger.info("=" * 80)

    # Create Modbus client
    if stub_mode:
        logger.info("Running in STUB MODE (no PLC hardware required)")
        client = ModbusClient(stub_mode=True)
    else:
        logger.info(f"Running in LIVE MODE (PLC on {serial_port})")
        config = ModbusConfig(port=serial_port)
        client = ModbusClient(stub_mode=False, config=config)

    # Create state manager
    state_manager = StateManager(client, poll_interval=0.25)

    # Create and start HMI server
    server = HMIServer(state_manager, host='localhost', port=8080)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested...")
    finally:
        await state_manager.stop()
        logger.info("Server stopped")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='NEOCOUDE-HD-15 HMI Server')
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in live mode (connect to real PLC)'
    )
    parser.add_argument(
        '--port',
        type=str,
        default='/dev/ttyUSB0',
        help='Serial port for RS485 converter (default: /dev/ttyUSB0)'
    )

    args = parser.parse_args()

    try:
        asyncio.run(main(stub_mode=not args.live, serial_port=args.port))
    except KeyboardInterrupt:
        logger.info("\nShutdown complete")
