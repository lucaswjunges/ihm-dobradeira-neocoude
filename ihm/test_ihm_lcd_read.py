#!/usr/bin/env python3
"""
Test Script: Descobrir se conseguimos ler o estado da tela LCD da IHM física
Testa leitura de registros relacionados ao controle de display
"""

import sys
from pymodbus.client import ModbusSerialClient
import time

# Configuração Modbus
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 2
BYTESIZE = 8
SLAVE_ID = 1

# Registros a testar
REGISTROS_TELA = {
    'SCREEN_NUM': {'hex': '0FEC', 'dec': 4076, 'tipo': 'holding'},
    'LOAD_TRIGGER': {'hex': '00D7', 'dec': 215, 'tipo': 'coil'},
    'DISPLAY_OFF': {'hex': '00DB', 'dec': 219, 'tipo': 'coil'},
    'KEY_LOCKED': {'hex': '00D8', 'dec': 216, 'tipo': 'coil'},
    'VALUE_CHANGED': {'hex': '00DA', 'dec': 218, 'tipo': 'coil'},
    'COUNT_BLOCK': {'hex': '00D2', 'dec': 210, 'tipo': 'coil'},
}

# Área de registros próximos a 0FEC (explorar vizinhança)
AREA_EXPLORACAO = range(4070, 4090)  # 0FE6 - 0FFA

def conectar():
    """Conecta ao CLP via RS485"""
    print(f"🔌 Conectando ao CLP em {PORT}...")
    print(f"   Baudrate: {BAUDRATE}, Parity: {PARITY}, Stop bits: {STOPBITS}")

    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=BYTESIZE,
        timeout=1
    )

    if client.connect():
        print("✅ Conectado ao CLP\n")
        return client
    else:
        print("❌ ERRO: Não foi possível conectar ao CLP")
        print(f"   Verifique se o cabo USB-RS485 está em {PORT}")
        return None

def ler_coil(client, address, nome):
    """Lê um coil (bit) individual"""
    try:
        response = client.read_coils(address=address, count=1, device_id=SLAVE_ID)
        if not response.isError():
            valor = response.bits[0]
            print(f"  ✓ {nome:20s} (coil {address:4d}): {'ON' if valor else 'OFF'}")
            return valor
        else:
            print(f"  ✗ {nome:20s} (coil {address:4d}): ERRO - {response}")
            return None
    except Exception as e:
        print(f"  ✗ {nome:20s} (coil {address:4d}): EXCEÇÃO - {e}")
        return None

def ler_register(client, address, nome):
    """Lê um holding register individual"""
    try:
        response = client.read_holding_registers(address=address, count=1, device_id=SLAVE_ID)
        if not response.isError():
            valor = response.registers[0]
            print(f"  ✓ {nome:20s} (reg {address:4d}): {valor:5d} (0x{valor:04X})")
            return valor
        else:
            print(f"  ✗ {nome:20s} (reg {address:4d}): ERRO - {response}")
            return None
    except Exception as e:
        print(f"  ✗ {nome:20s} (reg {address:4d}): EXCEÇÃO - {e}")
        return None

def explorar_area(client, start, end):
    """Lê uma faixa de registros para explorar"""
    print(f"\n🔍 Explorando registros {start} a {end}...")
    resultados = {}

    for addr in range(start, end):
        try:
            response = client.read_holding_registers(address=addr, count=1, device_id=SLAVE_ID)
            if not response.isError():
                valor = response.registers[0]
                if valor != 0:  # Mostrar apenas não-zero
                    print(f"  • Reg {addr:4d} (0x{addr:04X}): {valor:5d} (0x{valor:04X})")
                    resultados[addr] = valor
            time.sleep(0.01)  # Pequeno delay entre leituras
        except:
            pass

    return resultados

def testar_mudanca_tela(client):
    """Testa se conseguimos detectar mudança de tela simulando tecla"""
    print("\n🧪 TESTE: Simulando mudança de tela (pressionar K1)")
    print("   Vamos ler 0FEC antes e depois de simular K1...")

    # Ler estado inicial
    print("\n📖 Estado ANTES:")
    inicial = ler_register(client, 4076, "SCREEN_NUM (0FEC)")

    # Simular K1 (vai para tela 4)
    print("\n⌨️  Simulando K1 (pulso 100ms)...")
    client.write_coil(address=160, value=True, device_id=SLAVE_ID)  # K1 ON
    time.sleep(0.1)
    client.write_coil(address=160, value=False, device_id=SLAVE_ID)  # K1 OFF

    # Aguardar processamento
    time.sleep(0.5)

    # Ler estado final
    print("\n📖 Estado DEPOIS:")
    final = ler_register(client, 4076, "SCREEN_NUM (0FEC)")

    if inicial is not None and final is not None:
        if inicial != final:
            print(f"\n✅ SUCESSO! Registro 0FEC mudou: {inicial} → {final}")
            print("   → Conseguimos DETECTAR mudança de tela via Modbus!")
        else:
            print(f"\n⚠️  Registro 0FEC não mudou (permaneceu {inicial})")
            print("   → Pode ser write-only OU tela já era a 4")

    return inicial, final

def main():
    print("=" * 70)
    print(" TESTE: Leitura do Estado da Tela LCD da IHM Física")
    print("=" * 70)

    client = conectar()
    if not client:
        sys.exit(1)

    try:
        # 1. Testar registros conhecidos
        print("\n" + "=" * 70)
        print("1️⃣  TESTANDO REGISTROS CONHECIDOS")
        print("=" * 70)

        for nome, info in REGISTROS_TELA.items():
            if info['tipo'] == 'coil':
                ler_coil(client, info['dec'], f"{nome} ({info['hex']})")
            else:
                ler_register(client, info['dec'], f"{nome} ({info['hex']})")

        # 2. Explorar área próxima a 0FEC
        print("\n" + "=" * 70)
        print("2️⃣  EXPLORANDO ÁREA PRÓXIMA A 0FEC")
        print("=" * 70)

        resultados = explorar_area(client, min(AREA_EXPLORACAO), max(AREA_EXPLORACAO))

        if resultados:
            print(f"\n✓ Encontrados {len(resultados)} registros não-zero na área")
        else:
            print("\n⚠️  Nenhum registro não-zero encontrado na área")

        # 3. Testar mudança de tela
        print("\n" + "=" * 70)
        print("3️⃣  TESTE DE MUDANÇA DE TELA")
        print("=" * 70)

        inicial, final = testar_mudanca_tela(client)

        # 4. Conclusões
        print("\n" + "=" * 70)
        print("📝 CONCLUSÕES")
        print("=" * 70)

        if inicial is not None:
            print(f"\n✓ Registro 0FEC é LEGÍVEL via Modbus")
            print(f"  Valor atual: {inicial} (0x{inicial:04X})")

            if inicial == final:
                print("\n⚠️  Registro não muda ao simular tecla:")
                print("  • Pode ser que ladder não escreve nele imediatamente")
                print("  • Pode ser que IHM física não estava conectada")
                print("  • Pode ser área de configuração, não estado dinâmico")
            else:
                print("\n✅ Registro MUDA ao simular tecla!")
                print("  → Podemos usar 0FEC para rastrear tela atual")
        else:
            print("\n❌ Registro 0FEC NÃO é legível")
            print("  → Precisamos de abordagem alternativa")

        print("\n💡 RECOMENDAÇÕES:")
        print("  1. Nossa IHM web deve manter estado local de navegação")
        print("  2. Sincronizar via dados (encoder, ângulos) ao invés de telas")
        print("  3. Replicar LÓGICA da IHM física, não o estado literal")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
        print("\n🔌 Desconectado do CLP")

if __name__ == "__main__":
    main()
