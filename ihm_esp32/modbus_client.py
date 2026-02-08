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

        # Contador de erros consecutivos para detecção de desconexão
        self.consecutive_errors = 0
        self.max_errors_before_disconnect = 10  # OTIMIZADO: 10 erros seguidos (mais tolerante)

        # Reconexão automática
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 3
        self.last_reconnect_attempt = 0
        self.reconnect_interval = 5.0  # Tenta reconectar a cada 5 segundos

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
            print(f"🔌 Tentando conectar em {self.port}...")
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                parity='N',
                stopbits=2,  # CORRIGIDO 27/Nov/2025: 2 stop bits necessário
                bytesize=8,
                timeout=0.5  # OTIMIZADO 06/Jan/2026: 500ms para estabilidade @ 57600bps
            )
            # Configura slave_id no objeto client
            self.client.slave_id = self.slave_id

            self.connected = self.client.connect()
            if self.connected:
                print(f"✓ Modbus conectado: {self.port} @ {self.baudrate} bps (slave {self.slave_id})")
            else:
                print(f"✗ Falha ao conectar em {self.port} - CLP desligado ou cabo desconectado")
        except Exception as e:
            print(f"✗ Erro ao conectar Modbus: {e}")
            self.connected = False
            
    def _handle_communication_error(self, error_msg: str):
        """
        Gerencia erros de comunicação com contador de erros consecutivos.
        Só marca como desconectado após múltiplos erros seguidos.

        Args:
            error_msg: Mensagem de erro para logging
        """
        self.consecutive_errors += 1

        if self.consecutive_errors >= self.max_errors_before_disconnect:
            if self.connected:  # Só loga na primeira vez que desconecta
                print(f"✗ [DESCONEXÃO DETECTADA] {self.consecutive_errors} erros consecutivos")
                print(f"  Último erro: {error_msg}")
                self.connected = False
        # Não loga erros individuais para não poluir o console

    def _try_reconnect(self):
        """
        Tenta reconectar ao CLP quando desconectado.
        Usa throttling para não sobrecarregar o sistema.

        Returns:
            True se reconectou com sucesso, False caso contrário
        """
        import time

        current_time = time.time()

        # Throttling: só tenta reconectar após intervalo mínimo
        if current_time - self.last_reconnect_attempt < self.reconnect_interval:
            return False

        self.last_reconnect_attempt = current_time
        self.reconnect_attempts += 1

        if self.reconnect_attempts > self.max_reconnect_attempts:
            # Após max tentativas, aumenta o intervalo para não ficar tentando eternamente
            self.reconnect_interval = min(30.0, self.reconnect_interval * 1.5)
            self.reconnect_attempts = 0

        print(f"🔄 Tentando reconectar ao CLP (tentativa {self.reconnect_attempts}/{self.max_reconnect_attempts})...")

        try:
            # Fecha conexão antiga se existir
            if self.client:
                try:
                    self.client.close()
                except:
                    pass

            # Tenta nova conexão
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                parity='N',
                stopbits=2,  # CORRIGIDO 27/Nov/2025: 2 stop bits necessário
                bytesize=8,
                timeout=0.5  # OTIMIZADO 06/Jan/2026: 500ms para estabilidade
            )
            self.client.slave_id = self.slave_id

            if self.client.connect():
                # Testa leitura para confirmar que CLP está respondendo
                # Usa COILS porque INPUT REGISTERS pode não existir no endereço 0
                result = self.client.read_coils(address=0x00C0, count=8, slave=self.slave_id)
                if not result.isError():
                    print(f"✅ RECONECTADO com sucesso ao CLP!")
                    self.connected = True
                    self.consecutive_errors = 0
                    self.reconnect_attempts = 0
                    self.reconnect_interval = 5.0  # Reset intervalo
                    return True
                else:
                    print(f"✗ CLP não respondeu ao teste de leitura: {result}")

        except Exception as e:
            print(f"✗ Falha ao reconectar: {e}")

        return False

    def _init_stub_data(self):
        """Inicializa dados simulados para modo stub"""
        # Em modo stub, connected = False para indicar que não há CLP real
        # Isso faz o frontend mostrar status correto (vermelho = sem CLP)
        self.connected = False

        # Simula encoder em 45.7 graus
        self.stub_registers[mm.ENCODER['ANGLE_MSW']] = 0x0000
        self.stub_registers[mm.ENCODER['ANGLE_LSW']] = 0x01C9  # 457 = 45.7°

        # Ângulos setpoint iniciais - COMENTADO: mm.BEND_ANGLES não existe
        # self.stub_registers[mm.BEND_ANGLES['BEND_1_SETPOINT']] = 900   # 90.0°
        # self.stub_registers[mm.BEND_ANGLES['BEND_2_SETPOINT']] = 1200  # 120.0°
        # self.stub_registers[mm.BEND_ANGLES['BEND_3_SETPOINT']] = 560   # 56.0°
        # TODO: Usar BEND_ANGLES_SCADA ou BEND_ANGLES_MODBUS_INPUT

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
            # Tenta reconectar automaticamente
            self._try_reconnect()
            if not self.connected:
                return None

        try:
            # pymodbus usa endereçamento correto diretamente
            # CORRIGIDO: Usar address direto (testado 18/Nov/2025)

            # BUGFIX: pymodbus 3.11.3 não funciona com count=1
            # Lemos 8 coils começando do endereço base (múltiplo de 8)
            base_address = (address // 8) * 8
            bit_offset = address - base_address

            result = self.client.read_coils(address=base_address, count=8, slave=self.slave_id)
            if result.isError():
                self._handle_communication_error(f"Erro ao ler coil 0x{address:04X}")
                return None

            # Sucesso - reseta contador de erros
            self.consecutive_errors = 0

            # BUGFIX: result.count está sempre 0 no pymodbus 3.11.3
            # Mas result.bits contém os dados corretos
            # Extrair o bit correto
            return result.bits[bit_offset]
        except Exception as e:
            self._handle_communication_error(f"Exceção ao ler coil 0x{address:04X}: {e}")
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
            # Tenta reconectar automaticamente
            self._try_reconnect()
            if not self.connected:
                return None

        try:
            # pymodbus 3.x: NÃO precisa subtrair 1, slave_id já configurado no objeto client
            # CORRIGIDO 02/Jan/2026: ENCODER em 04D6 usa HOLDING REGISTERS (FC 0x03)
            result = self.client.read_holding_registers(address=address, count=1, slave=self.slave_id)
            if result.isError():
                self._handle_communication_error(f"Erro ao ler registro 0x{address:04X}")
                return None

            # Sucesso - reseta contador de erros
            self.consecutive_errors = 0
            value = result.registers[0]
            return value
        except Exception as e:
            self._handle_communication_error(f"Exceção ao ler registro 0x{address:04X}: {e}")
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
        if self.stub_mode:
            msw = self.stub_registers.get(msw_address, 0)
            lsw = self.stub_registers.get(lsw_address, 0)
            return mm.read_32bit(msw, lsw)

        if not self.connected:
            # Tenta reconectar automaticamente
            self._try_reconnect()
            if not self.connected:
                return None

        try:
            # OTIMIZADO: Ler 2 registros consecutivos de uma vez (mais eficiente e funciona melhor)
            # CORRIGIDO 02/Jan/2026: ENCODER usa HOLDING REGISTERS (FC 0x03)!
            result = self.client.read_holding_registers(address=msw_address, count=2, slave=self.slave_id)
            if result.isError():
                self._handle_communication_error(f"Erro ao ler 32-bit 0x{msw_address:04X}")
                return None

            # Sucesso - reseta contador de erros
            self.consecutive_errors = 0

            msw = result.registers[0]
            lsw = result.registers[1]
            return mm.read_32bit(msw, lsw)
        except Exception as e:
            self._handle_communication_error(f"Exceção ao ler 32-bit 0x{msw_address:04X}: {e}")
            return None
        
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
            # Modo stub: simula escrita bem-sucedida
            return True

        if not self.connected:
            return False

        try:
            # CORRIGIDO 28/Nov/2025: NÃO subtrair 1!
            # O pymodbus 3.x usa endereçamento direto (igual read_coil e write_register)
            # O offset -1 estava causando escrita no endereço errado (0x0381 em vez de 0x0382, etc)
            result = self.client.write_coil(address=address, value=value, slave=self.slave_id)
            if result.isError():
                print(f"✗ [DEBUG] write_coil 0x{address:04X}: result.isError()=True")
            return not result.isError()
        except Exception as e:
            print(f"✗ Erro escrevendo coil 0x{address:04X}: {e}")
            import traceback
            traceback.print_exc()
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
            # pymodbus 3.x: NÃO precisa subtrair 1, usa endereçamento direto
            result = self.client.write_register(address=address, value=value, slave=self.slave_id)
            if result.isError():
                print(f"✗ [DEBUG] write_register 0x{address:04X}: result.isError()=True")
            return not result.isError()
        except Exception as e:
            print(f"✗ Erro escrevendo registro 0x{address:04X}: {e}")
            import traceback
            traceback.print_exc()
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

    def write_bend_angle(self, bend_number: int, degrees: float, verify: bool = True) -> bool:
        """
        Grava ângulo REAL de dobra com verificação read-after-write.

        CORRIGIDO 08/Fev/2026: READ = WRITE (mesmos endereços 0x0A00+)
        Verificação agora lê do mesmo endereço que escreveu (não depende do ladder copiar).

        Endereços (DECIMAL):
          - Dobra 1: 2560 (0x0A00)
          - Dobra 2: 2562 (0x0A02)
          - Dobra 3: 2564 (0x0A04)

        Args:
            bend_number (int): 1, 2 ou 3
            degrees (float): Ângulo REAL da dobra (ex: 90.0°)
            verify (bool): Se True, lê de volta para confirmar (recomendado)

        Returns:
            bool: True se sucesso E verificado

        Exemplo:
            >>> client.write_bend_angle(1, 90.0)
            ✎ Gravando Dobra 1: 90.0° → valor 180 → endereço 2560
            ✓ Verificação OK: lido 180 = esperado 180
            True
        """
        if bend_number not in [1, 2, 3]:
            print(f"✗ Número de dobra inválido: {bend_number} (deve ser 1, 2 ou 3)")
            return False

        # Mapeamento: Endereços de ESCRITA (DECIMAL)
        write_addresses = {
            1: mm.BEND_ANGLES['ANGULO_1_WRITE'],    # 2560 (0x0A00)
            2: mm.BEND_ANGLES['ANGULO_2_WRITE'],    # 2562 (0x0A02)
            3: mm.BEND_ANGLES['ANGULO_3_WRITE'],    # 2564 (0x0A04)
        }

        # Mapeamento: Endereços de LEITURA para verificação
        read_addresses = {
            1: mm.BEND_ANGLES['ANGULO_1_READ'],     # 2114 (0x0842)
            2: mm.BEND_ANGLES['ANGULO_2_READ'],     # 2116 (0x0844)
            3: mm.BEND_ANGLES['ANGULO_3_READ'],     # 2118 (0x0846)
        }

        write_addr = write_addresses[bend_number]
        read_addr = read_addresses[bend_number]

        # Converter ângulo REAL para valor CLP
        clp_value = mm.real_angle_to_clp(degrees)

        if clp_value > 2048:
            print(f"✗ Valor fora do range: {degrees}° → {clp_value} > 2048")
            return False

        print(f"✎ [WRITE] Dobra {bend_number}: {degrees}° → valor {clp_value} (0x{clp_value:04X}) → addr {write_addr}")

        # CONFIABILIDADE: 5 tentativas com delay crescente
        MAX_RETRIES = 5
        RETRY_DELAYS = [0.05, 0.1, 0.2, 0.3, 0.5]  # 50ms, 100ms, 200ms, 300ms, 500ms

        for attempt in range(MAX_RETRIES):
            # Tenta escrever
            success = self.write_register(write_addr, clp_value)

            if not success:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    print(f"  ⚠️ Escrita falhou (tentativa {attempt + 1}/{MAX_RETRIES}), retry em {delay*1000:.0f}ms...")
                    time.sleep(delay)
                continue

            # Escrita OK - agora verifica se o CLP recebeu corretamente
            if verify:
                # Aguarda ladder copiar de 0x0A00+ para 0x0842+
                time.sleep(0.15)  # 150ms para sincronização do ladder

                # Lê de volta para verificar
                value_read = self.read_register(read_addr)

                if value_read is None:
                    print(f"  ⚠️ Verificação falhou (não conseguiu ler addr {read_addr})")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAYS[attempt])
                    continue

                # Tolerância de ±2 unidades (erros de arredondamento)
                if abs(value_read - clp_value) <= 2:
                    print(f"  ✓ Dobra {bend_number} CONFIRMADA: gravado {clp_value}, lido {value_read} (OK)")
                    if attempt > 0:
                        print(f"    (sucesso na tentativa {attempt + 1}/{MAX_RETRIES})")
                    return True
                else:
                    print(f"  ❌ DISCREPÂNCIA! Gravado {clp_value}, lido {value_read} (diff={abs(value_read - clp_value)})")
                    # Tenta novamente
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAYS[attempt])
                    continue
            else:
                # Sem verificação - assume sucesso
                print(f"  ✓ Dobra {bend_number} gravada: {degrees}° = {clp_value} (sem verificação)")
                return True

        print(f"  ✗ FALHA CRÍTICA: Dobra {bend_number} não confirmada após {MAX_RETRIES} tentativas!")
        print(f"    Ação recomendada: Verificar conexão Modbus e cabo RS485")
        return False

    def read_bend_angle(self, bend_number: int) -> Optional[float]:
        """
        Lê ângulo REAL de dobra diretamente dos registros de escrita.

        CORRIGIDO 08/Fev/2026: Lê dos endereços de ESCRITA (0x0A00+)
        Os endereços antigos (0x0842+) dependiam do ladder copiar e retornavam 0.
        Holding registers são R/W, lemos de onde escrevemos.

        Conversão: valor_disco / 2 = ângulo real

        Endereços (DECIMAL):
          - Dobra 1: 2560 (0x0A00)
          - Dobra 2: 2562 (0x0A02)
          - Dobra 3: 2564 (0x0A04)

        Args:
            bend_number (int): 1, 2 ou 3

        Returns:
            float: Ângulo REAL da dobra, ou None se erro

        Exemplo:
            >>> angle = client.read_bend_angle(1)
            >>> print(f"Dobra 1: {angle}° real")
            📖 Lendo Dobra 1 de endereço 2114: 512 (0x0200) → 90.0°
            Dobra 1: 90.0°
        """
        # Mapeamento: Endereços de LEITURA (DECIMAL)
        addresses = {
            1: mm.BEND_ANGLES['ANGULO_1_READ'],  # 2114 (0x0842)
            2: mm.BEND_ANGLES['ANGULO_2_READ'],  # 2116 (0x0844)
            3: mm.BEND_ANGLES['ANGULO_3_READ'],  # 2118 (0x0846)
        }

        if bend_number not in addresses:
            print(f"✗ Número de dobra inválido: {bend_number}")
            return None

        addr = addresses[bend_number]

        # Ler 16-bit (1 registro) - valor em escala 0-2048
        clp_value = self.read_register(addr)

        if clp_value is None:
            return None

        # Converter valor CLP para ângulo REAL
        real_angle = mm.clp_to_real_angle(clp_value)

        print(f"📖 Lendo Dobra {bend_number} de endereço {addr}: {clp_value} (0x{clp_value:04X}) → {real_angle:.1f}°")

        return real_angle

    def read_all_bend_angles(self) -> dict:
        """
        Lê todos os 3 ângulos de dobra de uma vez

        Returns:
            dict: {'bend_1': 90.0, 'bend_2': 120.0, 'bend_3': 45.0}

        Exemplo:
            >>> angles = client.read_all_bend_angles()
            >>> print(angles)
            {'bend_1': 90.0, 'bend_2': 120.0, 'bend_3': 45.0}
        """
        return {
            'bend_1': self.read_bend_angle(1),
            'bend_2': self.read_bend_angle(2),
            'bend_3': self.read_bend_angle(3)
        }

    def write_speed_class(self, rpm: int) -> bool:
        """
        Muda a classe de velocidade da máquina

        ✅ VALIDADO 20/Nov/2025 - Conversão via ladder ROT2
        Escreve em 0x0A02, lê de 0x06E0

        Args:
            rpm (int): Velocidade desejada (5, 10 ou 15)

        Returns:
            bool: True se sucesso

        Conversão automática:
            5 RPM  → escreve 1319 (0x0527)
            10 RPM → escreve 4181 (0x1055)
            15 RPM → escreve 5507 (0x1583)

        Exemplo:
            >>> client.write_speed_class(5)   # 5 rpm
            True
            >>> client.write_speed_class(15)  # 15 rpm
            True
        """
        if rpm not in [5, 10, 15]:
            print(f"✗ Velocidade inválida: {rpm} (deve ser 5, 10 ou 15)")
            return False

        # Converte RPM para valor do registro (ladder ROT2)
        register_value = mm.rpm_to_register(rpm)

        print(f"⚡ Mudando velocidade para {rpm} rpm (escrevendo {register_value} / 0x{register_value:04X})...")

        # VALIDADO: Escrita em 0x0A02 (RPM_WRITE) com conversão
        return self.write_register(mm.RPM_REGISTERS['RPM_WRITE'], register_value)

    def read_speed_class(self) -> Optional[int]:
        """
        Lê a classe de velocidade atual

        ✅ VALIDADO 20/Nov/2025 - Lê de 0x06E0 (inversor) + conversão via ladder ROT2

        Returns:
            int: 5, 10 ou 15 (rpm), ou None se erro

        Conversão:
            Registro 1319 (0x0527) → 5 RPM
            Registro 4181 (0x1055) → 10 RPM
            Registro 5507 (0x1583) → 15 RPM

        Exemplo:
            >>> speed = client.read_speed_class()
            >>> print(f"Velocidade: {speed} rpm")
            Velocidade: 10 rpm
        """
        # Lê valor bruto do registro
        register_value = self.read_register(mm.RPM_REGISTERS['RPM_READ'])

        if register_value is None:
            return None

        # Converte valor do registro para RPM usando função de conversão
        rpm = mm.register_to_rpm(register_value)
        return rpm

    # ==========================================
    # CONTROLE DE MOTOR - BOTÕES DE PAINEL
    # ==========================================

    def start_forward(self) -> bool:
        """
        AVANÇAR - Seta flag 0x0385 no CLP (CCW).

        ✅ ATUALIZADO 28/Nov/2025 - Usa flags dedicados do ladder
        Antes de ativar FORWARD, desativa BACKWARD.

        Endereços:
          FORWARD:  0x0385 (901) -> ON
          BACKWARD: 0x0386 (902) -> OFF

        Returns:
            bool: True se sucesso
        """
        if self.stub_mode:
            print("🟢 [STUB] AVANÇAR ativado (0x0385=ON)")
            return True

        try:
            # 1. Desativa BACKWARD primeiro
            self.write_coil(mm.PANEL_BUTTONS['BACKWARD'], False)  # 0x0386 OFF

            # 2. Ativa FORWARD
            success = self.write_coil(mm.PANEL_BUTTONS['FORWARD'], True)  # 0x0385 ON

            if success:
                print("✅ AVANÇAR: 0x0385=ON (0x0386=OFF)")
            else:
                print("❌ AVANÇAR: Falha ao ativar 0x0385")

            return success
        except Exception as e:
            print(f"❌ Erro em start_forward: {e}")
            return False

    def start_backward(self) -> bool:
        """
        RECUAR - Seta flag 0x0386 no CLP (CW).

        ✅ ATUALIZADO 28/Nov/2025 - Usa flags dedicados do ladder
        Antes de ativar BACKWARD, desativa FORWARD.

        Endereços:
          FORWARD:  0x0385 (901) -> OFF
          BACKWARD: 0x0386 (902) -> ON

        Returns:
            bool: True se sucesso
        """
        if self.stub_mode:
            print("🟢 [STUB] RECUAR ativado (0x0386=ON)")
            return True

        try:
            # 1. Desativa FORWARD primeiro
            self.write_coil(mm.PANEL_BUTTONS['FORWARD'], False)  # 0x0385 OFF

            # 2. Ativa BACKWARD
            success = self.write_coil(mm.PANEL_BUTTONS['BACKWARD'], True)  # 0x0386 ON

            if success:
                print("✅ RECUAR: 0x0386=ON (0x0385=OFF)")
            else:
                print("❌ RECUAR: Falha ao ativar 0x0386")

            return success
        except Exception as e:
            print(f"❌ Erro em start_backward: {e}")
            return False

    def stop_motor(self) -> bool:
        """
        PARADA - Desativa flags 0x0385 e 0x0386 no CLP.

        ✅ ATUALIZADO 28/Nov/2025 - Apenas desativa FORWARD e BACKWARD
        Não usa flag próprio, apenas desliga os dois comandos de movimento.

        Endereços:
          FORWARD:  0x0385 (901) -> OFF
          BACKWARD: 0x0386 (902) -> OFF

        Returns:
            bool: True se sucesso
        """
        if self.stub_mode:
            print("🛑 [STUB] MOTOR parado (0x0385=OFF, 0x0386=OFF)")
            return True

        try:
            # Desativa ambos os comandos de movimento
            fwd_off = self.write_coil(mm.PANEL_BUTTONS['FORWARD'], False)   # 0x0385 OFF
            bwd_off = self.write_coil(mm.PANEL_BUTTONS['BACKWARD'], False)  # 0x0386 OFF

            if fwd_off and bwd_off:
                print("✅ PARADA: 0x0385=OFF, 0x0386=OFF")
            else:
                print(f"⚠️ PARADA parcial: 0x0385={'OFF' if fwd_off else 'ERRO'}, 0x0386={'OFF' if bwd_off else 'ERRO'}")

            return fwd_off and bwd_off
        except Exception as e:
            print(f"❌ Erro em stop_motor: {e}")
            return False

    def read_panel_buttons(self) -> dict:
        """
        Lê estado dos botões físicos do painel (E2, E3, E4, E5).

        ✅ CORRIGIDO 20/Nov/2025 - Adiciona E5 (sensor)
        Útil para feedback visual na IHM.

        Returns:
            dict: Estado dos botões físicos (True = pressionado)

        Exemplo:
            >>> buttons = client.read_panel_buttons()
            >>> print(buttons)
            {'forward': False, 'stop': False, 'backward': False, 'sensor': False}
        """
        if self.stub_mode:
            return {
                'forward': False,
                'stop': False,
                'backward': False,
                'sensor': False,
            }

        try:
            # Lê entradas digitais dos botões físicos
            forward_input = self.read_coil(mm.PANEL_BUTTONS['FORWARD_INPUT'])
            stop_input = self.read_coil(mm.PANEL_BUTTONS['STOP_INPUT'])
            backward_input = self.read_coil(mm.PANEL_BUTTONS['BACKWARD_INPUT'])
            sensor_input = self.read_coil(mm.PANEL_BUTTONS['SENSOR_INPUT'])

            return {
                'forward': forward_input if forward_input is not None else False,
                'stop': stop_input if stop_input is not None else False,
                'backward': backward_input if backward_input is not None else False,
                'sensor': sensor_input if sensor_input is not None else False,
            }
        except Exception as e:
            print(f"❌ Erro lendo botões do painel: {e}")
            return {'forward': False, 'stop': False, 'backward': False, 'sensor': False}

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

    # Ler ângulos usando novos métodos
    print("\n=== TESTANDO NOVOS MÉTODOS DE ÂNGULOS ===")
    angles = client.read_all_bend_angles()
    print(f"Todos ângulos: {angles}")

    # Gravar ângulos
    print("\nGravando novos ângulos...")
    client.write_bend_angle(1, 135.5)
    client.write_bend_angle(2, 45.0)
    client.write_bend_angle(3, 180.0)

    # Ler de volta
    print("\nLendo de volta:")
    for i in [1, 2, 3]:
        angle = client.read_bend_angle(i)
        print(f"  Dobra {i}: {angle}°")

    # Ler LEDs
    leds = client.read_leds()
    print(f"LEDs: {leds}")

    # Simular botão K1
    print("Pressionando K1...")
    client.press_key(mm.KEYBOARD_NUMERIC['K1'])

    # Escrever número da tela
    print("Escrevendo tela 4 em supervisão...")
    client.write_screen_number(4)

    # Alterar velocidade (método antigo - K1+K7)
    print("\n=== TESTANDO MUDANÇA DE VELOCIDADE (ANTIGO) ===")
    print("Alterando velocidade (K1+K7)...")
    client.change_speed_class()

    # Testar novos métodos de velocidade
    print("\n=== TESTANDO MUDANÇA DE VELOCIDADE (NOVO) ===")
    current_speed = client.read_speed_class()
    print(f"Velocidade atual: {current_speed} rpm")

    print("\nMudando para 5 rpm...")
    client.write_speed_class(5)
    print(f"Nova velocidade: {client.read_speed_class()} rpm")

    print("\nMudando para 15 rpm...")
    client.write_speed_class(15)
    print(f"Nova velocidade: {client.read_speed_class()} rpm")

    print("\nRestaurando 10 rpm...")
    client.write_speed_class(10)
    print(f"Velocidade final: {client.read_speed_class()} rpm")

    client.close()
