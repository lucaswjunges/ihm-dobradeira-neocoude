#!/usr/bin/env python3
"""
Lê valores OFICIAIS do CLP para confirmar ângulos e RPM
"""
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def main():
    print("=" * 60)
    print("  LEITURA OFICIAL DE VALORES DO CLP")
    print("=" * 60)

    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0')

    if not client.connected:
        print("❌ CLP não conectado!")
        return

    print("✅ CLP conectado\n")

    # Lê ângulos
    print("ÂNGULOS DE DOBRA (valores em °):")
    print("-" * 60)

    angles = [
        ("Dobra 1 Esquerda", mm.BEND_ANGLES['BEND_1_LEFT_MSW'], mm.BEND_ANGLES['BEND_1_LEFT_LSW']),
        ("Dobra 2 Esquerda", mm.BEND_ANGLES['BEND_2_LEFT_MSW'], mm.BEND_ANGLES['BEND_2_LEFT_LSW']),
        ("Dobra 3 Esquerda", mm.BEND_ANGLES['BEND_3_LEFT_MSW'], mm.BEND_ANGLES['BEND_3_LEFT_LSW']),
    ]

    for name, msw_addr, lsw_addr in angles:
        raw = client.read_32bit(msw_addr, lsw_addr)
        if raw is not None:
            degrees = mm.clp_to_degrees(raw)
            print(f"  {name:20s}: {degrees:7.1f}° (raw={raw:6d}, 0x{msw_addr:04X}/0x{lsw_addr:04X})")
        else:
            print(f"  {name:20s}: ERRO (endereço 0x{msw_addr:04X}/0x{lsw_addr:04X})")

    print()

    # Lê velocidade/RPM
    print("VELOCIDADE / RPM:")
    print("-" * 60)

    speed_addr = mm.SUPERVISION_AREA['SPEED_CLASS']
    speed = client.read_register(speed_addr)
    if speed is not None:
        print(f"  Classe de Velocidade: {speed} RPM (endereço 0x{speed_addr:04X} = {speed_addr} dec)")
    else:
        print(f"  Classe de Velocidade: ERRO (endereço 0x{speed_addr:04X})")

    print()

    # Lê encoder
    print("POSIÇÃO ATUAL (ENCODER):")
    print("-" * 60)

    encoder_raw = client.read_32bit(mm.ENCODER['ANGLE_MSW'], mm.ENCODER['ANGLE_LSW'])
    if encoder_raw is not None:
        encoder_degrees = mm.clp_to_degrees(encoder_raw)
        print(f"  Posição: {encoder_degrees:7.1f}° (raw={encoder_raw:6d})")
    else:
        print(f"  Posição: ERRO")

    print()

    # Lê modo
    print("MODO DE OPERAÇÃO:")
    print("-" * 60)

    mode_bit = client.read_coil(mm.CRITICAL_STATES['MODE_BIT_REAL'])
    if mode_bit is not None:
        mode_text = "AUTO" if mode_bit else "MANUAL"
        print(f"  Modo atual: {mode_text} (bit 02FF = {mode_bit})")
    else:
        print(f"  Modo atual: ERRO")

    print()
    print("=" * 60)

    client.close()

if __name__ == "__main__":
    main()
