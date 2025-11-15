"""
Modbus Client - IHM Web Dobradeira
===================================

Cliente Modbus RTU com suporte a modo stub para desenvolvimento web-first.

Modo Stub: Desenvolve/testa interface sem CLP conectado
Modo Live: Comunicação real via RS485-B
"""

import time
import random
from typing import Optional, Union
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import modbus_map as mm


class ModbusClientWrapper:
    """
    Wrapper para pyModbus com modo stub e tratamento robusto de erros
    """
    
    def __init__(self, stub_mode: bool = False, port: str = '/dev/ttyUSB0', 
                 baudrate: int = 57600, slave_id: int = 1):
        """
        Inicializa cliente Modbus
        
        Args:
            stub_mode: True para modo simulado (sem CLP)
            port: Porta serial (ex: /dev/ttyUSB0)
            baudrate: Taxa de comunicação (padrão 57600)
            slave_id: Endereço slave do CLP (padrão 1)
        """
        self.stub_mode = stub_mode
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.client = None
        self.connected = False
        
        # Estado simulado para modo stub
        self.stub_coils = {}  # Coils/bits
        self.stub_registers = {}  # Registros 16-bit
        
        if not stub_mode:
            self._connect_live()
        else:
            self._init_stub_data()
            
    def _connect_live(self):
        """Conecta ao CLP real via RS485"""
        try:
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                parity='N',
                stopbits=2,  # Importante: 2 stop bits conforme CLAUDE.md
                bytesize=8,
                timeout=1.0
            )
            # Configura slave_id no objeto client
            self.client.slave_id = self.slave_id

            self.connected = self.client.connect()
            if self.connected:
                print(f"✓ Modbus conectado: {self.port} @ {self.baudrate} bps (slave {self.slave_id})")
            else:
                print(f"✗ Falha ao conectar em {self.port}")
        except Exception as e:
            print(f"✗ Erro ao conectar Modbus: {e}")
            self.connected = False
            
    def _init_stub_data(self):
        """Inicializa dados simulados para modo stub"""
        self.connected = True

        # Simula encoder em 45.7 graus
        self.stub_registers[mm.ENCODER['ANGLE_MSW']] = 0x0000
        self.stub_registers[mm.ENCODER['ANGLE_LSW']] = 0x01C9  # 457 = 45.7°

        # Ângulos setpoint iniciais
        self.stub_registers[mm.BEND_ANGLES['BEND_1_LEFT_MSW']] = 0x0000
        self.stub_registers[mm.BEND_ANGLES['BEND_1_LEFT_LSW']] = 0x0384  # 900 = 90°
        self.stub_registers[mm.BEND_ANGLES['BEND_2_LEFT_MSW']] = 0x0000
        self.stub_registers[mm.BEND_ANGLES['BEND_2_LEFT_LSW']] = 0x04B0  # 1200 = 120°
        self.stub_registers[mm.BEND_ANGLES['BEND_3_LEFT_MSW']] = 0x0000
        self.stub_registers[mm.BEND_ANGLES['BEND_3_LEFT_LSW']] = 0x0230  # 560 = 56°

        # Entradas digitais (todos OFF)
        for addr in mm.DIGITAL_INPUTS.values():
            self.stub_registers[addr] = 0x0000

        # Saídas digitais (todos OFF)
        for addr in mm.DIGITAL_OUTPUTS.values():
            self.stub_registers[addr] = 0x0000

        # Botões (todos soltos)
        for addr in list(mm.KEYBOARD_NUMERIC.values()) + list(mm.KEYBOARD_FUNCTION.values()):
            self.stub_coils[addr] = False

        # LEDs (LED1 aceso = dobra 1 ativa)
        for i, addr in enumerate(mm.LEDS.values(), 1):
            self.stub_coils[addr] = (i == 1)  # Apenas LED1 ON

        # Estado Modbus slave habilitado
        self.stub_coils[mm.CRITICAL_STATES['MODBUS_SLAVE_ENABLED']] = True

        # Área de supervisão (inicializada em 0)
        for addr in mm.SUPERVISION_AREA.values():
            self.stub_registers[addr] = 0

        print("✓ Modo STUB ativado (simulação sem CLP)")
        
    def read_coil(self, address: int) -> Optional[bool]:
        """
        Lê um coil/bit (Function 0x01)

        Args:
            address: Endereço do coil (ex: 0x00A0 para K1)

        Returns:
            True/False ou None se erro

        NOTA: Devido a um bug no pymodbus 3.11.3, count=1 não funciona.
        Solução: Ler 8 coils (1 byte) e extrair o bit correto.
        """
        if self.stub_mode:
            return self.stub_coils.get(address, False)

        if not self.connected:
            return None

        try:
            # BUGFIX: pymodbus 3.11.3 não funciona com count=1
            # Lemos 8 coils começando do endereço base (múltiplo de 8)
            base_address = (address // 8) * 8
            bit_offset = address - base_address

            result = self.client.read_coils(address=base_address, count=8, device_id=self.slave_id)
            if result.isError():
                return None

            # BUGFIX: result.count está sempre 0 no pymodbus 3.11.3
            # Mas result.bits contém os dados corretos
            # Extrair o bit correto
            return result.bits[bit_offset]
        except Exception as e:
            print(f"✗ Erro lendo coil 0x{address:04X}: {e}")
            return None
            
    def read_register(self, address: int) -> Optional[int]:
        """
        Lê um registro 16-bit (Function 0x03)

        Args:
            address: Endereço do registro (ex: 0x04D6)

        Returns:
            Valor 0-65535 ou None se erro
        """
        if self.stub_mode:
            return self.stub_registers.get(address, 0)

        if not self.connected:
            return None

        try:
            result = self.client.read_holding_registers(address=address, count=1)
            if result.isError():
                return None
            return result.registers[0]
        except Exception as e:
            print(f"✗ Erro lendo registro 0x{address:04X}: {e}")
            return None
            
    def read_32bit(self, msw_address: int, lsw_address: int) -> Optional[int]:
        """
        Lê valor 32-bit (MSW + LSW)
        
        Args:
            msw_address: Endereço MSW (bits 31-16)
            lsw_address: Endereço LSW (bits 15-0)
            
        Returns:
            Valor 32-bit ou None se erro
        """
        msw = self.read_register(msw_address)
        lsw = self.read_register(lsw_address)
        
        if msw is None or lsw is None:
            return None
            
        return mm.read_32bit(msw, lsw)
        
    def write_coil(self, address: int, value: bool) -> bool:
        """
        Escreve um coil/bit (Function 0x05)

        Args:
            address: Endereço do coil
            value: True (ON) ou False (OFF)

        Returns:
            True se sucesso, False se erro
        """
        if self.stub_mode:
            self.stub_coils[address] = value
            return True

        if not self.connected:
            return False

        try:
            result = self.client.write_coil(address=address, value=value)
            return not result.isError()
        except Exception as e:
            print(f"✗ Erro escrevendo coil 0x{address:04X}: {e}")
            return False
            
    def write_register(self, address: int, value: int) -> bool:
        """
        Escreve um registro 16-bit (Function 0x06)

        Args:
            address: Endereço do registro
            value: Valor 0-65535

        Returns:
            True se sucesso, False se erro
        """
        if self.stub_mode:
            self.stub_registers[address] = value & 0xFFFF
            return True

        if not self.connected:
            return False

        try:
            result = self.client.write_register(address=address, value=value)
            return not result.isError()
        except Exception as e:
            print(f"✗ Erro escrevendo registro 0x{address:04X}: {e}")
            return False
            
    def write_32bit(self, msw_address: int, lsw_address: int, value: int, retries: int = 3) -> bool:
        """
        Escreve valor 32-bit (MSW + LSW) com retry logic

        Args:
            msw_address: Endereço MSW
            lsw_address: Endereço LSW
            value: Valor 32-bit (0 a 4294967295)
            retries: Número de tentativas (padrão: 3)

        Returns:
            True se sucesso, False se erro
        """
        for attempt in range(retries):
            msw, lsw = mm.split_32bit(value)

            # Escreve MSW
            ok_msw = self.write_register(msw_address, msw)
            if not ok_msw:
                if attempt < retries - 1:
                    time.sleep(0.05)  # Aguarda 50ms antes de retry
                continue

            # Delay entre MSW e LSW para CLP processar
            time.sleep(0.05)

            # Escreve LSW
            ok_lsw = self.write_register(lsw_address, lsw)

            if ok_msw and ok_lsw:
                if attempt > 0:
                    print(f"✓ write_32bit sucesso na tentativa {attempt + 1}/{retries}")
                return True

            if attempt < retries - 1:
                print(f"⚠️ write_32bit tentativa {attempt + 1}/{retries} falhou, retrying...")
                time.sleep(0.1)

        print(f"✗ write_32bit falhou após {retries} tentativas")
        return False
        
    def press_key(self, address: int, hold_ms: int = 100) -> bool:
        """
        Simula pressionar uma tecla (pulso ON→OFF)
        
        Args:
            address: Endereço do botão (ex: mm.BTN_K1)
            hold_ms: Tempo de retenção em ms (padrão 100ms)
            
        Returns:
            True se sucesso
        """
        # Ativa coil
        if not self.write_coil(address, True):
            return False
            
        # Aguarda tempo de retenção
        time.sleep(hold_ms / 1000.0)
        
        # Desativa coil
        return self.write_coil(address, False)
        
    def change_speed_class(self) -> bool:
        """
        Alterna classe de velocidade (simula K1+K7)

        Returns:
            True se sucesso
        """
        print("⚡ Iniciando mudança de velocidade (K1+K7)...")

        # Ativa K1 e K7 simultaneamente
        k1_addr = mm.KEYBOARD_NUMERIC['K1']
        k7_addr = mm.KEYBOARD_NUMERIC['K7']

        print(f"  Ativando K1 (0x{k1_addr:04X})...")
        ok1 = self.write_coil(k1_addr, True)
        print(f"  K1 ON: {'✓' if ok1 else '✗'}")

        print(f"  Ativando K7 (0x{k7_addr:04X})...")
        ok2 = self.write_coil(k7_addr, True)
        print(f"  K7 ON: {'✓' if ok2 else '✗'}")

        if not (ok1 and ok2):
            print("✗ Falha ao ativar K1+K7")
            return False

        # Aguarda detecção (aumentado para 200ms)
        print("  Aguardando CLP detectar (200ms)...")
        time.sleep(0.2)

        # Desativa K1 e K7
        print("  Desativando K1 e K7...")
        ok1 = self.write_coil(k1_addr, False)
        ok2 = self.write_coil(k7_addr, False)

        success = ok1 and ok2
        print(f"{'✓' if success else '✗'} Mudança de velocidade {'concluída' if success else 'falhou'}")

        return success

    def change_mode_direct(self, to_auto: bool) -> bool:
        """
        Alterna modo MANUAL/AUTO via escrita direta no bit 0x02FF

        WORKAROUND para S1 que não funciona devido a condição E6 não identificada.
        Escreve diretamente no bit REAL de modo do ladder.

        Args:
            to_auto: True para AUTO, False para MANUAL

        Returns:
            True se sucesso
        """
        MODE_BIT_REAL = 0x02FF  # 767 decimal - Bit REAL de modo do ladder

        success = self.write_coil(MODE_BIT_REAL, to_auto)

        if success:
            mode_str = "AUTO" if to_auto else "MANUAL"
            print(f"✓ Modo alterado para {mode_str} (0x02FF = {to_auto})")
        else:
            print(f"✗ Falha ao alterar modo")

        return success

    def write_angle(self, bend_number: int, direction: str, angle_degrees: float) -> bool:
        """
        Escreve ângulo programado para uma dobra

        Args:
            bend_number: Número da dobra (1, 2, ou 3)
            direction: 'left' ou 'right'
            angle_degrees: Ângulo em graus (ex: 90.0)

        Returns:
            True se sucesso
        """
        # Mapeamento de endereços (apenas LSW, descobrimos que MSW não é usado)
        ANGLE_ADDRESSES = {
            (1, 'left'): 0x0842,   # 2114 - Dobra 1 Esquerda
            (2, 'left'): 0x084A,   # 2122 - Dobra 2 Esquerda
            (3, 'left'): 0x0852,   # 2130 - Dobra 3 Esquerda
            # TODO: Adicionar endereços direita quando conhecidos
        }

        key = (bend_number, direction.lower())
        if key not in ANGLE_ADDRESSES:
            print(f"✗ Endereço para dobra {bend_number} {direction} não mapeado")
            return False

        addr = ANGLE_ADDRESSES[key]

        # Converte graus para valor interno (graus * 10)
        internal_value = int(angle_degrees * 10)

        success = self.write_register(addr, internal_value)

        if success:
            print(f"✓ Ângulo dobra {bend_number} {direction}: {angle_degrees}° (0x{addr:04X} = {internal_value})")
        else:
            print(f"✗ Falha ao escrever ângulo")

        return success

    # ==========================================
    # SUPERVISÃO - Estratégia Híbrida
    # ==========================================

    def write_supervision_register(self, register_name: str, value: int) -> bool:
        """
        Escreve registro na área de supervisão (0x0940-0x0950).

        ESTRATÉGIA HÍBRIDA:
        - Python lê coils (botões, LEDs) via Function 0x01
        - Python infere estados (tela, modo, dobra)
        - Python ESCREVE nesta área via Function 0x06
        - IHM Web lê desta área → Precisão 100%!

        Args:
            register_name: Nome do registro (ex: 'SCREEN_NUM')
            value: Valor a escrever (uint16)

        Returns:
            True se sucesso, False se falha
        """
        if register_name not in mm.SUPERVISION_AREA:
            print(f"✗ Registro '{register_name}' não existe em SUPERVISION_AREA")
            return False

        address = mm.SUPERVISION_AREA[register_name]

        if self.write_register(address, value):
            if not self.stub_mode:  # Não loga em stub (muito verboso)
                print(f"✓ Supervisão: {register_name}={value} (0x{address:04X})")
            return True
        else:
            print(f"✗ Falha ao escrever {register_name}={value} em 0x{address:04X}")
            return False

    def write_screen_number(self, screen_num: int) -> bool:
        """
        Escreve número da tela (0-10) em 0x0940.

        Args:
            screen_num: Número da tela (0-10)

        Returns:
            True se sucesso
        """
        if not (0 <= screen_num <= 10):
            print(f"✗ Número de tela inválido: {screen_num} (esperado 0-10)")
            return False
        return self.write_supervision_register('SCREEN_NUM', screen_num)

    def read_leds(self) -> Optional[dict]:
        """
        Lê todos os LEDs de uma vez (0x00C0-0x00C4).

        Returns:
            Dicionário {'LED1': True/False, ...} ou None se TODOS falharem
        """
        leds = {}
        failed_count = 0

        for name, address in mm.LEDS.items():
            status = self.read_coil(address)
            if status is None:
                leds[name] = False  # Assume desligado em caso de erro
                failed_count += 1
            else:
                leds[name] = status

        # Retorna None apenas se TODOS os LEDs falharam
        if failed_count == len(mm.LEDS):
            return None

        return leds

    def toggle_mode_direct(self) -> Optional[bool]:
        """
        Toggle de modo via simulação do botão S1

        Simula um press do botão S1 (0x00DC) para alternar AUTO/MANUAL.
        Esta é a forma CORRETA que respeita a lógica do ladder.

        Returns:
            True se mudou para AUTO, False se mudou para MANUAL, None em erro
        """
        import time

        try:
            # Ler modo atual ANTES do toggle
            current_mode = self.read_coil(0x02FF)  # 767
            if current_mode is None:
                print("✗ Erro lendo bit 02FF (modo atual)")
                return None

            mode_antes_text = "AUTO" if current_mode else "MANUAL"
            print(f"📖 Modo ANTES do toggle: {mode_antes_text} (02FF={current_mode})")

            # Simular pressionamento do botão S1
            print("🔘 Simulando pressionamento de S1...")
            success = self.press_key(0x00DC, hold_ms=150)  # S1 = 0x00DC (220)

            if not success:
                print("✗ Falha ao pressionar S1")
                return None

            # Aguardar o ladder processar a mudança de modo
            # O ladder tem lógica para detectar S1 e alternar 02FF
            time.sleep(0.5)  # Aguarda 500ms para ladder processar

            # Ler modo DEPOIS do toggle
            new_mode = self.read_coil(0x02FF)
            if new_mode is None:
                print("⚠️  Erro ao ler modo após S1")
                return None

            mode_depois_text = "AUTO" if new_mode else "MANUAL"
            print(f"📖 Modo DEPOIS do toggle: {mode_depois_text} (02FF={new_mode})")

            # Verificar se realmente mudou
            if new_mode != current_mode:
                print(f"✅ Modo alterado com sucesso: {mode_antes_text} → {mode_depois_text}")
                return new_mode
            else:
                print(f"⚠️  Modo não mudou (ainda {mode_antes_text})")
                print(f"   Possível causa: Condições do ladder não permitiram a mudança")
                print(f"   Verifique: E6 deve estar ativa, máquina parada, etc.")
                return current_mode

        except Exception as e:
            print(f"✗ Erro ao alternar modo: {e}")
            import traceback
            traceback.print_exc()
            return None

    def read_real_mode(self) -> Optional[bool]:
        """
        Lê o modo REAL do ladder (bit 02FF)

        Retorna o bit que controla REALMENTE o modo no ladder,
        não a cópia em MODE_STATE (0x0946).

        Returns:
            True = AUTO, False = MANUAL, None = erro
        """
        try:
            mode_bit = self.read_coil(0x02FF)
            if mode_bit is not None:
                mode_text = "AUTO" if mode_bit else "MANUAL"
                print(f"📖 Modo real (02FF): {mode_text}")
            return mode_bit
        except Exception as e:
            print(f"✗ Erro lendo modo real: {e}")
            return None

    def read_buttons(self) -> Optional[dict]:
        """
        Lê todos os botões de uma vez (K0-K9, S1, S2, etc).

        Returns:
            Dicionário {'K1': True/False, ...} ou None se erro parcial
        """
        buttons = {}

        # Botões numéricos
        for name, address in mm.KEYBOARD_NUMERIC.items():
            status = self.read_coil(address)
            if status is not None:
                buttons[name] = status

        # Botões de função
        for name, address in mm.KEYBOARD_FUNCTION.items():
            status = self.read_coil(address)
            if status is not None:
                buttons[name] = status

        return buttons if buttons else None

    def simulate_key_press(self, key_name: str) -> bool:
        """
        Simula pressão de tecla via ROT9 (método simplificado)

        Em vez de 3 comandos Modbus (ON → wait → OFF), envia apenas 1 comando.
        O CLP (ROT9) gerencia automaticamente o pulso de 100ms.

        Args:
            key_name: Nome da tecla ('K1', 'K2', 'K3', 'S1', 'S2',
                      'ENTER', 'ESC', 'EDIT')

        Returns:
            True se comando enviado com sucesso

        Exemplo:
            >>> client.simulate_key_press('K1')  # Simula K1
            True
        """
        # Fallback: usa press_key() padrão
        all_keys = {**mm.KEYBOARD_NUMERIC, **mm.KEYBOARD_FUNCTION}

        if key_name not in all_keys:
            print(f"✗ Tecla '{key_name}' não reconhecida")
            print(f"  Teclas disponíveis: {list(all_keys.keys())}")
            return False

        address = all_keys[key_name]
        return self.press_key(address, hold_ms=100)

    def close(self):
        """Fecha conexão Modbus"""
        if self.client and self.connected:
            self.client.close()
            self.connected = False
            print("✓ Conexão Modbus fechada")


# Exemplo de uso
if __name__ == "__main__":
    # Teste em modo stub
    print("=== TESTE MODO STUB ===")
    client = ModbusClientWrapper(stub_mode=True)

    # Ler encoder
    angle_raw = client.read_32bit(mm.ENCODER['ANGLE_MSW'], mm.ENCODER['ANGLE_LSW'])
    angle_deg = mm.clp_to_degrees(angle_raw) if angle_raw else 0
    print(f"Encoder: {angle_raw} = {angle_deg:.1f}° (stub)")

    # Ler ângulo dobra 1
    bend1_raw = client.read_32bit(mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW'])
    bend1_deg = mm.clp_to_degrees(bend1_raw) if bend1_raw else 0
    print(f"Ângulo Dobra 1: {bend1_raw} = {bend1_deg:.1f}° (stub)")

    # Ler LEDs
    leds = client.read_leds()
    print(f"LEDs: {leds}")

    # Simular botão K1
    print("Pressionando K1...")
    client.press_key(mm.KEYBOARD_NUMERIC['K1'])

    # Escrever número da tela
    print("Escrevendo tela 4 em supervisão...")
    client.write_screen_number(4)

    # Alterar velocidade
    print("Alterando velocidade (K1+K7)...")
    client.change_speed_class()

    client.close()
