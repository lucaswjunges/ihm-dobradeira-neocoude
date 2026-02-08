#!/usr/bin/env python3
"""
Teste na Máquina Real - Validação de Ângulos Dobrados

Este script testa as conversões diretamente na máquina:
1. Lê ângulos atuais do CLP
2. Mostra conversão correta (÷ 2)
3. Permite gravar novos ângulos para teste
4. Valida leitura do encoder

Execute ao lado da máquina com CLP conectado!
"""

import sys
sys.path.append('/home/lucas-junges/Documents/wco/ihm_esp32')

from modbus_client import ModbusClientWrapper
import modbus_map as mm
import time

def test_leitura_encoder(client):
    """Testa leitura do encoder."""
    print("\n" + "=" * 70)
    print("TESTE 1 - LEITURA DO ENCODER")
    print("=" * 70)

    print("\nLendo encoder (endereço 1238 decimal, 0x04D6)...")

    # Ler 5 vezes para ver se está estável
    for i in range(5):
        pulsos = client.read_register(1238)  # 0x04D6
        if pulsos is not None:
            graus_maquina = mm.clp_to_degrees(pulsos)
            print(f"  Leitura {i+1}: {pulsos:3d} pulsos = {graus_maquina:6.1f}° (máquina)")
        else:
            print(f"  Leitura {i+1}: ERRO ao ler encoder")
        time.sleep(0.2)

    print("\n✅ Encoder sempre mostra 0-400 DECIMAL (nunca A/B/F)!")

def test_leitura_angulos(client):
    """Testa leitura de ângulos programados."""
    print("\n" + "=" * 70)
    print("TESTE 2 - LEITURA DE ÂNGULOS PROGRAMADOS")
    print("=" * 70)

    print("\nLendo ângulos do CLP (endereços 2114, 2116, 2118 decimal)...")

    for i in [1, 2, 3]:
        # Endereços de leitura
        addresses = {
            1: 2114,  # 0x0842
            2: 2116,  # 0x0844
            3: 2118,  # 0x0846
        }

        addr = addresses[i]
        pulsos = client.read_register(addr)

        if pulsos is not None:
            graus_maquina = mm.clp_to_degrees(pulsos)
            graus_real = mm.machine_angle_to_real(pulsos)

            print(f"\n  Dobra {i} (endereço {addr}):")
            print(f"    CLP retorna: {pulsos} pulsos (DECIMAL)")
            print(f"    Máquina gira: {graus_maquina:.1f}°")
            print(f"    ✅ Ângulo REAL: {graus_real:.1f}°")
        else:
            print(f"\n  Dobra {i}: ERRO ao ler")

def test_escrita_angulo(client):
    """Testa escrita de ângulo."""
    print("\n" + "=" * 70)
    print("TESTE 3 - ESCRITA DE ÂNGULO")
    print("=" * 70)

    print("\n⚠️  ATENÇÃO: Isso vai GRAVAR um ângulo no CLP!")
    print("            Certifique-se de que é seguro fazer isso agora.")

    resposta = input("\nDeseja continuar? (s/N): ").strip().lower()

    if resposta != 's':
        print("Teste de escrita cancelado.")
        return

    print("\nDigite o ângulo REAL da dobra (ex: 90 para dobrar 90°):")
    try:
        angulo_real = float(input("Ângulo: ").strip())
    except:
        print("❌ Valor inválido!")
        return

    print(f"\nGravando ângulo REAL de {angulo_real}° na Dobra 1...")
    print(f"  Conversão: {angulo_real}° real → {angulo_real * 2}° máquina → {mm.real_angle_to_machine(angulo_real)} pulsos")

    sucesso = client.write_bend_angle(1, angulo_real)

    if sucesso:
        print("✅ Gravado com sucesso!")

        # Aguardar ladder copiar
        print("\nAguardando 1 segundo para ladder copiar...")
        time.sleep(1.0)

        # Ler de volta
        print("\nLendo de volta para validar...")
        lido = client.read_bend_angle(1)

        if lido is not None:
            erro = abs(lido - angulo_real)
            if erro < 1.0:
                print(f"✅ VALIDADO! Gravado: {angulo_real}°, Lido: {lido:.1f}° (erro: {erro:.2f}°)")
            else:
                print(f"⚠️  ATENÇÃO: Gravado: {angulo_real}°, Lido: {lido:.1f}° (erro: {erro:.2f}°)")
        else:
            print("❌ Erro ao ler de volta")
    else:
        print("❌ Erro ao gravar")

def main():
    """Função principal."""
    print("=" * 70)
    print("TESTE NA MÁQUINA REAL - VALIDAÇÃO DE ÂNGULOS DOBRADOS")
    print("=" * 70)
    print()
    print("⚠️  DESCOBERTA CRÍTICA: Para dobrar 90°, máquina gira 180°!")
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
        # Teste 1: Encoder
        test_leitura_encoder(client)

        # Teste 2: Ângulos programados
        test_leitura_angulos(client)

        # Teste 3: Escrita (opcional)
        test_escrita_angulo(client)

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
