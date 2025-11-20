#!/usr/bin/env python3
"""
Mapeamento Modbus Completo - CLP Atos MPC4004
Versão: 2.0 (Híbrida - Python + Ladder)
Data: 13 de Novembro de 2025

Este arquivo centraliza TODOS os endereços Modbus validados empiricamente.
"""

# ==========================================
# BOTÕES / TECLADO (Coils - Function 0x01/0x05)
# ==========================================

KEYBOARD_NUMERIC = {
    'K1': 0x00A0,  # 160 - Número 1 / Vai para Tela 4 (dobra 1)
    'K2': 0x00A1,  # 161 - Número 2 / Vai para Tela 5 (dobra 2)
    'K3': 0x00A2,  # 162 - Número 3 / Vai para Tela 6 (dobra 3)
    'K4': 0x00A3,  # 163 - Número 4 / Sentido Esquerda (AUTO)
    'K5': 0x00A4,  # 164 - Número 5 / Sentido Direita (AUTO)
    'K6': 0x00A5,  # 165 - Número 6
    'K7': 0x00A6,  # 166 - Número 7 / Velocidade (K1+K7 simultâneo)
    'K8': 0x00A7,  # 167 - Número 8
    'K9': 0x00A8,  # 168 - Número 9
    'K0': 0x00A9,  # 169 - Número 0
}

KEYBOARD_FUNCTION = {
    'S1':        0x00DC,  # 220 - Alterna AUTO/MANUAL (só quando parado)
    'S2':        0x00DD,  # 221 - Reset/Contexto
    'ARROW_UP':  0x00AC,  # 172 - Seta CIMA
    'ARROW_DOWN': 0x00AD,  # 173 - Seta BAIXO
    'ESC':       0x00BC,  # 188 - Cancelar/Sair
    'ENTER':     0x0025,  # 37  - Confirmar
    'EDIT':      0x0026,  # 38  - Modo Edição
    'LOCK':      0x00F1,  # 241 - Trava Teclado
}

# ==========================================
# BOTÕES DE PAINEL FÍSICO (Coils - Function 0x05)
# ==========================================
# ✅ CORRIGIDO 20/Nov/2025 - Usa SAÍDAS FÍSICAS S0/S1
# Análise completa do ladder ROT0.lad revelou sistema DUPLO:
# - PRIMÁRIO: 0x0180/0x0181 (S0/S1) = Saídas físicas (USAR ESTE!)
# - SECUNDÁRIO: 0x0190/0x0191 = Flags internas (modo AUTO avançado)
#
# IMPORTANTE: Sistema usa LATCH (SETR), motor fica ligado até desligar

PANEL_BUTTONS = {
    # SAÍDAS FÍSICAS (PRIMÁRIO - usar estes!)
    'FORWARD':  0x0180,  # 384 dec - S0 (saída física AVANÇAR)
    'BACKWARD': 0x0181,  # 385 dec - S1 (saída física RECUAR)

    # ESTADOS INTERNOS (SECUNDÁRIO - para modo AUTO avançado)
    'FORWARD_FLAG':  0x0190,  # 400 dec (flag interna)
    'BACKWARD_FLAG': 0x0191,  # 401 dec (flag interna)

    # ENTRADAS DIGITAIS (READ-ONLY - para feedback)
    'FORWARD_INPUT':  0x0102,  # 258 dec - E2: Botão AVANÇAR físico
    'STOP_INPUT':     0x0103,  # 259 dec - E3: Botão PARADA físico
    'BACKWARD_INPUT': 0x0104,  # 260 dec - E4: Botão RECUAR físico
    'SENSOR_INPUT':   0x0105,  # 261 dec - E5: Sensor adicional
}

# ==========================================
# LEDs (Coils - Function 0x01)
# ==========================================

LEDS = {
    'LED1': 0x00C0,  # 192 - Dobra 1 ativa (K1)
    'LED2': 0x00C1,  # 193 - Dobra 2 ativa (K2)
    'LED3': 0x00C2,  # 194 - Dobra 3 ativa (K3)
    'LED4': 0x00C3,  # 195 - Sentido Esquerda (K4)
    'LED5': 0x00C4,  # 196 - Sentido Direita (K5)
}

# ==========================================
# I/O DIGITAL (Registers 16-bit - Function 0x03)
# ==========================================
# IMPORTANTE: Usar bit 0 (LSB) para status

DIGITAL_INPUTS = {
    'E0': 0x0100,  # 256
    'E1': 0x0101,  # 257
    'E2': 0x0102,  # 258
    'E3': 0x0103,  # 259
    'E4': 0x0104,  # 260
    'E5': 0x0105,  # 261
    'E6': 0x0106,  # 262
    'E7': 0x0107,  # 263
}

DIGITAL_OUTPUTS = {
    'S0': 0x0180,  # 384
    'S1': 0x0181,  # 385
    'S2': 0x0182,  # 386
    'S3': 0x0183,  # 387
    'S4': 0x0184,  # 388
    'S5': 0x0185,  # 389
    'S6': 0x0186,  # 390
    'S7': 0x0187,  # 391
}

# ==========================================
# ENCODER / POSIÇÃO ANGULAR (32-bit MSW+LSW)
# ==========================================
# Formato: value = (MSW << 16) | LSW
# Conversão: graus = value / 10.0

ENCODER = {
    'ANGLE_MSW': 0x04D6,  # 1238 - Posição angular (bits 31-16)
    'ANGLE_LSW': 0x04D7,  # 1239 - Posição angular (bits 15-0)
    'RPM_MSW':   0x04D0,  # 1232 - RPM/velocidade (bits 31-16)
    'RPM_LSW':   0x04D1,  # 1233 - RPM/velocidade (bits 15-0)
}

# ==========================================
# ÁREA MODBUS INPUT (32-bit) - ESCRITA IHM WEB
# ==========================================
# ✅ VALIDADO 20/Nov/2025 - Endereços testados empiricamente no CLP real
# FLUXO: IHM escreve em 0x0A00 (base) → ladder lê de 0x0840 (shadow)
# Formato: 32-bit em 2 registros consecutivos (Big-Endian style)
# Conversão: value_clp = graus * 10
#
# ATENÇÃO: 0x0A02 é para RPM, NÃO para ângulo!
# Layout da memória:
#   0x0A00, 0x0A01 = Dobra 1 (MSW, LSW) - 32-bit
#   0x0A02         = RPM (16-bit)
#   0x0A04, 0x0A05 = Dobra 2 (MSW, LSW) - 32-bit
#   0x0A08, 0x0A09 = Dobra 3 (MSW, LSW) - 32-bit

BEND_ANGLES_MODBUS_INPUT = {
    # Dobra 1 - 32-bit em 0x0A00-0x0A01
    'BEND_1_INPUT_BASE': 0x0A00,  # 2560 - Dobra 1 base (escrever 2 registros consecutivos)
    'BEND_1_TRIGGER':    0x0390,  # 912  - Trigger Dobra 1 (COIL)

    # Dobra 2 - 32-bit em 0x0A04-0x0A05
    'BEND_2_INPUT_BASE': 0x0A04,  # 2564 - Dobra 2 base (escrever 2 registros consecutivos)
    'BEND_2_TRIGGER':    0x0391,  # 913  - Trigger Dobra 2 (COIL)

    # Dobra 3 - 32-bit em 0x0A08-0x0A09
    'BEND_3_INPUT_BASE': 0x0A08,  # 2568 - Dobra 3 base (escrever 2 registros consecutivos)
    'BEND_3_TRIGGER':    0x0392,  # 914  - Trigger Dobra 3 (COIL)
}

# ==========================================
# RPM / VELOCIDADE (16-bit)
# ==========================================
# ✅ VALIDADO 20/Nov/2025 - Testado empiricamente
# Escrever em 0x0A02, ler de 0x06E0

RPM_REGISTERS = {
    'RPM_WRITE': 0x0A02,  # 2562 - Escrita de RPM (16-bit: 5, 10 ou 15)
    'RPM_READ':  0x06E0,  # 1760 - Leitura de RPM/tensão do inversor
}

# ==========================================
# ÁREA SCADA (32-bit) - ESPELHO PARA LEITURA
# ==========================================
# ✅ RECOMENDADO para leitura pela IHM Web
# ROT5 copia automaticamente de 0x0840 para 0x0B00
# Formato: 32-bit MSW/LSW

BEND_ANGLES_SCADA = {
    # Dobra 1 - READ-ONLY (espelho SCADA)
    # NOTA: No CLP a ordem é LSW primeiro, MSW depois
    # Mas para read_register_32bit precisamos passar endereço MSW
    'BEND_1_SCADA_MSW': 0x0B02,  # 2818 - MSW Dobra 1 (SCADA mirror)
    'BEND_1_SCADA_LSW': 0x0B00,  # 2816 - LSW Dobra 1 (SCADA mirror)

    # Dobra 2 - READ-ONLY
    'BEND_2_SCADA_MSW': 0x0B06,  # 2822 - MSW Dobra 2 (SCADA mirror)
    'BEND_2_SCADA_LSW': 0x0B04,  # 2820 - LSW Dobra 2 (SCADA mirror)

    # Dobra 3 - READ-ONLY
    'BEND_3_SCADA_MSW': 0x0B0A,  # 2826 - MSW Dobra 3 (SCADA mirror)
    'BEND_3_SCADA_LSW': 0x0B08,  # 2824 - LSW Dobra 3 (SCADA mirror)
}

# ==========================================
# ÂNGULOS SHADOW (32-bit) - ÁREA PROTEGIDA
# ==========================================
# ⚠️ NÃO USAR PARA ESCRITA - Somente leitura!
# Valores sobrescritos por ROT4/ROT5 no ladder a cada scan
# Byte baixo forçado para 0x99 (153) - Ver ANALISE_BYTE_099_LADDER.md
#
# IMPORTANTE: Estes são os endereços que o LADDER LÊ (PRINCIPAL.lad):
#   - Line00008: SUB 0858 = 0842 - 0840  (Dobra 1)
#   - Line00009: SUB 0858 = 0848 - 0846  (Dobra 2)
#   - Line00010: SUB 0858 = 0852 - 0850  (Dobra 3)

BEND_ANGLES_SHADOW = {
    # Dobra 1 - READ-ONLY
    'BEND_1_LEFT_LSW':  0x0840,  # 2112 - Shadow Dobra 1 (LSW - protegido)
    'BEND_1_LEFT_MSW':  0x0842,  # 2114 - Shadow Dobra 1 (MSW - protegido)

    # Dobra 2 - READ-ONLY
    'BEND_2_LEFT_LSW':  0x0846,  # 2118 - Shadow Dobra 2 (LSW - protegido)
    'BEND_2_LEFT_MSW':  0x0848,  # 2120 - Shadow Dobra 2 (MSW - protegido)

    # Dobra 3 - READ-ONLY
    'BEND_3_LEFT_LSW':  0x0850,  # 2128 - Shadow Dobra 3 (LSW - protegido)
    'BEND_3_LEFT_MSW':  0x0852,  # 2130 - Shadow Dobra 3 (MSW - protegido)
}

# ==========================================
# ÁREA DE SUPERVISÃO (Python Escrita)
# ==========================================
# ESTRATÉGIA HÍBRIDA:
# - Python LÊ coils (botões, LEDs) via Function 0x01
# - Python INFERE estados (tela, modo, dobra)
# - Python ESCREVE em 0x0940-0x0950 via Function 0x06
# - IHM Web LÊ desta área → Precisão 100%!

SUPERVISION_AREA = {
    'SCREEN_NUM':    0x0940,  # 2368 - Número da tela (0-10) ✅ TESTADO R/W
    'TARGET_MSW':    0x0942,  # 2370 - Posição alvo MSW (escrito por ladder)
    'TARGET_LSW':    0x0944,  # 2372 - Posição alvo LSW (escrito por ladder)
    'MODE_STATE':    0x0946,  # 2374 - Modo (0=Manual, 1=Auto)
    'BEND_CURRENT':  0x0948,  # 2376 - Dobra atual (1, 2, 3)
    'DIRECTION':     0x094A,  # 2378 - Direção (0=Esq, 1=Dir)
    'SPEED_CLASS':   0x094C,  # 2380 - Velocidade (5, 10, 15 rpm) ✅ TESTADO R/W
    'CYCLE_ACTIVE':  0x094E,  # 2382 - Ciclo ativo (0=Parado, 1=Ativo)
    # NOTA: Removido EMERGENCY daqui - conflitava com BEND_ANGLES antigo
    # Emergency status deve ser lido via coil ou entrada digital
}

# ==========================================
# REGISTROS AUXILIARES
# ==========================================

AUXILIARY = {
    'CALC_AUX': 0x0858,  # 2136 - Registro para cálculos (SUB)
}

# ==========================================
# INVERSOR / CONTROLE
# ==========================================

INVERTER = {
    'VOLTAGE': 0x06E0,  # 1760 - Tensão do inversor
}

# ==========================================
# ESTADOS CRÍTICOS (Coils - Function 0x01)
# ==========================================

CRITICAL_STATES = {
    'MODBUS_SLAVE_ENABLED': 0x00BE,  # 190 - DEVE estar ON para Modbus funcionar
    'CYCLE_ACTIVE':         0x0191,  # 401 - Ciclo de dobra ativo
    'MODE_BIT_REAL':        0x02FF,  # 767 - BIT REAL DE MODO (False=MANUAL, True=AUTO)
}

# ==========================================
# HELPERS - CONVERSÃO 32-bit
# ==========================================

def read_32bit(msw: int, lsw: int) -> int:
    """
    Combina MSW e LSW em valor 32-bit.

    Args:
        msw: Most Significant Word (16-bit)
        lsw: Least Significant Word (16-bit)

    Returns:
        Valor 32-bit combinado
    """
    return (msw << 16) | lsw


def split_32bit(value: int) -> tuple:
    """
    Divide valor 32-bit em MSW e LSW.

    Args:
        value: Valor 32-bit

    Returns:
        Tupla (msw, lsw)
    """
    msw = (value >> 16) & 0xFFFF
    lsw = value & 0xFFFF
    return (msw, lsw)


def clp_to_degrees(clp_value: int) -> float:
    """
    Converte valor CLP (32-bit) para graus com validação e MOD 360.

    ✅ ATUALIZADO 20/Nov/2025 - Aplica MOD 360° para mostrar ângulo atual
    dentro de uma volta completa (0-360°).

    Exemplo:
        3058 → 305.8° (3058 MOD 360 = 338.8°)
        119 → 11.9°
        3600 → 0.0° (volta completa)

    Args:
        clp_value: Valor lido do CLP (multiplicado por 10)

    Returns:
        Ângulo em graus MOD 360 (float), 0.0 se inválido
    """
    if clp_value is None:
        return 0.0

    degrees = clp_value / 10.0

    # Validação: ângulos devem estar entre 0 e 100000 graus
    # (considerando possíveis múltiplas voltas acumuladas)
    if degrees < 0 or degrees > 100000:
        # Valor absurdo, provavelmente lixo de memória
        return 0.0

    # Aplica MOD 360 para mostrar ângulo atual dentro de uma volta
    degrees_mod = degrees % 360.0

    return degrees_mod


def degrees_to_clp(degrees: float) -> int:
    """
    Converte graus para valor CLP (32-bit).

    Args:
        degrees: Ângulo em graus

    Returns:
        Valor para escrever no CLP (int)
    """
    return int(degrees * 10)


# ==========================================
# CONSTANTES DE CONFIGURAÇÃO
# ==========================================

# Comunicação Modbus RTU
MODBUS_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 57600,
    'parity': 'N',  # None
    'stopbits': 2,
    'bytesize': 8,
    'timeout': 1.0,  # segundos
    'slave_id': 1,
}

# Velocidades disponíveis
SPEED_CLASSES = {
    1: 5,   # Classe 1 = 5 rpm (MANUAL e AUTO)
    2: 10,  # Classe 2 = 10 rpm (só AUTO)
    3: 15,  # Classe 3 = 15 rpm (só AUTO)
}

# Textos das telas (para geração local na IHM Web)
SCREEN_TEXTS = {
    0: {
        'line1': '    TRILLOR     ',
        'line2': '   DOBRADEIRA   ',
    },
    1: {
        'line1': 'MENU PRINCIPAL  ',
        'line2': 'K1:Dobras K2:...',
    },
    2: {
        'line1': '  MODO AUTO     ',
        'line2': 'K4:ESQ   K5:DIR ',
    },
    4: {
        'line1': 'DOBRA 1 {DIR}   ',
        'line2': 'ANG: {ANGLE}°   ',
    },
    5: {
        'line1': 'DOBRA 2 {DIR}   ',
        'line2': 'ANG: {ANGLE}°   ',
    },
    6: {
        'line1': 'DOBRA 3 {DIR}   ',
        'line2': 'ANG: {ANGLE}°   ',
    },
}

# ==========================================
# SUMÁRIO DO MAPEAMENTO
# ==========================================

if __name__ == '__main__':
    print("=" * 70)
    print("MAPEAMENTO MODBUS - CLP ATOS MPC4004")
    print("=" * 70)
    print(f"\n📌 BOTÕES (Coils): {len(KEYBOARD_NUMERIC) + len(KEYBOARD_FUNCTION)} endereços")
    print(f"💡 LEDs (Coils): {len(LEDS)} endereços")
    print(f"🔌 I/O Digital: {len(DIGITAL_INPUTS) + len(DIGITAL_OUTPUTS)} endereços")
    print(f"📐 Encoder (32-bit): {len(ENCODER)} registros")
    print(f"📏 Ângulos (32-bit): {len(BEND_ANGLES)} registros")
    print(f"🎯 Supervisão (Python escrita): {len(SUPERVISION_AREA)} registros")
    print(f"⚙️  Auxiliares: {len(AUXILIARY) + len(INVERTER)} registros")
    print(f"🚨 Estados críticos: {len(CRITICAL_STATES)} coils")

    total = (len(KEYBOARD_NUMERIC) + len(KEYBOARD_FUNCTION) + len(LEDS) +
             len(DIGITAL_INPUTS) + len(DIGITAL_OUTPUTS) + len(ENCODER) +
             len(BEND_ANGLES) + len(SUPERVISION_AREA) + len(AUXILIARY) +
             len(INVERTER) + len(CRITICAL_STATES))

    print(f"\n🎉 TOTAL: {total} endereços mapeados")
    print("=" * 70)

    print("\n✅ VALIDADO EMPIRICAMENTE:")
    print("   • E0-E7, S0-S7: 12/Nov/2025 (mbpoll + pymodbus)")
    print("   • Encoder 32-bit: 12/Nov/2025")
    print("   • Ângulos 32-bit: 12/Nov/2025")
    print("   • Supervisão 0x0940: 13/Nov/2025 ✅ R/W confirmado")
    print("=" * 70)
