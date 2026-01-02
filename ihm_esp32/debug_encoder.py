#!/usr/bin/env python3
"""
DEBUG: Leitura do Encoder - Diagnóstico Completo
================================================

Script para diagnosticar problema de variação do encoder.
Mostra TODOS os valores intermediários para identificar a causa.
"""

import time
import sys
from modbus_client import ModbusClientWrapper
import modbus_map as mm

def main():
    print("=" * 70)
    print("DEBUG: LEITURA DO ENCODER - DIAGNÓSTICO COMPLETO")
    print("=" * 70)
    print()

    # Conecta ao CLP
    print("🔌 Conectando ao CLP...")
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', baudrate=57600, slave_id=1)

    if not client.connected:
        print("✗ ERRO: Não foi possível conectar ao CLP!")
        print("  Verifique:")
        print("  - Cabo USB-RS485 conectado")
        print("  - CLP ligado")
        print("  - Porta /dev/ttyUSB0 correta")
        sys.exit(1)

    print("✓ Conectado ao CLP!\n")
    print("Iniciando leitura contínua do encoder...")
    print("Pressione Ctrl+C para parar\n")
    print("-" * 70)
    print(f"{'Timestamp':<12} {'RAW (32-bit)':<15} {'MSW':<8} {'LSW':<8} {'MOD400':<8} {'Graus':<10}")
    print("-" * 70)

    try:
        count = 0
        last_raw = None

        while True:
            # Timestamp
            ts = time.strftime("%H:%M:%S.") + f"{int((time.time() % 1) * 1000):03d}"

            # Lê MSW (bits 31-16)
            msw = client.read_register(mm.ENCODER['ANGLE_MSW'])

            # Pequeno delay entre leituras (evitar race condition)
            time.sleep(0.001)

            # Lê LSW (bits 15-0)
            lsw = client.read_register(mm.ENCODER['ANGLE_LSW'])

            if msw is None or lsw is None:
                print(f"{ts:<12} ERRO: Falha na leitura Modbus!")
                time.sleep(0.1)
                continue

            # Combina em 32-bit
            raw_32bit = (msw << 16) | lsw

            # Normaliza (MOD 400)
            mod_400 = raw_32bit % 400

            # Converte para graus
            graus = (mod_400 / 400.0) * 360.0

            # Detecta variação
            delta_str = ""
            if last_raw is not None:
                delta = raw_32bit - last_raw
                if delta != 0:
                    delta_str = f" (Δ={delta:+d})"

            # Imprime linha
            print(f"{ts:<12} {raw_32bit:<15d} {msw:<8} {lsw:<8} {mod_400:<8} {graus:<10.2f}{delta_str}")

            last_raw = raw_32bit
            count += 1

            # A cada 20 leituras, mostra estatísticas
            if count % 20 == 0:
                print("-" * 70)
                print(f"Total de leituras: {count}")
                print("-" * 70)

            # Aguarda próxima leitura (50ms = 20 Hz)
            time.sleep(0.05)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("DEBUG FINALIZADO")
        print("=" * 70)
        print(f"Total de leituras: {count}")
        print()

    client.close()

if __name__ == "__main__":
    main()
