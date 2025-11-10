#!/usr/bin/env python3
"""
Teste básico de comunicação com o CLP Atos MPC4004
Tenta ler o slave ID e alguns registros básicos
"""

from pymodbus.client import ModbusSerialClient
import time

# Configuração serial conforme manual do CLP
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'  # None
STOPBITS = 2  # CRITICAL: Atos MPC4004 requires 2 stop bits!
BYTESIZE = 8
TIMEOUT = 1.0

# Testar com diferentes slave IDs comuns
SLAVE_IDS_TO_TEST = [1, 2, 3, 4, 5, 10, 247]

print("=" * 60)
print("TESTE DE COMUNICAÇÃO COM CLP ATOS MPC4004")
print("=" * 60)
print(f"Porta: {PORT}")
print(f"Configuração: {BAUDRATE} {BYTESIZE}{PARITY}{STOPBITS}")
print(f"Timeout: {TIMEOUT}s")
print()

# Criar cliente Modbus
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=BYTESIZE,
    timeout=TIMEOUT
)

print("Conectando à porta serial...")
if not client.connect():
    print("❌ ERRO: Não foi possível abrir a porta serial!")
    print("Verifique:")
    print("  - Se o cabo USB está conectado")
    print("  - Se você está no grupo 'dialout': groups | grep dialout")
    print("  - Se a porta está correta: ls -la /dev/ttyUSB*")
    exit(1)

print("✓ Porta serial aberta com sucesso!")
print()

# Testar comunicação com diferentes slave IDs
found_slave = None

for slave_id in SLAVE_IDS_TO_TEST:
    print(f"Testando Slave ID: {slave_id}")

    try:
        # Tentar ler o registro do slave ID (endereço 6536 = 1988h)
        result = client.read_holding_registers(
            address=6536,
            count=1,
            device_id=slave_id
        )

        if not result.isError():
            print(f"  ✓ RESPOSTA! Slave ID {slave_id} está respondendo!")
            print(f"  Registro 6536 (slave ID armazenado): {result.registers[0]}")
            found_slave = slave_id

            # Tentar ler encoder (registros 1238/1239)
            print(f"  Tentando ler encoder (regs 1238-1239)...")
            result2 = client.read_holding_registers(
                address=1238,
                count=2,
                device_id=slave_id
            )

            if not result2.isError():
                msw = result2.registers[0]
                lsw = result2.registers[1]
                encoder_value = (msw << 16) | lsw
                print(f"  ✓ Encoder MSW: {msw}, LSW: {lsw}")
                print(f"  ✓ Valor do encoder: {encoder_value}")
            else:
                print(f"  ⚠ Encoder não lido: {result2}")

            # Tentar ler entradas digitais E0-E7 (registros 256-263)
            print(f"  Tentando ler entradas E0-E7 (regs 256-263)...")
            result3 = client.read_holding_registers(
                address=256,
                count=8,
                device_id=slave_id
            )

            if not result3.isError():
                print(f"  ✓ Entradas digitais:")
                for i, val in enumerate(result3.registers):
                    estado = "ON" if (val & 0x01) else "OFF"
                    print(f"    E{i}: {estado} (raw: {val})")
            else:
                print(f"  ⚠ Entradas não lidas: {result3}")

            break
        else:
            print(f"  - Sem resposta (timeout ou erro)")

        time.sleep(0.1)  # Pequeno delay entre tentativas

    except Exception as e:
        print(f"  ❌ Erro: {e}")

print()
print("=" * 60)

if found_slave:
    print(f"✓ COMUNICAÇÃO OK com Slave ID: {found_slave}")
    print()
    print("Configure o WinSUP com:")
    print(f"  - Slave ID: {found_slave}")
    print(f"  - Baudrate: {BAUDRATE}")
    print(f"  - Paridade: Nenhuma")
    print(f"  - Stop bits: {STOPBITS}")
else:
    print("❌ NENHUM CLP RESPONDEU!")
    print()
    print("Possíveis causas:")
    print("  1. CLP não está ligado ou energizado")
    print("  2. Cabo RS485 com A/B invertido")
    print("  3. Baudrate diferente (tente 9600, 19200)")
    print("  4. Estado 00BE (190 dec) não está ativado no CLP")
    print("  5. CLP configurado com stop bits = 2")
    print()
    print("Tente novamente com 2 stop bits:")
    print("  python3 test_2stopbits.py")

print("=" * 60)

client.close()
