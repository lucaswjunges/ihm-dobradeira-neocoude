#!/usr/bin/env python3
"""
Diagnóstico automático de comunicação Modbus com CLP Atos
Testa diferentes combinações de parâmetros até encontrar a configuração correta
"""

from pymodbus.client import ModbusSerialClient
import time

print("=" * 70)
print("DIAGNÓSTICO AUTOMÁTICO - CLP ATOS MPC4004")
print("=" * 70)
print()

# Configurações a testar
SLAVE_IDS = [1, 2, 3, 4, 5]
BAUDRATES = [57600, 38400, 19200, 9600]
PARITIES = ['N', 'E', 'O']
STOP_BITS = [1, 2]

# Endereços para testar (mais simples primeiro)
TEST_ADDRESSES = [
    {'type': 'holding', 'addr': 0, 'count': 1, 'desc': 'Holding Register 0'},
    {'type': 'holding', 'addr': 1, 'count': 1, 'desc': 'Holding Register 1'},
    {'type': 'input', 'addr': 0, 'count': 1, 'desc': 'Input Register 0'},
    {'type': 'input', 'addr': 1238, 'count': 2, 'desc': 'Encoder (0x04D6)'},
    {'type': 'coil', 'addr': 0, 'count': 8, 'desc': 'Coils 0-7'},
]

def test_connection(port, slave_id, baudrate, parity, stopbits):
    """Testa uma combinação específica de parâmetros"""
    try:
        client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=8,
            timeout=0.5  # Timeout curto para diagnóstico rápido
        )

        if not client.connect():
            return None

        # Testa leitura simples
        result = client.read_holding_registers(address=0, count=1, slave=slave_id)

        client.close()

        if not result.isError():
            return True

    except Exception:
        pass

    return None

def deep_test(port, slave_id, baudrate, parity, stopbits):
    """Testa vários tipos de leitura com uma configuração específica"""
    print(f"\n{'='*70}")
    print(f"TESTANDO CONFIGURAÇÃO:")
    print(f"  Slave ID: {slave_id}")
    print(f"  Baudrate: {baudrate}")
    print(f"  Parity: {parity}")
    print(f"  Stop bits: {stopbits}")
    print(f"{'='*70}")

    try:
        client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=8,
            timeout=1.0
        )

        if not client.connect():
            print("❌ Não conseguiu conectar na porta serial")
            return False

        print("✅ Conexão serial OK")
        success_count = 0

        for test in TEST_ADDRESSES:
            try:
                if test['type'] == 'holding':
                    result = client.read_holding_registers(
                        address=test['addr'],
                        count=test['count'],
                        slave=slave_id
                    )
                elif test['type'] == 'input':
                    result = client.read_input_registers(
                        address=test['addr'],
                        count=test['count'],
                        slave=slave_id
                    )
                elif test['type'] == 'coil':
                    result = client.read_coils(
                        address=test['addr'],
                        count=test['count'],
                        slave=slave_id
                    )

                if not result.isError():
                    print(f"  ✅ {test['desc']}: {result.registers if hasattr(result, 'registers') else result.bits[:test['count']]}")
                    success_count += 1
                else:
                    print(f"  ❌ {test['desc']}: ERRO")

            except Exception as e:
                print(f"  ❌ {test['desc']}: Exceção - {e}")

            time.sleep(0.1)

        client.close()

        if success_count > 0:
            print(f"\n🎉 SUCESSO! {success_count}/{len(TEST_ADDRESSES)} leituras funcionaram!")
            print(f"\n{'='*70}")
            print("CONFIGURAÇÃO CORRETA ENCONTRADA:")
            print(f"  slave_id = {slave_id}")
            print(f"  baudrate = {baudrate}")
            print(f"  parity = '{parity}'")
            print(f"  stopbits = {stopbits}")
            print(f"{'='*70}")
            return True

        return False

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

# FASE 1: Busca rápida
print("FASE 1: Busca rápida (testando configurações mais comuns)...")
print()

port = '/dev/ttyUSB0'
found = False

# Testar configurações mais comuns primeiro
common_configs = [
    (1, 57600, 'N', 1),
    (1, 57600, 'E', 1),
    (1, 57600, 'N', 2),
    (1, 38400, 'N', 1),
    (1, 19200, 'N', 1),
    (2, 57600, 'N', 1),
]

for slave_id, baudrate, parity, stopbits in common_configs:
    config_str = f"ID={slave_id}, {baudrate}bps, parity={parity}, stop={stopbits}"
    print(f"  Testando {config_str}...", end=' ')

    if test_connection(port, slave_id, baudrate, parity, stopbits):
        print("✅ RESPOSTA!")
        found = True
        # Teste detalhado
        if deep_test(port, slave_id, baudrate, parity, stopbits):
            exit(0)
    else:
        print("❌")

    time.sleep(0.1)

if not found:
    print("\n❌ Nenhuma configuração comum funcionou")
    print("\nFASE 2: Busca completa (pode demorar alguns minutos)...")
    print()

    # Busca exaustiva
    total = len(SLAVE_IDS) * len(BAUDRATES) * len(PARITIES) * len(STOP_BITS)
    current = 0

    for slave_id in SLAVE_IDS:
        for baudrate in BAUDRATES:
            for parity in PARITIES:
                for stopbits in STOP_BITS:
                    current += 1
                    config_str = f"ID={slave_id}, {baudrate}bps, {parity}, {stopbits}"
                    print(f"  [{current}/{total}] {config_str}...", end=' ')

                    if test_connection(port, slave_id, baudrate, parity, stopbits):
                        print("✅ RESPOSTA!")
                        if deep_test(port, slave_id, baudrate, parity, stopbits):
                            exit(0)
                    else:
                        print("❌")

                    time.sleep(0.1)

print("\n" + "=" * 70)
print("❌ FALHA: CLP não respondeu a NENHUMA configuração testada")
print("=" * 70)
print("\nPossíveis causas:")
print("  1. CLP está DESLIGADO")
print("  2. CLP não está em modo RUN")
print("  3. Estado 00BE (Modbus slave) não está ativado no ladder")
print("  4. Cabo RS485 com A/B invertidos")
print("  5. Cabo RS485 com defeito")
print("  6. Adaptador USB-RS485 com defeito")
print("\nSoluções:")
print("  1. Verifique se o CLP está LIGADO e com LED verde")
print("  2. Coloque o CLP em modo RUN (não STOP/PROG)")
print("  3. Abra o ladder e verifique se bit 00BE está ON")
print("  4. Inverta os fios A e B do RS485")
print("  5. Teste com outro cabo ou adaptador")
print("=" * 70)
