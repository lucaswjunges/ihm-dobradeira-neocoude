"""
Mapeamento de bits e registros Modbus para o CLP ATOS MPC4004
Interface com dobradeira NEOCOUDE-HD-15

Usar este arquivo como referência para o servidor Python (modbus_map.py)
"""

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO MODBUS RTU
# ══════════════════════════════════════════════════════════════════════════════

MODBUS_CONFIG = {
    'port': '/dev/ttyUSB0',  # ou /dev/ttyUSB1 (ajustar conforme sistema)
    'baudrate': 57600,
    'bytesize': 8,
    'parity': 'N',  # None
    'stopbits': 1,
    'timeout': 1.0,
    'slave_address': 1,  # Verificar no registro 1988H (6536 dec) do CLP
}

# ══════════════════════════════════════════════════════════════════════════════
# COMANDOS - ESCREVER VIA MODBUS (Function Code 0x05 - Force Single Coil)
# ══════════════════════════════════════════════════════════════════════════════

COMANDOS_MODBUS = {
    # Botões do painel da máquina
    'MB_BTN_AVANCAR':  {'address': 992,  'hex': '0x03E0', 'desc': 'Botão AVANÇAR (CCW)'},
    'MB_BTN_RECUAR':   {'address': 993,  'hex': '0x03E1', 'desc': 'Botão RECUAR (CW)'},
    'MB_BTN_PARADA':   {'address': 994,  'hex': '0x03E2', 'desc': 'Botão PARADA'},

    # Teclas HMI
    'MB_S1_CMD':       {'address': 995,  'hex': '0x03E3', 'desc': 'Tecla S1 (mudança modo)'},

    # Mudança de modo
    'MB_MODO_AUTO':    {'address': 997,  'hex': '0x03E5', 'desc': 'Força modo AUTOMÁTICO'},
    'MB_MODO_MANUAL':  {'address': 998,  'hex': '0x03E6', 'desc': 'Força modo MANUAL'},
}

# ══════════════════════════════════════════════════════════════════════════════
# STATUS - LER VIA MODBUS (Function Code 0x01 - Read Coil Status)
# ══════════════════════════════════════════════════════════════════════════════

STATUS_BITS = {
    # Sistema
    'MODBUS_SLAVE_ON': {'address': 190,  'hex': '0x00BE', 'desc': 'Modbus Slave ativo (DEVE=1)'},
    'INTERFACE_OK':    {'address': 1023, 'hex': '0x03FF', 'desc': 'Interface Modbus OK'},

    # Modos de operação (a confirmar com lógica original)
    'MODO_MANUAL':     {'address': 400,  'hex': '0x0190', 'desc': 'Modo MANUAL ativo'},
    'MODO_AUTO':       {'address': 401,  'hex': '0x0191', 'desc': 'Modo AUTOMÁTICO ativo'},

    # Segurança
    'SEM_EMERGENCIA':  {'address': 767,  'hex': '0x02FF', 'desc': 'Sistema não em emergência'},
}

# Entradas digitais E0-E7 (256-263)
ENTRADAS_DIGITAIS = {
    'E0': {'address': 256, 'hex': '0x0100', 'desc': 'Entrada digital E0'},
    'E1': {'address': 257, 'hex': '0x0101', 'desc': 'Entrada digital E1'},
    'E2': {'address': 258, 'hex': '0x0102', 'desc': 'Entrada E2 - AVANÇAR'},
    'E3': {'address': 259, 'hex': '0x0103', 'desc': 'Entrada E3 - PARADA'},
    'E4': {'address': 260, 'hex': '0x0104', 'desc': 'Entrada E4 - RECUAR'},
    'E5': {'address': 261, 'hex': '0x0105', 'desc': 'Entrada digital E5'},
    'E6': {'address': 262, 'hex': '0x0106', 'desc': 'Entrada digital E6'},
    'E7': {'address': 263, 'hex': '0x0107', 'desc': 'Entrada digital E7'},
}

# Saídas digitais S0-S7 (384-391)
SAIDAS_DIGITAIS = {
    'S0': {'address': 384, 'hex': '0x0180', 'desc': 'Saída digital S0'},
    'S1': {'address': 385, 'hex': '0x0181', 'desc': 'Saída digital S1'},
    'S2': {'address': 386, 'hex': '0x0182', 'desc': 'Saída digital S2'},
    'S3': {'address': 387, 'hex': '0x0183', 'desc': 'Saída digital S3'},
    'S4': {'address': 388, 'hex': '0x0184', 'desc': 'Saída digital S4'},
    'S5': {'address': 389, 'hex': '0x0185', 'desc': 'Saída digital S5'},
    'S6': {'address': 390, 'hex': '0x0186', 'desc': 'Saída digital S6'},
    'S7': {'address': 391, 'hex': '0x0187', 'desc': 'Saída digital S7'},
}

# ══════════════════════════════════════════════════════════════════════════════
# REGISTROS - LER VIA MODBUS (Function Code 0x03 - Read Holding Registers)
# ══════════════════════════════════════════════════════════════════════════════

REGISTROS_LEITURA = {
    # Encoder (32-bit - ler 2 registros consecutivos)
    'ENCODER_MSW':     {'address': 1238, 'hex': '0x04D6', 'desc': 'Encoder MSW (bits 31-16)'},
    'ENCODER_LSW':     {'address': 1239, 'hex': '0x04D7', 'desc': 'Encoder LSW (bits 15-0)'},

    # Entradas digitais como registros (16-bit, usar bit 0)
    'REG_E0':          {'address': 256, 'hex': '0x0100', 'desc': 'Entrada E0 (bit 0)'},
    'REG_E1':          {'address': 257, 'hex': '0x0101', 'desc': 'Entrada E1 (bit 0)'},
    'REG_E2':          {'address': 258, 'hex': '0x0102', 'desc': 'Entrada E2 (bit 0)'},
    'REG_E3':          {'address': 259, 'hex': '0x0103', 'desc': 'Entrada E3 (bit 0)'},
    'REG_E4':          {'address': 260, 'hex': '0x0104', 'desc': 'Entrada E4 (bit 0)'},
    'REG_E5':          {'address': 261, 'hex': '0x0105', 'desc': 'Entrada E5 (bit 0)'},
    'REG_E6':          {'address': 262, 'hex': '0x0106', 'desc': 'Entrada E6 (bit 0)'},
    'REG_E7':          {'address': 263, 'hex': '0x0107', 'desc': 'Entrada E7 (bit 0)'},

    # Saídas digitais como registros (16-bit, usar bit 0)
    'REG_S0':          {'address': 384, 'hex': '0x0180', 'desc': 'Saída S0 (bit 0)'},
    'REG_S1':          {'address': 385, 'hex': '0x0181', 'desc': 'Saída S1 (bit 0)'},
    'REG_S2':          {'address': 386, 'hex': '0x0182', 'desc': 'Saída S2 (bit 0)'},
    'REG_S3':          {'address': 387, 'hex': '0x0183', 'desc': 'Saída S3 (bit 0)'},
    'REG_S4':          {'address': 388, 'hex': '0x0184', 'desc': 'Saída S4 (bit 0)'},
    'REG_S5':          {'address': 389, 'hex': '0x0185', 'desc': 'Saída S5 (bit 0)'},
    'REG_S6':          {'address': 390, 'hex': '0x0186', 'desc': 'Saída S6 (bit 0)'},
    'REG_S7':          {'address': 391, 'hex': '0x0187', 'desc': 'Saída S7 (bit 0)'},
}

# ══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES
# ══════════════════════════════════════════════════════════════════════════════

def ler_encoder_32bit(cliente_modbus, slave_addr=1):
    """
    Lê o valor do encoder como 32-bit

    O encoder usa 2 registros consecutivos:
    - 04D6 (1238 dec) = MSW (bits 31-16)
    - 04D7 (1239 dec) = LSW (bits 15-0)

    Valor final = (MSW << 16) | LSW
    """
    try:
        # Ler 2 registros a partir do endereço 1238
        resultado = cliente_modbus.read_holding_registers(1238, 2, slave=slave_addr)

        if resultado.isError():
            return None

        msw = resultado.registers[0]  # Registro 1238
        lsw = resultado.registers[1]  # Registro 1239

        # Combinar em 32-bit
        valor_32bit = (msw << 16) | lsw

        return valor_32bit

    except Exception as e:
        print(f"Erro ao ler encoder: {e}")
        return None


def simular_botao_modbus(cliente_modbus, bit_address, slave_addr=1, hold_time_ms=100):
    """
    Simula pressionamento de botão via Modbus

    Sequência:
    1. Escreve bit = 1 (ON)
    2. Aguarda hold_time_ms
    3. Escreve bit = 0 (OFF)

    Args:
        cliente_modbus: Cliente pymodbus
        bit_address: Endereço do bit (ex: 992 para AVANÇAR)
        slave_addr: Endereço Modbus do CLP
        hold_time_ms: Tempo em milissegundos (padrão 100ms)
    """
    import time

    try:
        # Passo 1: Ativar bit
        resultado = cliente_modbus.write_coil(bit_address, True, slave=slave_addr)
        if resultado.isError():
            print(f"Erro ao ativar bit {bit_address}")
            return False

        # Passo 2: Aguardar
        time.sleep(hold_time_ms / 1000.0)

        # Passo 3: Desativar bit
        resultado = cliente_modbus.write_coil(bit_address, False, slave=slave_addr)
        if resultado.isError():
            print(f"Erro ao desativar bit {bit_address}")
            return False

        return True

    except Exception as e:
        print(f"Erro ao simular botão: {e}")
        return False


def ler_entrada_digital(cliente_modbus, numero_entrada, slave_addr=1):
    """
    Lê o estado de uma entrada digital (E0-E7)

    Args:
        numero_entrada: 0-7

    Returns:
        True/False ou None em caso de erro
    """
    try:
        address = 256 + numero_entrada  # E0=256, E1=257, etc

        # Pode usar Read Coil (FC 0x01) ou Read Holding Register (FC 0x03)
        # Usando Read Coil:
        resultado = cliente_modbus.read_coils(address, 1, slave=slave_addr)

        if resultado.isError():
            return None

        return resultado.bits[0]

    except Exception as e:
        print(f"Erro ao ler entrada E{numero_entrada}: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# EXEMPLO DE USO
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from pymodbus.client import ModbusSerialClient

    # Conectar ao CLP
    cliente = ModbusSerialClient(
        port=MODBUS_CONFIG['port'],
        baudrate=MODBUS_CONFIG['baudrate'],
        bytesize=MODBUS_CONFIG['bytesize'],
        parity=MODBUS_CONFIG['parity'],
        stopbits=MODBUS_CONFIG['stopbits'],
        timeout=MODBUS_CONFIG['timeout']
    )

    if not cliente.connect():
        print("Erro ao conectar no CLP!")
        exit(1)

    print("Conectado ao CLP ATOS MPC4004")

    # Verificar se Modbus está ativo
    resultado = cliente.read_coils(190, 1, slave=1)  # Bit 00BE
    if not resultado.isError():
        modbus_ativo = resultado.bits[0]
        print(f"Modbus Slave ativo: {modbus_ativo}")
        if not modbus_ativo:
            print("AVISO: Bit 00BE está OFF! Aguarde 120s após power-on do CLP.")

    # Ler encoder
    encoder = ler_encoder_32bit(cliente, slave_addr=1)
    if encoder is not None:
        print(f"Encoder value: {encoder}")

    # Ler entrada E2 (botão AVANÇAR)
    e2_status = ler_entrada_digital(cliente, 2, slave_addr=1)
    if e2_status is not None:
        print(f"Entrada E2 (AVANÇAR): {'PRESSIONADO' if e2_status else 'SOLTO'}")

    # Exemplo: Simular pressionamento do botão AVANÇAR via Modbus
    # CUIDADO: Só execute se máquina estiver em condições seguras!
    # print("Simulando botão AVANÇAR...")
    # simular_botao_modbus(cliente, COMANDOS_MODBUS['MB_BTN_AVANCAR']['address'])

    cliente.close()
    print("Desconectado")
