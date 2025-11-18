"""
Modbus Client ESP32 - IHM Web Dobradeira
Vers�o MicroPython adaptada de modbus_client.py
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
        self.stub_registers[mm.ENCODER['ANGLE_LSW']] = 457  # 45.7�
        self.stub_registers[mm.BEND_ANGLES['BEND_1_SETPOINT']] = 900
        self.stub_registers[mm.BEND_ANGLES['BEND_2_SETPOINT']] = 1200
        self.stub_registers[mm.BEND_ANGLES['BEND_3_SETPOINT']] = 560
        print(" Modo STUB ativado")

    def read_register(self, address):
        """L� 1 registro 16-bit"""
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
        """Le 2 registros consecutivos (32-bit) - MSW e MSW+1"""
        if self.stub_mode:
            msw = self.stub_registers.get(address_msw, 0)
            lsw = self.stub_registers.get(address_msw + 1, 0)
            return (msw << 16) | lsw

        msw = self.read_register(address_msw)
        lsw = self.read_register(address_msw + 1)

        if msw is None or lsw is None:
            return None

        return (msw << 16) | lsw

    def read_register_32bit_scada(self, address_lsw):
        """Le 2 registros nao-consecutivos (32-bit) - area SCADA 0x0B00
        SCADA: LSW em addr, MSW em addr+2 (pulando 1 registro)"""
        if self.stub_mode:
            lsw = self.stub_registers.get(address_lsw, 0)
            msw = self.stub_registers.get(address_lsw + 2, 0)
            return (msw << 16) | lsw

        lsw = self.read_register(address_lsw)
        msw = self.read_register(address_lsw + 2)

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
            result = self.client.write_single_register(self.slave_id, address, value & 0xFFFF)
            time.sleep_ms(50)  # Delay entre comandos
            return result
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
        """Simula press de tecla (ON � delay � OFF)"""
        if self.write_coil(address, True):
            time.sleep_ms(hold_ms)
            return self.write_coil(address, False)
        return False

    def write_bend_angle(self, bend_number, degrees):
        """
        Grava angulo de dobra via area MODBUS INPUT (0x0A00+) com triggers

        FLUXO VALIDADO (ROT5.lad Lines 7-12):
          1. IHM grava MSW em 0x0A00 (Dobra 1) / 0x0A04 (Dobra 2) / 0x0A08 (Dobra 3)
          2. IHM grava LSW em 0x0A02 (Dobra 1) / 0x0A06 (Dobra 2) / 0x0A0A (Dobra 3)
          3. IHM aciona trigger 0x0390/0x0391/0x0392 via COIL (Function 0x05)
          4. ROT5 auto-copia: 0x0A00->0x0842, 0x0A02->0x0840 (somente quando trigger ativo)
          5. ROT5 Line 13: MOV 0x0840->0x0B00 (espelho SCADA sempre ativo)
          6. Principal.lad le de 0x0840/0x0842 para calculos de dobra

        Args:
            bend_number (int): 1, 2 ou 3
            degrees (float): Angulo em graus (ex: 90.5)

        Returns:
            bool: True se sucesso
        """
        if bend_number not in [1, 2, 3]:
            print(f"Dobra invalida: {bend_number}")
            return False

        # Mapeamento correto conforme ROT5.lad
        addresses = {
            1: {'msw': mm.BEND_ANGLES_MODBUS_INPUT['BEND_1_INPUT_MSW'],
                'lsw': mm.BEND_ANGLES_MODBUS_INPUT['BEND_1_INPUT_LSW'],
                'trigger': mm.BEND_ANGLES_MODBUS_INPUT['BEND_1_TRIGGER']},
            2: {'msw': mm.BEND_ANGLES_MODBUS_INPUT['BEND_2_INPUT_MSW'],
                'lsw': mm.BEND_ANGLES_MODBUS_INPUT['BEND_2_INPUT_LSW'],
                'trigger': mm.BEND_ANGLES_MODBUS_INPUT['BEND_2_TRIGGER']},
            3: {'msw': mm.BEND_ANGLES_MODBUS_INPUT['BEND_3_INPUT_MSW'],
                'lsw': mm.BEND_ANGLES_MODBUS_INPUT['BEND_3_INPUT_LSW'],
                'trigger': mm.BEND_ANGLES_MODBUS_INPUT['BEND_3_TRIGGER']},
        }

        addr = addresses[bend_number]

        # Converte graus para valor CLP (32-bit)
        value_32bit = int(degrees * 10)
        msw = (value_32bit >> 16) & 0xFFFF
        lsw = value_32bit & 0xFFFF

        print(f"Gravando Dobra {bend_number}: {degrees}° -> 0x{addr['msw']:04X}/0x{addr['lsw']:04X} (MSW={msw}, LSW={lsw})")

        # 1. Grava MSW e LSW (Function 0x06 - Write Single Register)
        ok_msw = self.write_register(addr['msw'], msw)
        ok_lsw = self.write_register(addr['lsw'], lsw)

        if not (ok_msw and ok_lsw):
            print("Erro gravacao registros")
            return False

        # 2. Aciona trigger via COIL (Function 0x05 - Force Single Coil)
        # IMPORTANTE: Triggers 0x0390/0x0391/0x0392 sao COILS, nao registros!
        print(f"  Acionando trigger 0x{addr['trigger']:04X} (via coil)...")

        # Liga trigger (coil ON)
        if not self.write_coil(addr['trigger'], True):
            print("Erro trigger ON")
            return False

        time.sleep_ms(100)  # Aguarda 2 scans CLP (~12ms scan time, usar 100ms seguro)

        # Desliga trigger (coil OFF)
        if not self.write_coil(addr['trigger'], False):
            print("Erro trigger OFF")
            return False

        print(f"OK: Dobra {bend_number} = {degrees}°")
        return True

    def read_bend_angle(self, bend_number):
        """
        Le angulo de dobra da area SCADA (0x0B00 - espelho read-only)

        ROT5.lad Line 13: MOV 0x0840->0x0B00 (sempre ativo, sem trigger)
        Esta area e sincronizada automaticamente pelo ladder com os valores oficiais.

        IMPORTANTE: Area SCADA usa GAP entre LSW e MSW:
          - LSW em addr base
          - MSW em addr base+2 (pulando 1 registro)

        Args:
            bend_number (int): 1, 2 ou 3

        Returns:
            float: Angulo em graus (ou None se erro)
        """
        if bend_number not in [1, 2, 3]:
            print(f"Dobra invalida: {bend_number}")
            return None

        # Mapeamento area SCADA (read-only mirror)
        addresses_lsw = {
            1: mm.BEND_ANGLES_SCADA['BEND_1_SCADA_LSW'],  # 0x0B00
            2: mm.BEND_ANGLES_SCADA['BEND_2_SCADA_LSW'],  # 0x0B04
            3: mm.BEND_ANGLES_SCADA['BEND_3_SCADA_LSW'],  # 0x0B08
        }

        addr_lsw = addresses_lsw[bend_number]

        # Le 32-bit com gap handling (LSW em addr, MSW em addr+2)
        value_32bit = self.read_register_32bit_scada(addr_lsw)

        if value_32bit is None:
            print(f"Erro lendo Dobra {bend_number} (SCADA)")
            return None

        # Converte para graus
        degrees = mm.clp_to_degrees(value_32bit)
        return degrees
