"""
Modbus Client ESP32 - IHM Web Dobradeira
Versão MicroPython adaptada de modbus_client.py
"""
import time
from lib.umodbus.serial import ModbusRTU
import modbus_map as mm


class ModbusClientWrapper:
    """Wrapper Modbus RTU para ESP32"""

    def __init__(self, stub_mode=False, slave_id=1):
        self.stub_mode = stub_mode
        self.slave_id = slave_id
        self.client = None
        self.connected = False

        # Estado stub
        self.stub_registers = {}
        self.stub_coils = {}

        if not stub_mode:
            self._connect_live()
        else:
            self._init_stub()

    def _connect_live(self):
        """Conecta via UART2 (GPIO17/16)"""
        try:
            print("Conectando Modbus UART2...")
            self.client = ModbusRTU(uart_id=2, baudrate=57600, data_bits=8, stop_bits=2, parity=None, tx_pin=17, rx_pin=16, ctrl_pin=4)
            self.connected = True
            print(" Modbus conectado")
        except Exception as e:
            print(f" Erro Modbus: {e}")
            self.connected = False

    def _init_stub(self):
        """Inicializa dados simulados"""
        self.connected = True
        self.stub_registers[mm.ENCODER['ANGLE_MSW']] = 0
        self.stub_registers[mm.ENCODER['ANGLE_LSW']] = 457  # 45.7°
        self.stub_registers[mm.BEND_ANGLES['BEND_1_SETPOINT']] = 900
        self.stub_registers[mm.BEND_ANGLES['BEND_2_SETPOINT']] = 1200
        self.stub_registers[mm.BEND_ANGLES['BEND_3_SETPOINT']] = 560
        print(" Modo STUB ativado")

    def read_register(self, address):
        """Lê 1 registro 16-bit"""
        if self.stub_mode:
            return self.stub_registers.get(address, 0)

        if not self.connected:
            return None

        try:
            result = self.client.read_holding_registers(self.slave_id, address, 1)
            return result[0] if result else None
        except:
            return None

    def read_register_32bit(self, address_msw):
        """Lê 2 registros consecutivos (32-bit)"""
        if self.stub_mode:
            msw = self.stub_registers.get(address_msw, 0)
            lsw = self.stub_registers.get(address_msw + 1, 0)
            return (msw << 16) | lsw

        msw = self.read_register(address_msw)
        lsw = self.read_register(address_msw + 1)

        if msw is None or lsw is None:
            return None

        return (msw << 16) | lsw

    def write_register(self, address, value):
        """Escreve 1 registro"""
        if self.stub_mode:
            self.stub_registers[address] = value & 0xFFFF
            return True

        if not self.connected:
            return False

        try:
            return self.client.write_single_register(self.slave_id, address, value & 0xFFFF)
        except:
            return False

    def write_coil(self, address, value):
        """Escreve 1 coil"""
        if self.stub_mode:
            self.stub_coils[address] = bool(value)
            return True

        if not self.connected:
            return False

        try:
            return self.client.write_single_coil(self.slave_id, address, bool(value))
        except:
            return False

    def press_key(self, address, hold_ms=100):
        """Simula press de tecla (ON ’ delay ’ OFF)"""
        if self.write_coil(address, True):
            time.sleep_ms(hold_ms)
            return self.write_coil(address, False)
        return False
