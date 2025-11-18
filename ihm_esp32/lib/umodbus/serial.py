"""
uModbus Serial - Simplified Modbus RTU for MicroPython ESP32
"""
from machine import UART, Pin
import struct
import time


def _calculate_crc16(data):
    """Calcula CRC16 Modbus"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)


class ModbusRTU:
    """Cliente Modbus RTU via UART"""

    def __init__(self, uart_id=2, baudrate=57600, data_bits=8, stop_bits=1, parity=None,
                 tx_pin=17, rx_pin=16, ctrl_pin=4):
        """
        uart_id: Número do UART (2 para GPIO16/17)
        baudrate: Taxa de comunicação (57600 para CLP Atos)
        tx_pin: GPIO TX (17 padrão)
        rx_pin: GPIO RX (16 padrão)
        ctrl_pin: GPIO DE/RE do MAX485 (4 padrão)
        """
        self.uart = UART(uart_id, baudrate=baudrate, bits=data_bits,
                        parity=parity, stop=stop_bits, tx=tx_pin, rx=rx_pin)
        self.ctrl = Pin(ctrl_pin, Pin.OUT)
        self.ctrl.value(0)  # Modo RX por padrão
        self.timeout = 1.0  # Timeout padrão 1s

    def _send_frame(self, frame):
        """Envia frame Modbus com CRC"""
        crc = _calculate_crc16(frame)
        self.ctrl.value(1)  # Modo TX
        time.sleep_ms(5)  # Estabilização
        self.uart.write(frame + crc)
        self.uart.flush()
        time.sleep_ms(10)  # Aguarda transmissão
        self.ctrl.value(0)  # Modo RX

    def _receive_frame(self):
        """Recebe frame Modbus com timeout"""
        response = bytearray()
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < int(self.timeout * 1000):
            if self.uart.any():
                response.extend(self.uart.read())
                time.sleep_ms(10)  # Aguarda mais dados
            else:
                if len(response) >= 5:  # Mínimo: slave + func + dados + crc
                    break
                time.sleep_ms(5)

        if len(response) < 5:
            return None

        # Valida CRC
        received_crc = response[-2:]
        calculated_crc = _calculate_crc16(response[:-2])
        if received_crc != calculated_crc:
            return None

        return response[:-2]  # Remove CRC

    def read_holding_registers(self, slave_addr, starting_addr, register_qty):
        """Function Code 0x03: Read Holding Registers"""
        frame = struct.pack('>BBHH', slave_addr, 0x03, starting_addr, register_qty)
        self._send_frame(frame)
        response = self._receive_frame()

        if not response or len(response) < 3:
            return None

        if response[1] == 0x03:  # Success
            byte_count = response[2]
            registers = []
            for i in range(3, 3 + byte_count, 2):
                registers.append(struct.unpack('>H', response[i:i+2])[0])
            return registers
        return None

    def read_coils(self, slave_addr, starting_addr, coil_qty):
        """Function Code 0x01: Read Coil Status"""
        frame = struct.pack('>BBHH', slave_addr, 0x01, starting_addr, coil_qty)
        self._send_frame(frame)
        response = self._receive_frame()

        if not response or len(response) < 3:
            return None

        if response[1] == 0x01:  # Success
            byte_count = response[2]
            coils = []
            for byte in response[3:3+byte_count]:
                for bit in range(8):
                    if len(coils) < coil_qty:
                        coils.append(bool(byte & (1 << bit)))
            return coils
        return None

    def write_single_coil(self, slave_addr, coil_addr, value):
        """Function Code 0x05: Force Single Coil"""
        coil_value = 0xFF00 if value else 0x0000
        frame = struct.pack('>BBHH', slave_addr, 0x05, coil_addr, coil_value)
        self._send_frame(frame)
        response = self._receive_frame()

        if not response or len(response) < 6:
            return False

        return response[1] == 0x05  # Success

    def write_single_register(self, slave_addr, register_addr, value):
        """Function Code 0x06: Preset Single Register"""
        frame = struct.pack('>BBHH', slave_addr, 0x06, register_addr, value & 0xFFFF)
        self._send_frame(frame)
        response = self._receive_frame()

        if not response or len(response) < 6:
            return False

        return response[1] == 0x06  # Success
