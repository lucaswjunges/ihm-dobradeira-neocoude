#!/usr/bin/env python3
"""
Teste na Máquina Real - Escala 2048

Valida que:
- 90° → grava 512 (0x0200) no CLP
- 45° → grava 256 (0x0100) no CLP
- Leitura retorna ângulos corretos
"""

import sys
sys.path.append('/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

def main():
    print("=" * 70)
    print("TESTE ESCALA 2048 - VALIDAÇÃO NA MÁQUINA")
    print("=" * 70)
    print()
    print("⚠️  Validando que:")
    print("  - 90° → 512 (0x0200) no CLP")
    print("  - 45° → 256 (0x0100) no CLP")
    print()

    # Conectar ao CLP
    print("Conectando ao CLP...")
    client = ModbusClientWrapper(
        stub_mode=False,
        port='/dev/ttyUSB0',
        baudrate=57600,
        slave_id=1
    )

    if not client.connected:
        print("\n❌ CLP NÃO CONECTADO!")
        print("Verifique:")
        print("  - Cabo USB-RS485 conectado")
        print("  - CLP ligado")
        print("  - Porta correta (/dev/ttyUSB0)")
        return

    print("✅ CLP conectado!\n")

    try:
        # Teste 1: Ler ângulos atuais
        print("-" * 70)
        print("TESTE 1 - LEITURA DE ÂNGULOS ATUAIS")
        print("-" * 70)
        print()

        for i in [1, 2, 3]:
            addr = [2114, 2116, 2118][i-1]
            clp_value = client.read_register(addr)

            if clp_value is not None:
                degrees = mm.clp_to_real_angle(clp_value)
                print(f"Dobra {i} (endereço {addr}):")
                print(f"  CLP retorna: {clp_value} (0x{clp_value:04X})")
                print(f"  Ângulo: {degrees:.1f}°")
                print()
            else:
                print(f"Dobra {i}: ERRO ao ler\n")

        # Teste 2: Gravar 90° na Dobra 1
        print("-" * 70)
        print("TESTE 2 - GRAVAR 90° NA DOBRA 1")
        print("-" * 70)
        print()

        resposta = input("Deseja gravar 90° na Dobra 1? (s/N): ").strip().lower()

        if resposta == 's':
            print("\n✎ Gravando 90°...")
            sucesso = client.write_bend_angle(1, 90.0)

            if sucesso:
                print("✅ Gravado!")

                # Aguardar ladder copiar
                print("\nAguardando 1 segundo para ladder copiar...")
                time.sleep(1.0)

                # Ler de volta
                print("\nLendo de volta do endereço 2114...")
                clp_value = client.read_register(2114)

                if clp_value is not None:
                    print(f"  CLP retorna: {clp_value} (0x{clp_value:04X})")

                    if clp_value == 512:
                        print(f"  ✅ CORRETO! Esperado 512 (0x0200), recebido {clp_value}")
                    else:
                        print(f"  ❌ ERRO! Esperado 512 (0x0200), recebido {clp_value}")

                    degrees = mm.clp_to_real_angle(clp_value)
                    print(f"  Ângulo convertido: {degrees:.1f}°")
                else:
                    print("  ❌ Erro ao ler de volta")
            else:
                print("❌ Erro ao gravar")
        else:
            print("Teste de escrita cancelado.")

        # Teste 3: Gravar 45° na Dobra 2
        print()
        print("-" * 70)
        print("TESTE 3 - GRAVAR 45° NA DOBRA 2")
        print("-" * 70)
        print()

        resposta = input("Deseja gravar 45° na Dobra 2? (s/N): ").strip().lower()

        if resposta == 's':
            print("\n✎ Gravando 45°...")
            sucesso = client.write_bend_angle(2, 45.0)

            if sucesso:
                print("✅ Gravado!")

                # Aguardar ladder copiar
                print("\nAguardando 1 segundo para ladder copiar...")
                time.sleep(1.0)

                # Ler de volta
                print("\nLendo de volta do endereço 2116...")
                clp_value = client.read_register(2116)

                if clp_value is not None:
                    print(f"  CLP retorna: {clp_value} (0x{clp_value:04X})")

                    if clp_value == 256:
                        print(f"  ✅ CORRETO! Esperado 256 (0x0100), recebido {clp_value}")
                    else:
                        print(f"  ❌ ERRO! Esperado 256 (0x0100), recebido {clp_value}")

                    degrees = mm.clp_to_real_angle(clp_value)
                    print(f"  Ângulo convertido: {degrees:.1f}°")
                else:
                    print("  ❌ Erro ao ler de volta")
            else:
                print("❌ Erro ao gravar")
        else:
            print("Teste de escrita cancelado.")

    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuário.")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n" + "=" * 70)
        print("TESTE FINALIZADO")
        print("=" * 70)

if __name__ == "__main__":
    main()
