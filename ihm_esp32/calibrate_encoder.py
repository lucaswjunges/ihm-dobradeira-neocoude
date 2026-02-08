#!/usr/bin/env python3
"""
CALIBRAÇÃO: Descobrir pulsos/volta real do encoder
===================================================

Este script ajuda a descobrir:
1. Se estamos lendo o endereço correto (04D6)
2. Quantos pulsos por volta o encoder REALMENTE tem
3. Fator de conversão correto
"""

import time
from modbus_client import ModbusClientWrapper

def main():
    print("=" * 80)
    print("CALIBRAÇÃO DO ENCODER - Descobrindo pulsos/volta REAIS")
    print("=" * 80)
    print()

    # Conecta
    client = ModbusClientWrapper(stub_mode=False, port='/dev/ttyUSB0', baudrate=57600, slave_id=1)

    if not client.connected:
        print("✗ CLP não conectado!")
        return

    print("✓ Conectado ao CLP!\n")

    # Lê endereço 04D6
    addr_hex = 0x04D6
    addr_dec = 1238

    print(f"📍 Testando endereço: 0x{addr_hex:04X} ({addr_dec} decimal)")
    print()

    # Lê valor inicial
    print("Lendo valor inicial...")
    valor_inicial = client.read_register(addr_hex)

    if valor_inicial is None:
        print("✗ ERRO ao ler 0x04D6!")
        print("  Verifique se o endereço está correto")
        client.close()
        return

    print(f"✓ Valor inicial: {valor_inicial}")
    print()

    print("=" * 80)
    print("INSTRUÇÕES:")
    print("=" * 80)
    print()
    print("1. Marque a posição INICIAL do eixo (use fita adesiva)")
    print("2. Gire o eixo EXATAMENTE 1 VOLTA COMPLETA (360°)")
    print("3. Pare quando voltar à marca inicial")
    print()
    print("Pressione ENTER quando estiver pronto para começar...")
    input()

    print("\n🔄 GIRANDO... (monitorando valor em tempo real)")
    print()
    print(f"{'Tempo':<8} {'Valor RAW':<12} {'Delta':<12} {'Estimativa °':<15}")
    print("-" * 80)

    ultimo_valor = valor_inicial
    start_time = time.time()

    try:
        while True:
            # Lê valor atual
            valor_atual = client.read_register(addr_hex)

            if valor_atual is not None:
                # Calcula delta
                delta = valor_atual - valor_inicial
                delta_ultimo = valor_atual - ultimo_valor

                # Estimativa em graus (assumindo 400 pulsos/volta)
                graus_400 = (delta / 400.0) * 360.0

                # Tempo decorrido
                elapsed = time.time() - start_time

                # Imprime
                marca = " ← MUDOU!" if delta_ultimo != 0 else ""
                print(f"{elapsed:7.1f}s {valor_atual:<12} {delta:+12} {graus_400:14.1f}°{marca}")

                ultimo_valor = valor_atual

            time.sleep(0.1)  # Atualiza a cada 100ms

    except KeyboardInterrupt:
        print("\n")
        print("=" * 80)
        print("PARADO! Calculando resultados...")
        print("=" * 80)
        print()

        # Lê valor final
        valor_final = client.read_register(addr_hex)

        if valor_final is not None:
            total_pulsos = valor_final - valor_inicial

            print(f"Valor inicial: {valor_inicial}")
            print(f"Valor final:   {valor_final}")
            print(f"Total pulsos:  {total_pulsos}")
            print()

            print("=" * 80)
            print("ANÁLISE:")
            print("=" * 80)
            print()

            if abs(total_pulsos) < 10:
                print("⚠️  ATENÇÃO: Poucos pulsos detectados!")
                print("   - Encoder pode não estar conectado")
                print("   - Ou endereço 04D6 está errado")
            else:
                print(f"✓ Detectados {total_pulsos} pulsos em 1 volta")
                print()

                # Calcula fator de conversão
                if total_pulsos > 0:
                    pulsos_por_volta = abs(total_pulsos)
                    graus_por_pulso = 360.0 / pulsos_por_volta

                    print(f"📊 RESULTADO:")
                    print(f"   Pulsos por volta: {pulsos_por_volta}")
                    print(f"   Graus por pulso:  {graus_por_pulso:.4f}°")
                    print()

                    print(f"🔧 CORREÇÃO NECESSÁRIA no código:")
                    print(f"   graus = (pulsos % {pulsos_por_volta}) * {graus_por_pulso:.6f}")
                    print()

                    # Compara com 400
                    if abs(pulsos_por_volta - 400) < 10:
                        print("✓ Código atual está CORRETO (400 pulsos/volta)")
                    elif abs(pulsos_por_volta - 100) < 10:
                        print("✗ Código está ERRADO! Deveria ser 100 pulsos/volta")
                    else:
                        print(f"✗ Código está ERRADO! Deveria ser {pulsos_por_volta} pulsos/volta")

    client.close()

if __name__ == "__main__":
    main()
