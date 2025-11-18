"""
MODBUS MAP - IHM Web para Dobradeira NEOCOUDE-HD-15
====================================================

Mapeamento completo de 95 registros/bits descobertos via análise PRINCIPA.LAD

Protocolo: Modbus RTU
Baudrate: 57600 bps
Parity: None
Stop bits: 2
Slave ID: 1

Data: 11 de novembro de 2025
"""

# ============================================================================
# BOTÕES/TECLADO (Coils - Function 0x05)
# ============================================================================

# Teclado Numérico (K0-K9)
BTN_K1 = 0x00A0  # 160 - Número 1 / Vai p/ Tela 4 (Dobra 1)
BTN_K2 = 0x00A1  # 161 - Número 2 / Vai p/ Tela 5 (Dobra 2)
BTN_K3 = 0x00A2  # 162 - Número 3 / Vai p/ Tela 6 (Dobra 3)
BTN_K4 = 0x00A3  # 163 - Número 4 / Sentido Esquerda (modo AUTO)
BTN_K5 = 0x00A4  # 164 - Número 5 / Sentido Direita (modo AUTO)
BTN_K6 = 0x00A5  # 165 - Número 6
BTN_K7 = 0x00A6  # 166 - Número 7 / Velocidade (K1+K7 simultâneo)
BTN_K8 = 0x00A7  # 167 - Número 8
BTN_K9 = 0x00A8  # 168 - Número 9
BTN_K0 = 0x00A9  # 169 - Número 0

# Teclas de Função
BTN_S1 = 0x00DC  # 220 - Alterna AUTO/MANUAL
BTN_S2 = 0x00DD  # 221 - Reset/Contexto

# Navegação
BTN_ARROW_UP = 0x00AC    # 172 - Seta CIMA
BTN_ARROW_DOWN = 0x00AD  # 173 - Seta BAIXO
BTN_ESC = 0x00BC         # 188 - Escape/Cancelar

# Sistema
BTN_ENTER = 0x0025  # 37 - Confirmar
BTN_EDIT = 0x0026   # 38 - Modo Edição
BTN_LOCK = 0x00F1   # 241 - Trava Teclado

# ============================================================================
# ENCODER / POSIÇÃO ANGULAR (Registers 32-bit - Function 0x03)
# ============================================================================

# Posição Angular Atual (MSW + LSW)
ENCODER_ANGLE_MSW = 0x04D6  # 1238 - Encoder posição (bits 31-16)
ENCODER_ANGLE_LSW = 0x04D7  # 1239 - Encoder posição (bits 15-0)

# ============================================================================
# ÂNGULOS SETPOINT - 3 DOBRAS (Registers 32-bit - Function 0x03/0x06)
# ============================================================================

# DOBRA 1 (Tela 4 - Acessada por K1)
BEND_1_LEFT_LSW = 0x0840  # 2112 - Ângulo 1 Esquerda (bits 15-0)
BEND_1_LEFT_MSW = 0x0842  # 2114 - Ângulo 1 Esquerda (bits 31-16)

# DOBRA 2 (Tela 5 - Acessada por K2)
BEND_2_LEFT_LSW = 0x0848  # 2120 - Ângulo 2 Esquerda (bits 15-0)
BEND_2_LEFT_MSW = 0x084A  # 2122 - Ângulo 2 Esquerda (bits 31-16)

# DOBRA 3 (Tela 6 - Acessada por K3)
BEND_3_LEFT_LSW = 0x0850  # 2128 - Ângulo 3 Esquerda (bits 15-0)
BEND_3_LEFT_MSW = 0x0852  # 2130 - Ângulo 3 Esquerda (bits 31-16)

# ============================================================================
# ENTRADAS DIGITAIS E0-E7 (Registers 16-bit - Function 0x03)
# ============================================================================

INPUT_E0 = 0x0100  # 256 - Sensor referência/zero
INPUT_E1 = 0x0101  # 257 - Carenagem/proteção
INPUT_E2 = 0x0102  # 258 - Botão AVANÇAR (painel físico)
INPUT_E3 = 0x0103  # 259 - Botão PARADA (painel físico)
INPUT_E4 = 0x0104  # 260 - Botão RECUAR (painel físico)
INPUT_E5 = 0x0105  # 261 - Sensor carenagem
INPUT_E6 = 0x0106  # 262 - Não mapeado
INPUT_E7 = 0x0107  # 263 - Não mapeado

# ============================================================================
# SAÍDAS DIGITAIS S0-S7 (Registers 16-bit - Function 0x03/0x05/0x06)
# ============================================================================

OUTPUT_S0 = 0x0180  # 384 - Motor AVANÇAR (CCW)
OUTPUT_S1 = 0x0181  # 385 - Motor RECUAR (CW)
OUTPUT_S2 = 0x0182  # 386 - Não mapeado
OUTPUT_S3 = 0x0183  # 387 - Não mapeado
OUTPUT_S4 = 0x0184  # 388 - Não mapeado
OUTPUT_S5 = 0x0185  # 389 - Não mapeado
OUTPUT_S6 = 0x0186  # 390 - Não mapeado
OUTPUT_S7 = 0x0187  # 391 - Não mapeado

# ============================================================================
# LEDs FRONTAIS (Coils - Function 0x01/0x05)
# ============================================================================

LED_1 = 0x00C0   # 192 - LED 1 (indica dobra 1 ativa?)
LED_2 = 0x00C1   # 193 - LED 2 (indica dobra 2 ativa?)
LED_3 = 0x00C2   # 194 - LED 3 (indica dobra 3 ativa?)
LED_4 = 0x00C3   # 195 - LED 4 (sentido esquerda?)
LED_5 = 0x00C4   # 196 - LED 5 (sentido direita?)

# ============================================================================
# CONFIGURAÇÃO DO CLP (Registers - Function 0x03)
# ============================================================================

STATE_MODBUS_SLAVE_ENABLE = 0x00BE  # 190 - Habilita modo Modbus slave (CRÍTICO!)

# ============================================================================
# HELPERS - Funções auxiliares para 32-bit
# ============================================================================

def read_32bit(msw: int, lsw: int) -> int:
    """Combina MSW e LSW em valor 32-bit"""
    return (msw << 16) | lsw

def split_32bit(value: int) -> tuple:
    """Separa valor 32-bit em MSW e LSW"""
    msw = (value >> 16) & 0xFFFF
    lsw = value & 0xFFFF
    return (msw, lsw)

# ============================================================================
# MAPEAMENTO ESTRUTURADO PARA IHM WEB
# ============================================================================

KEYBOARD_NUMERIC = {
    'K0': BTN_K0, 'K1': BTN_K1, 'K2': BTN_K2, 'K3': BTN_K3, 'K4': BTN_K4,
    'K5': BTN_K5, 'K6': BTN_K6, 'K7': BTN_K7, 'K8': BTN_K8, 'K9': BTN_K9
}

KEYBOARD_FUNCTION = {
    'S1': BTN_S1,
    'S2': BTN_S2,
    'UP': BTN_ARROW_UP,
    'DOWN': BTN_ARROW_DOWN,
    'ESC': BTN_ESC,
    'ENTER': BTN_ENTER,
    'EDIT': BTN_EDIT,
    'LOCK': BTN_LOCK
}

BEND_ANGLES = {
    1: {'left_msw': BEND_1_LEFT_MSW, 'left_lsw': BEND_1_LEFT_LSW},
    2: {'left_msw': BEND_2_LEFT_MSW, 'left_lsw': BEND_2_LEFT_LSW},
    3: {'left_msw': BEND_3_LEFT_MSW, 'left_lsw': BEND_3_LEFT_LSW}
}

DIGITAL_INPUTS = {
    'E0': INPUT_E0, 'E1': INPUT_E1, 'E2': INPUT_E2, 'E3': INPUT_E3,
    'E4': INPUT_E4, 'E5': INPUT_E5, 'E6': INPUT_E6, 'E7': INPUT_E7
}

DIGITAL_OUTPUTS = {
    'S0': OUTPUT_S0, 'S1': OUTPUT_S1, 'S2': OUTPUT_S2, 'S3': OUTPUT_S3,
    'S4': OUTPUT_S4, 'S5': OUTPUT_S5, 'S6': OUTPUT_S6, 'S7': OUTPUT_S7
}

LEDS = {
    'LED1': LED_1, 'LED2': LED_2, 'LED3': LED_3, 'LED4': LED_4, 'LED5': LED_5
}
