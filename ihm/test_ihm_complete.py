#!/usr/bin/env python3
"""
Script de Teste Completo - IHM Dobradeira NEOCOUDE-HD-15
Demonstra todas as funcionalidades mapeadas via Modbus

Baseado em: MAPEAMENTO_MODBUS_COMPLETO.md
Data: 15 de Novembro de 2025
"""

import time
from pymodbus.client import ModbusSerialClient

# ============================================================================
# CONFIGURAÇÃO MODBUS
# ============================================================================

MODBUS_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 57600,
    'parity': 'N',
    'stopbits': 2,
    'bytesize': 8,
    'timeout': 1,
}

SLAVE_ID = 1

# ============================================================================
# MAPEAMENTO DE ENDEREÇOS
# ============================================================================

# Encoder (Holding Registers 32-bit)
ENCODER_MSW = 1238
ENCODER_LSW = 1239

# Entradas Digitais E0-E7 (Coils)
INPUTS_BASE = 256  # E0
INPUT_COUNT = 8

# Saídas Digitais S0-S7 (Coils)
OUTPUTS_BASE = 384  # S0
OUTPUT_COUNT = 8

# LEDs (Coils)
LED_BASE = 192  # LED1
LED_COUNT = 5

# Teclado Numérico (Coils)
KEYS_NUMERIC = {
    'K0': 169, 'K1': 160, 'K2': 161, 'K3': 162, 'K4': 163,
    'K5': 164, 'K6': 165, 'K7': 166, 'K8': 167, 'K9': 168,
}

# Teclado Função (Coils)
KEYS_FUNCTION = {
    'S1': 220,      # AUTO/MANUAL toggle
    'S2': 221,      # Reset/Context
    'ENTER': 37,    # Confirm
    'ESC': 188,     # Cancel
    'EDIT': 38,     # Edit mode
    'LOCK': 241,    # Keyboard lock
    'UP': 172,      # Arrow up
    'DOWN': 173,    # Arrow down
}

# Ângulos Programados (Holding Registers 32-bit)
ANGLES = {
    'BEND_1_LEFT':  (2112, 2113),  # MSW, LSW
    'BEND_2_LEFT':  (2120, 2121),
    'BEND_3_LEFT':  (2128, 2129),
    'BEND_1_RIGHT': (2114, 2115),
    'BEND_2_RIGHT': (2122, 2123),
    'BEND_3_RIGHT': (2130, 2131),
}

# Estados Críticos (Coils)
STATE_MODBUS_ENABLED = 190  # 0x00BE - DEVE estar ON

# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class IHMDobradeiraTest:
    """Teste completo da IHM via Modbus"""

    def __init__(self):
        self.client = ModbusSerialClient(**MODBUS_CONFIG)
        self.connected = False

    def connect(self):
        """Conecta ao CLP"""
        print("🔌 Conectando ao CLP Atos MPC4004...")
        self.connected = self.client.connect()
        if self.connected:
            print("✅ Conectado!")
            # Verifica estado Modbus
            modbus_state = self.read_coil(STATE_MODBUS_ENABLED)
            if modbus_state:
                print(f"✅ Estado 0x00BE (Modbus Slave): ATIVO")
            else:
                print(f"⚠️  Estado 0x00BE (Modbus Slave): INATIVO")
        else:
            print("❌ Falha na conexão!")
        return self.connected

    def disconnect(self):
        """Desconecta do CLP"""
        if self.connected:
            self.client.close()
            print("🔌 Desconectado do CLP")

    # ========================================================================
    # LEITURAS
    # ========================================================================

    def read_coil(self, address):
        """Lê um coil (bit)"""
        try:
            result = self.client.read_coils(address, count=1, device_id=SLAVE_ID)
            if not result.isError():
                return result.bits[0]
        except Exception as e:
            print(f"❌ Erro ao ler coil {address}: {e}")
        return None

    def read_coils(self, address, count):
        """Lê múltiplos coils"""
        try:
            result = self.client.read_coils(address, count=count, device_id=SLAVE_ID)
            if not result.isError():
                return result.bits[:count]
        except Exception as e:
            print(f"❌ Erro ao ler coils {address}-{address+count-1}: {e}")
        return None

    def read_holding_register(self, address):
        """Lê um holding register (16-bit)"""
        try:
            result = self.client.read_holding_registers(address, count=1, device_id=SLAVE_ID)
            if not result.isError():
                return result.registers[0]
        except Exception as e:
            print(f"❌ Erro ao ler register {address}: {e}")
        return None

    def read_32bit(self, msw_addr, lsw_addr):
        """Lê um valor 32-bit (MSW + LSW)"""
        try:
            result = self.client.read_holding_registers(msw_addr, count=2, device_id=SLAVE_ID)
            if not result.isError():
                msw, lsw = result.registers
                value = (msw << 16) | lsw
                return value
        except Exception as e:
            print(f"❌ Erro ao ler 32-bit {msw_addr}/{lsw_addr}: {e}")
        return None

    def read_encoder(self):
        """Lê posição atual do encoder"""
        raw = self.read_32bit(ENCODER_MSW, ENCODER_LSW)
        if raw is not None:
            angle = raw / 10.0  # Conversão: raw ÷ 10 = graus
            return angle
        return None

    def read_angle(self, bend_name):
        """Lê um ângulo programado"""
        if bend_name not in ANGLES:
            return None
        msw_addr, lsw_addr = ANGLES[bend_name]
        raw = self.read_32bit(msw_addr, lsw_addr)
        if raw is not None:
            return raw / 10.0
        return None

    def read_inputs(self):
        """Lê todas entradas E0-E7"""
        return self.read_coils(INPUTS_BASE, INPUT_COUNT)

    def read_outputs(self):
        """Lê todas saídas S0-S7"""
        return self.read_coils(OUTPUTS_BASE, OUTPUT_COUNT)

    def read_leds(self):
        """Lê todos LEDs"""
        return self.read_coils(LED_BASE, LED_COUNT)

    # ========================================================================
    # ESCRITAS
    # ========================================================================

    def write_coil(self, address, value):
        """Escreve um coil"""
        try:
            result = self.client.write_coil(address, value, device_id=SLAVE_ID)
            return not result.isError()
        except Exception as e:
            print(f"❌ Erro ao escrever coil {address}: {e}")
            return False

    def press_key(self, key_name, hold_ms=100):
        """Simula pressionar uma tecla (pulso ON-WAIT-OFF)"""
        # Determina endereço
        if key_name in KEYS_NUMERIC:
            address = KEYS_NUMERIC[key_name]
        elif key_name in KEYS_FUNCTION:
            address = KEYS_FUNCTION[key_name]
        else:
            print(f"❌ Tecla desconhecida: {key_name}")
            return False

        print(f"⌨️  Pressionando {key_name} (endereço {address})...")

        # Pulso: ON → WAIT → OFF
        if not self.write_coil(address, True):
            return False
        time.sleep(hold_ms / 1000.0)
        if not self.write_coil(address, False):
            return False

        print(f"✅ Tecla {key_name} pressionada!")
        return True

    def write_angle(self, bend_name, degrees):
        """Escreve um ângulo programado"""
        if bend_name not in ANGLES:
            print(f"❌ Dobra desconhecida: {bend_name}")
            return False

        msw_addr, lsw_addr = ANGLES[bend_name]
        value = int(degrees * 10)  # Conversão: graus × 10
        msw = (value >> 16) & 0xFFFF
        lsw = value & 0xFFFF

        print(f"📐 Escrevendo {degrees}° em {bend_name} (valor={value}, MSW={msw}, LSW={lsw})...")

        try:
            result = self.client.write_registers(msw_addr, [msw, lsw], device_id=SLAVE_ID)
            if not result.isError():
                print(f"✅ Ângulo gravado!")
                return True
        except Exception as e:
            print(f"❌ Erro ao escrever ângulo: {e}")
        return False

    # ========================================================================
    # TESTES E DEMONSTRAÇÕES
    # ========================================================================

    def show_current_state(self):
        """Mostra estado completo da máquina"""
        print("\n" + "="*60)
        print("📊 ESTADO ATUAL DA MÁQUINA")
        print("="*60)

        # Encoder
        angle = self.read_encoder()
        if angle is not None:
            print(f"📐 Ângulo Encoder: {angle:.1f}°")

        # Entradas
        inputs = self.read_inputs()
        if inputs:
            print(f"\n🔌 Entradas E0-E7:")
            for i, state in enumerate(inputs):
                symbol = "🟢" if state else "⚫"
                print(f"   E{i}: {symbol} ({state})")

        # Saídas
        outputs = self.read_outputs()
        if outputs:
            print(f"\n⚡ Saídas S0-S7:")
            for i, state in enumerate(outputs):
                symbol = "🔴" if state else "⚫"
                print(f"   S{i}: {symbol} ({state})")

        # LEDs
        leds = self.read_leds()
        if leds:
            print(f"\n💡 LEDs 1-5:")
            for i, state in enumerate(leds, 1):
                symbol = "🔵" if state else "⚫"
                print(f"   LED{i}: {symbol} ({state})")

        # Ângulos
        print(f"\n📐 Ângulos Programados:")
        for bend_name in ANGLES.keys():
            angle = self.read_angle(bend_name)
            if angle is not None:
                print(f"   {bend_name}: {angle:.1f}°")

        print("="*60 + "\n")

    def test_keyboard(self):
        """Testa pressionar teclas"""
        print("\n🎹 TESTE DE TECLADO")
        print("="*60)

        # Testa S1 (já validado)
        self.press_key('S1')
        time.sleep(0.5)

        # Testa ENTER
        self.press_key('ENTER')
        time.sleep(0.5)

        print("="*60 + "\n")

    def test_write_angles(self):
        """Testa escrever ângulos"""
        print("\n📐 TESTE DE ESCRITA DE ÂNGULOS")
        print("="*60)

        # Exemplos
        self.write_angle('BEND_1_LEFT', 90.0)
        time.sleep(0.3)

        self.write_angle('BEND_2_LEFT', 120.0)
        time.sleep(0.3)

        self.write_angle('BEND_3_LEFT', 45.0)
        time.sleep(0.3)

        # Verifica se gravou
        print("\n✅ Verificando ângulos gravados:")
        for bend_name in ['BEND_1_LEFT', 'BEND_2_LEFT', 'BEND_3_LEFT']:
            angle = self.read_angle(bend_name)
            if angle is not None:
                print(f"   {bend_name}: {angle:.1f}°")

        print("="*60 + "\n")

    def continuous_monitor(self, duration=10):
        """Monitora estado continuamente"""
        print(f"\n📡 MONITORAMENTO CONTÍNUO ({duration}s)")
        print("="*60)

        start_time = time.time()
        last_encoder = None

        while (time.time() - start_time) < duration:
            # Lê encoder
            encoder = self.read_encoder()
            if encoder != last_encoder:
                print(f"📐 Encoder mudou: {encoder:.1f}°")
                last_encoder = encoder

            # Lê entradas críticas
            e6 = self.read_coil(262)  # E6 - testado
            if e6 is not None:
                print(f"🔌 E6: {'ATIVO' if e6 else 'INATIVO'}")

            time.sleep(0.25)  # 4 Hz (250ms)

        print("="*60 + "\n")

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Executa todos os testes"""
    ihm = IHMDobradeiraTest()

    try:
        # Conecta
        if not ihm.connect():
            return

        # Mostra estado atual
        ihm.show_current_state()

        # Testa teclado
        # ihm.test_keyboard()

        # Testa escrita de ângulos
        # ihm.test_write_angles()

        # Monitora continuamente
        # ihm.continuous_monitor(duration=10)

    except KeyboardInterrupt:
        print("\n⚠️  Interrompido pelo usuário")
    finally:
        ihm.disconnect()

if __name__ == "__main__":
    main()
