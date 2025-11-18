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
        uart_id: N�mero do UART (2 para GPIO16/17)
        baudrate: Taxa de comunica��o (57600 para CLP Atos)
        tx_pin: GPIO TX (17 padr�o)
        rx_pin: GPIO RX (16 padr�o)
        ctrl_pin: GPIO DE/RE do MAX485 (4 padr�o)
        """
        self.uart = UART(uart_id, baudrate=baudrate, bits=data_bits,
                        parity=parity, stop=stop_bits, tx=tx_pin, rx=rx_pin)
        self.ctrl = Pin(ctrl_pin, Pin.OUT)
        self.ctrl.value(0)  # Modo RX por padr�o
        self.timeout = 5.0  # Timeout aumentado para 5s (teste escrita)

    def _send_frame(self, frame):
        """Envia frame Modbus com CRC"""
        crc = _calculate_crc16(frame)
        self.ctrl.value(1)  # Modo TX
        time.sleep_ms(20)  # Estabiliza��o aumentada para escrita
        self.uart.write(frame + crc)
        self.uart.flush()
        time.sleep_ms(50)  # Aguarda transmiss�o (MUITO aumentado para escrita)
        self.ctrl.value(0)  # Modo RX
        time.sleep_ms(20)  # Aguarda estabiliza��o RX

    def _receive_frame(self):
        """Recebe frame Modbus com timeout"""
        response = bytearray()
        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < int(self.timeout * 1000):
            if self.uart.any():
                response.extend(self.uart.read())
                time.sleep_ms(20)  # Aguarda mais dados (aumentado)
            else:
                if len(response) >= 5:  # M�nimo: slave + func + dados + crc
                    break
                time.sleep_ms(10)  # Polling aumentado

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
        print(f"[MODBUS TX] Slave={slave_addr}, Func=0x01, Addr=0x{starting_addr:04X}, Qty={coil_qty}")
        self._send_frame(frame)
        response = self._receive_frame()

        if not response:
            print("[MODBUS RX] TIMEOUT - sem resposta")
            return None

        if len(response) < 3:
            print(f"[MODBUS RX] Resposta curta: {len(response)} bytes")
            return None

        if response[1] == 0x01:  # Success
            byte_count = response[2]
            coils = []
            for byte in response[3:3+byte_count]:
                for bit in range(8):
                    if len(coils) < coil_qty:
                        coils.append(bool(byte & (1 << bit)))
            print(f"[MODBUS RX] OK - {len(coils)} coils")
            return coils

        print(f"[MODBUS RX] Func incorreta: 0x{response[1]:02X}")
        return None

    def write_single_coil(self, slave_addr, coil_addr, value):
        """Function Code 0x05: Force Single Coil"""
        coil_value = 0xFF00 if value else 0x0000
        frame = struct.pack('>BBHH', slave_addr, 0x05, coil_addr, coil_value)
        print(f"[MODBUS TX] Slave={slave_addr}, Func=0x05, Addr=0x{coil_addr:04X}, Val={'ON' if value else 'OFF'}")
        self._send_frame(frame)
        response = self._receive_frame()

        if not response:
            print("[MODBUS RX] TIMEOUT - sem resposta")
            return False

        if len(response) < 6:
            hex_resp = ''.join([f'{b:02X}' for b in response])
            print(f"[MODBUS RX] Resposta curta: {len(response)} bytes - {hex_resp}")
            return False

        if response[1] == 0x05:
            print("[MODBUS RX] OK")
            return True

        print(f"[MODBUS RX] Func incorreta: 0x{response[1]:02X}")
        return False

    def write_single_register(self, slave_addr, register_addr, value):
        """Function Code 0x06: Preset Single Register"""
        frame = struct.pack('>BBHH', slave_addr, 0x06, register_addr, value & 0xFFFF)
        print(f"[MODBUS TX] Slave={slave_addr}, Func=0x06, Addr=0x{register_addr:04X}, Val={value}")
        self._send_frame(frame)
        response = self._receive_frame()

        if not response:
            print("[MODBUS RX] TIMEOUT - sem resposta")
            return False

        if len(response) < 6:
            hex_resp = ''.join([f'{b:02X}' for b in response])
            print(f"[MODBUS RX] Resposta curta: {len(response)} bytes - {hex_resp}")
            return False

        func_code = response[1]
        if func_code >= 0x80:
            error_code = response[2] if len(response) > 2 else 0
            print(f"[MODBUS RX] ERRO Modbus: Exception 0x{error_code:02X}")
            return False

        if func_code == 0x06:
            print(f"[MODBUS RX] OK")
            return True

        print(f"[MODBUS RX] Func incorreta: 0x{func_code:02X}")
        return False
