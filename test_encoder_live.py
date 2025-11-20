#!/usr/bin/env python3
"""
test_encoder_live.py
Monitora encoder em tempo real para calibração
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=" * 70)
print("TESTE DO ENCODER - MONITORAMENTO EM TEMPO REAL")
print("=" * 70)
print("\nInstruções:")
print("  1. Gire o prato manualmente")
print("  2. Observe a contagem do encoder")
print("  3. Para calibrar, marque posição inicial e gire 360°")
print("  4. Anote diferença para calcular pulsos/revolução")
print("\nPressione Ctrl+C para sair\n")

# Valor inicial para calcular delta
initial_value = None
previous_value = None

try:
    while True:
        # Ler registradores do encoder (04D6/04D7 = 1238/1239 decimal)
        result_msw = client.read_holding_registers(1238, 1)
        result_lsw = client.read_holding_registers(1239, 1)

        if result_msw and result_lsw and not result_msw.isError() and not result_lsw.isError():
            msw = result_msw.registers[0]
            lsw = result_lsw.registers[0]

            # Combinar em valor de 32-bit
            encoder_raw = (msw << 16) | lsw

            # Guardar valor inicial
            if initial_value is None:
                initial_value = encoder_raw
                previous_value = encoder_raw

            # Calcular deltas
            delta_from_start = encoder_raw - initial_value
            delta_from_prev = encoder_raw - previous_value

            # Tentar estimar ângulo (fórmula provisória)
            # Assumindo ~65536 pulsos/revolução (ajustar após calibrar)
            angle_estimated = (encoder_raw % 65536) * (360.0 / 65536.0)

            # Exibir informações
            print(f"\r"
                  f"Encoder: {encoder_raw:10d} | "
                  f"Delta: {delta_from_start:+8d} | "
                  f"Ângulo est: {angle_estimated:6.1f}° | "
                  f"MSW: 0x{msw:04X} LSW: 0x{lsw:04X}",
                  end='', flush=True)

            # Detectar mudanças grandes (rotação)
            if abs(delta_from_prev) > 100:
                direction = "↻ Horário" if delta_from_prev > 0 else "↺ Anti-horário"
                print(f"\n   → {direction} ({delta_from_prev:+d} pulsos)")

            previous_value = encoder_raw

        else:
            print("\r✗ Erro ao ler encoder", end='', flush=True)

        time.sleep(0.1)  # 100ms

except KeyboardInterrupt:
    print("\n\n" + "=" * 70)
    print("RESUMO DA CALIBRAÇÃO")
    print("=" * 70)
    if initial_value is not None and previous_value is not None:
        total_delta = previous_value - initial_value
        print(f"\nValor inicial: {initial_value}")
        print(f"Valor final:   {previous_value}")
        print(f"Delta total:   {total_delta} pulsos")
        print()
        print("Para calibrar:")
        print("  1. Marque posição inicial do prato")
        print("  2. Rode este script e anote valor inicial")
        print("  3. Gire o prato EXATAMENTE 360° (uma volta completa)")
        print("  4. Anote valor final")
        print("  5. Pulsos/revolução = Valor final - Valor inicial")
        print("  6. Graus/pulso = 360 / Pulsos/revolução")
    print()
