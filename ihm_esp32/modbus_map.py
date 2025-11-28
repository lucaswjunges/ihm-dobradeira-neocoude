#!/usr/bin/env python3
"""
Mapeamento Modbus - CLP Atos MPC4004
Versao: 3.0 (Novo Ladder - Maquina de Estados)
Data: 27 de Novembro de 2025

Este arquivo centraliza TODOS os enderecos Modbus para o novo programa ladder
baseado em maquina de estados com 8 estados distintos.

Referencia: PROJETO_LADDER_NOVO.md
"""

# ==========================================
# ESTADOS DA MAQUINA (Coils M000-M007)
# ==========================================
# Apenas UM estado deve estar ativo por vez

MACHINE_STATES = {
    'ST_IDLE':            0x0300,  # 768 - Maquina parada, aguardando
    'ST_AGUARDA_DIRECAO': 0x0301,  # 769 - Aguardando pedal para definir sentido
    'ST_DOBRANDO':        0x0302,  # 770 - Executando dobra (motor ligado)
    'ST_RETORNANDO':      0x0303,  # 771 - Retornando para posicao zero
    'ST_AGUARDA_PROXIMA': 0x0304,  # 772 - Aguardando pedal para proxima dobra
    'ST_COMPLETO':        0x0305,  # 773 - Sequencia de 3 dobras completa
    'ST_EMERGENCIA':      0x0306,  # 774 - Emergencia ativa
    'ST_MANUAL':          0x0307,  # 775 - Modo manual ativo
}

# Descricoes amigaveis dos estados (para exibir na IHM)
STATE_DESCRIPTIONS = {
    0x0300: {
        'name': 'PARADA',
        'description': 'Maquina parada. Pressione o pedal para iniciar.',
        'color': 'gray',
        'icon': '⏸️',
    },
    0x0301: {
        'name': 'AGUARDANDO DIRECAO',
        'description': 'Pressione AVANCO ou RECUO para definir o sentido da dobra.',
        'color': 'yellow',
        'icon': '↔️',
    },
    0x0302: {
        'name': 'DOBRANDO',
        'description': 'Executando dobra... Motor em movimento.',
        'color': 'green',
        'icon': '🔄',
    },
    0x0303: {
        'name': 'RETORNANDO',
        'description': 'Retornando para posicao zero...',
        'color': 'blue',
        'icon': '↩️',
    },
    0x0304: {
        'name': 'AGUARDANDO PROXIMA',
        'description': 'Dobra concluida. Pressione o pedal para proxima dobra.',
        'color': 'cyan',
        'icon': '⏭️',
    },
    0x0305: {
        'name': 'CICLO COMPLETO',
        'description': '3 dobras concluidas! Peca finalizada.',
        'color': 'lime',
        'icon': '✅',
    },
    0x0306: {
        'name': 'EMERGENCIA',
        'description': 'PARADA DE EMERGENCIA! Destravar botao para continuar.',
        'color': 'red',
        'icon': '🚨',
    },
    0x0307: {
        'name': 'MANUAL',
        'description': 'Modo manual ativo. Motor gira enquanto pedal pressionado.',
        'color': 'orange',
        'icon': '🔧',
    },
}

# ==========================================
# BITS DE CONTROLE (Coils B000-B007)
# ==========================================

CONTROL_BITS = {
    'DIR_AVANCO':      0x0380,  # 896 - Direcao definida = Avanco (CCW)
    'DIR_RECUO':       0x0381,  # 897 - Direcao definida = Recuo (CW)
    'MODO_AUTO':       0x0382,  # 898 - Modo automatico ativo
    'MODO_MANUAL':     0x0383,  # 899 - Modo manual ativo
    'PEDAL_SEGURA':    0x0384,  # 900 - Exige segurar pedal para movimento
    'NA_POSICAO_ZERO': 0x0385,  # 901 - Encoder esta na posicao zero
    'ATINGIU_ANGULO':  0x0386,  # 902 - Atingiu angulo alvo
    'HABILITADO':      0x0387,  # 903 - Sistema habilitado (sem emergencia)
}

# ==========================================
# BITS AUXILIARES (Deteccao de Borda)
# ==========================================

AUXILIARY_BITS = {
    'PEDAL_AV_ANT':    0x0390,  # 912 - Estado anterior do pedal avanco
    'PEDAL_RC_ANT':    0x0391,  # 913 - Estado anterior do pedal recuo
    'BORDA_AV':        0x0392,  # 914 - Borda de subida pedal avanco
    'BORDA_RC':        0x0393,  # 915 - Borda de subida pedal recuo
    'SENSOR_ZERO_ANT': 0x0394,  # 916 - Estado anterior sensor zero
    'BORDA_ZERO':      0x0395,  # 917 - Borda de subida sensor zero
}

# ==========================================
# ENTRADAS DIGITAIS (E0-E7)
# ==========================================

DIGITAL_INPUTS = {
    'E0': 0x0100,  # 256 - Sensor de posicao ZERO (NA)
    'E1': 0x0101,  # 257 - Reserva / Sensor carenagem
    'E2': 0x0102,  # 258 - PEDAL AVANCO (CCW) (NA)
    'E3': 0x0103,  # 259 - PEDAL PARADA (NA)
    'E4': 0x0104,  # 260 - PEDAL RECUO (CW) (NA)
    'E5': 0x0105,  # 261 - Sensor de seguranca/carenagem (NF)
    'E6': 0x0106,  # 262 - BOTAO EMERGENCIA (NF)
    'E7': 0x0107,  # 263 - Reserva
}

# Descricoes das entradas
INPUT_DESCRIPTIONS = {
    'E0': 'Sensor Posicao Zero',
    'E2': 'Pedal Avanco (CCW)',
    'E3': 'Pedal Parada',
    'E4': 'Pedal Recuo (CW)',
    'E5': 'Sensor Seguranca',
    'E6': 'Botao Emergencia',
}

# ==========================================
# SAIDAS DIGITAIS (S0-S7)
# ==========================================

DIGITAL_OUTPUTS = {
    'S0': 0x0180,  # 384 - Contator AVANCO (motor CCW)
    'S1': 0x0181,  # 385 - Contator RECUO (motor CW)
    'S2': 0x0182,  # 386 - Habilita inversor
    'S3': 0x0183,  # 387 - Reserva / Sinalizador
    'S4': 0x0184,  # 388 - LED Dobra 1
    'S5': 0x0185,  # 389 - LED Dobra 2
    'S6': 0x0186,  # 390 - LED Dobra 3
    'S7': 0x0187,  # 391 - Reserva
}

# ==========================================
# ENCODER / POSICAO ANGULAR (32-bit MSW+LSW)
# ==========================================

ENCODER = {
    'ANGLE_MSW': 0x04D6,  # 1238 - Posicao angular (bits 31-16)
    'ANGLE_LSW': 0x04D7,  # 1239 - Posicao angular (bits 15-0)
}

# ==========================================
# ANGULOS PROGRAMADOS (16-bit)
# ==========================================
# Unidade: 0.1 grau (900 = 90.0 graus)
# CORRIGIDO 27/Nov/2025: Mapeamento conforme novo ladder
#
# Fluxo: IHM escreve em 0x0A00+ → Ladder copia para 0x0842+
#   0x0A00 → 0x0842 (Angulo 1)
#   0x0A02 → 0x0844 (Angulo 2)
#   0x0A04 → 0x0846 (Angulo 3)
#   0x0A06 → 0x06E0 (Velocidade RPM)

BEND_ANGLES = {
    # Enderecos de LEITURA (onde o CLP armazena os valores)
    'ANGULO_1_READ': 0x0842,  # 2114 - Angulo dobra 1 (leitura)
    'ANGULO_2_READ': 0x0844,  # 2116 - Angulo dobra 2 (leitura)
    'ANGULO_3_READ': 0x0846,  # 2118 - Angulo dobra 3 (leitura)

    # Enderecos de ESCRITA (onde a IHM escreve)
    'ANGULO_1_WRITE': 0x0A00,  # 2560 - Angulo dobra 1 (escrita)
    'ANGULO_2_WRITE': 0x0A02,  # 2562 - Angulo dobra 2 (escrita)
    'ANGULO_3_WRITE': 0x0A04,  # 2564 - Angulo dobra 3 (escrita)
}

# ==========================================
# REGISTROS DE TRABALHO (16-bit)
# ==========================================

WORK_REGISTERS = {
    # Constantes
    'NUMERO0':     0x0900,  # 2304 - Valor = 0
    'NUMERO1':     0x0902,  # 2306 - Valor = 1
    'NUMERO2':     0x0904,  # 2308 - Valor = 2
    'MAX_DOBRAS':  0x0906,  # 2310 - Valor = 3
    'NUMERO4':     0x0908,  # 2312 - Valor = 4
    'NUMERO5':     0x0910,  # 2320 - Valor = 5
    'NUMERO6':     0x0912,  # 2322 - Valor = 6
    'NUMERO7':     0x0914,  # 2324 - Valor = 7

    # Variaveis de processo
    'VELOCIDADE_ATUAL': 0x0916,  # 2326 - Classe de velocidade (1, 2 ou 3)
    'DOBRA_ATUAL':      0x0918,  # 2328 - Numero da dobra atual (1, 2 ou 3)
    'CONTADOR_PECAS':   0x0920,  # 2336 - Contador de pecas produzidas
    'ESTADO_ANTERIOR':  0x0922,  # 2338 - Estado anterior (para transicoes)
    'ESTADO_ATUAL':     0x0924,  # 2340 - Estado atual (0-7)
}

# ==========================================
# INVERSOR / VELOCIDADE
# ==========================================
# Saida analogica para inversor: 0x06E0 (1760)
# Valores de referencia (conforme manual):
#   0 RPM   = 0      (0x0000)
#   5 RPM   = 527    (0x020F)
#   10 RPM  = 1055   (0x041F)
#   15 RPM  = 1583   (0x062F)
#   ~19 RPM = 2000   (0x07D0) - MAXIMO conforme manual
# Formula: valor = rpm * 105.533 (1583/15)

INVERTER = {
    'VELOCIDADE_INVERSOR': 0x06E0,  # 1760 - Saida analogica para inversor (LEITURA)
    'VELOCIDADE_WRITE': 0x0A06,     # 2566 - Endereco de escrita (IHM -> Ladder -> 0x06E0)
}

# Valores pre-calculados para RPM
RPM_VALUES = {
    0:  0,
    5:  527,
    10: 1055,
    15: 1583,
    19: 2000,  # Maximo conforme manual
}

# Fator de conversao RPM -> valor do registro (1583/15 = 105.533...)
RPM_FACTOR = 1583.0 / 15.0  # = 105.5333...

# Limites
RPM_MAX = 19.0      # ~2000 no CLP
REGISTER_MAX = 2000  # Maximo conforme manual

# ==========================================
# BOTOES / TECLADO (Coils para simulacao)
# ==========================================

KEYBOARD_NUMERIC = {
    'K1': 0x00A0,  # 160
    'K2': 0x00A1,  # 161
    'K3': 0x00A2,  # 162
    'K4': 0x00A3,  # 163
    'K5': 0x00A4,  # 164
    'K6': 0x00A5,  # 165
    'K7': 0x00A6,  # 166
    'K8': 0x00A7,  # 167
    'K9': 0x00A8,  # 168
    'K0': 0x00A9,  # 169
}

KEYBOARD_FUNCTION = {
    'S1':        0x00DC,  # 220
    'S2':        0x00DD,  # 221
    'ARROW_UP':  0x00AC,  # 172
    'ARROW_DOWN': 0x00AD,  # 173
    'ESC':       0x00BC,  # 188
    'ENTER':     0x0025,  # 37
    'EDIT':      0x0026,  # 38
    'LOCK':      0x00F1,  # 241
}

# ==========================================
# LEDS (Coils)
# ==========================================

LEDS = {
    'LED1': 0x00C0,  # 192 - Dobra 1 ativa
    'LED2': 0x00C1,  # 193 - Dobra 2 ativa
    'LED3': 0x00C2,  # 194 - Dobra 3 ativa
    'LED4': 0x00C3,  # 195 - Sentido Esquerda
    'LED5': 0x00C4,  # 196 - Sentido Direita
}

# ==========================================
# ESTADOS CRITICOS
# ==========================================

CRITICAL_STATES = {
    'MODBUS_SLAVE_ENABLED': 0x00BE,  # 190 - DEVE estar ON para Modbus funcionar
}

# ==========================================
# CONFIGURACAO MODBUS
# ==========================================

MODBUS_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 57600,
    'parity': 'N',
    'stopbits': 2,
    'bytesize': 8,
    'timeout': 1.0,
    'slave_id': 1,
}

# ==========================================
# FUNCOES AUXILIARES
# ==========================================

def read_32bit(msw: int, lsw: int) -> int:
    """Combina MSW e LSW em valor 32-bit."""
    if msw is None or lsw is None:
        return None
    return (msw << 16) | lsw


def split_32bit(value: int) -> tuple:
    """Divide valor 32-bit em MSW e LSW."""
    msw = (value >> 16) & 0xFFFF
    lsw = value & 0xFFFF
    return (msw, lsw)


def clp_to_degrees(clp_value: int) -> float:
    """
    Converte valor CLP para graus.
    Valor CLP esta em decimos de grau (900 = 90.0 graus).
    Aplica MOD 360 para mostrar angulo atual dentro de uma volta.

    NOTA: O encoder e acumulativo e pode ter valores muito grandes.
    Usamos MOD 3600 (360.0 graus * 10) para normalizar.
    """
    if clp_value is None:
        return 0.0

    # Normaliza para dentro de 360 graus antes de converter
    # O CLP usa decimos de grau, entao 3600 = 360.0 graus
    normalized = clp_value % 3600
    degrees = normalized / 10.0

    return degrees


def degrees_to_clp(degrees: float) -> int:
    """Converte graus para valor CLP (decimos de grau)."""
    return int(degrees * 10)


def rpm_to_register(rpm: float) -> int:
    """
    Converte RPM para valor do registro do inversor.

    Valores de referencia (EXATOS conforme manual):
      0 RPM  = 0    (0x0000)
      5 RPM  = 527  (0x020F)
      10 RPM = 1055 (0x041F)
      15 RPM = 1583 (0x062F)
      19 RPM = 2000 (0x07D0) - MAXIMO

    Args:
        rpm: Velocidade em RPM (0 a ~19)

    Returns:
        Valor a escrever no registro (0 a 2000)
    """
    if rpm <= 0:
        return 0
    if rpm >= RPM_MAX:
        return REGISTER_MAX

    # Interpolacao linear por segmentos para valores exatos
    # Pontos de referencia: (0,0), (5,527), (10,1055), (15,1583), (19,2000)
    points = [(0, 0), (5, 527), (10, 1055), (15, 1583), (19, 2000)]

    # Encontra o segmento correto
    for i in range(len(points) - 1):
        rpm1, val1 = points[i]
        rpm2, val2 = points[i + 1]
        if rpm1 <= rpm <= rpm2:
            # Interpolacao linear
            frac = (rpm - rpm1) / (rpm2 - rpm1)
            return round(val1 + frac * (val2 - val1))

    # Fallback (nao deveria chegar aqui)
    return round(rpm * RPM_FACTOR)


def register_to_rpm(value: int) -> float:
    """
    Converte valor do registro para RPM.

    Args:
        value: Valor lido do registro 0x06E0 (0 a 2000)

    Returns:
        RPM correspondente (0.0 a ~19.0)
    """
    if value is None or value <= 0:
        return 0.0
    if value >= REGISTER_MAX:
        return RPM_MAX

    # Interpolacao inversa: rpm = valor / 105.533
    return value / RPM_FACTOR


def get_state_info(state_address: int) -> dict:
    """
    Retorna informacoes sobre um estado da maquina.

    Args:
        state_address: Endereco do estado (0x0300-0x0307)

    Returns:
        Dict com name, description, color, icon
    """
    return STATE_DESCRIPTIONS.get(state_address, {
        'name': 'DESCONHECIDO',
        'description': 'Estado desconhecido',
        'color': 'gray',
        'icon': '❓',
    })


def get_active_state_address(state_values: dict) -> int:
    """
    Determina qual estado esta ativo baseado nos valores lidos.

    Args:
        state_values: Dict {endereco: valor_bool}

    Returns:
        Endereco do estado ativo ou None
    """
    for addr, name in MACHINE_STATES.items():
        if state_values.get(addr, False):
            return addr
    return None


# ==========================================
# SUMARIO
# ==========================================

if __name__ == '__main__':
    print("=" * 70)
    print("MAPEAMENTO MODBUS - NOVO LADDER (MAQUINA DE ESTADOS)")
    print("=" * 70)

    print(f"\n📊 ESTADOS DA MAQUINA: {len(MACHINE_STATES)} estados")
    for name, addr in MACHINE_STATES.items():
        info = STATE_DESCRIPTIONS.get(addr, {})
        print(f"   {info.get('icon', '?')} {name}: 0x{addr:04X} ({addr})")

    print(f"\n🎛️  BITS DE CONTROLE: {len(CONTROL_BITS)} bits")
    for name, addr in CONTROL_BITS.items():
        print(f"   {name}: 0x{addr:04X} ({addr})")

    print(f"\n📏 ANGULOS: 3 dobras (32-bit cada)")
    for name, addr in BEND_ANGLES.items():
        print(f"   {name}: 0x{addr:04X} ({addr})")

    print(f"\n📝 REGISTROS DE TRABALHO:")
    for name, addr in WORK_REGISTERS.items():
        print(f"   {name}: 0x{addr:04X} ({addr})")

    print(f"\n⚡ VELOCIDADE (Dimmer 0-15 RPM):")
    print(f"   Registro: 0x06E0 (1760)")
    print(f"   Formula: valor = rpm * {RPM_FACTOR:.2f}")
    for rpm, val in RPM_VALUES.items():
        print(f"   {rpm:2d} RPM = {val}")

    print("\n" + "=" * 70)
