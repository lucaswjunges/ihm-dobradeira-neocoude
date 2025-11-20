#!/usr/bin/env python3
"""
Script de diagnóstico de conexão Modbus com CLP Atos
Testa múltiplas configurações para encontrar a correta
"""

import serial
import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configurações para testar
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATES = [57600, 19200, 9600, 115200]
SLAVE_IDS = [1, 2, 247]  # 247 é o máximo permitido
PARITIES = ['N', 'E', 'O']
STOPBITS = [1, 2]

# Registro de teste (encoder - deve sempre existir)
TEST_ADDRESS = 1238  # 0x04D6
TEST_COUNT = 2

print("=" * 60)
print(" DIAGNÓSTICO DE CONEXÃO MODBUS - CLP ATOS")
print("=" * 60)
print()

# Teste 1: Verificar se porta serial existe e pode ser aberta
print("[Teste 1] Verificando porta serial...")
try:
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=57600,
        parity='N',
        stopbits=2,
        bytesize=8,
        timeout=1
    )
    print(f"✓ Porta {SERIAL_PORT} aberta com sucesso")
    print(f"  Configuração: {ser}")
    ser.close()
except Exception as e:
    print(f"✗ Erro ao abrir porta: {e}")
    exit(1)

print()

# Teste 2: Scan de configurações
print("[Teste 2] Testando combinações de configurações...")
print()

sucesso = False
config_ok = None

for baudrate in BAUDRATES:
    if sucesso:
        break

    for parity in PARITIES:
        if sucesso:
            break

        for stopbits in STOPBITS:
            if sucesso:
                break

            for slave_id in SLAVE_IDS:
                print(f"Testando: Baudrate={baudrate}, Parity={parity}, "
                      f"Stopbits={stopbits}, Slave={slave_id}... ", end="", flush=True)

                client = None
                try:
                    client = ModbusSerialClient(
                        port=SERIAL_PORT,
                        baudrate=baudrate,
                        parity=parity,
                        stopbits=stopbits,
                        bytesize=8,
                        timeout=1
                    )

                    if client.connect():
                        # Tentar ler encoder
                        result = client.read_holding_registers(
                            address=TEST_ADDRESS,
                            count=TEST_COUNT,
                            slave=slave_id
                        )

                        if not result.isError():
                            print(f"✓ SUCESSO!")
                            print(f"  Valores lidos: {result.registers}")
                            sucesso = True
                            config_ok = {
                                'baudrate': baudrate,
                                'parity': parity,
                                'stopbits': stopbits,
                                'slave_id': slave_id
                            }
                            break
                        else:
                            print(f"✗ Erro Modbus")
                    else:
                        print(f"✗ Conexão falhou")

                except Exception as e:
                    print(f"✗ Exceção: {str(e)[:50]}")

                finally:
                    if client is not None:
                        try:
                            client.close()
                        except:
                            pass

                time.sleep(0.1)  # Delay entre tentativas

print()

if sucesso:
    print("=" * 60)
    print(" CONFIGURAÇÃO ENCONTRADA!")
    print("=" * 60)
    print(f"  Baudrate:  {config_ok['baudrate']}")
    print(f"  Parity:    {config_ok['parity']}")
    print(f"  Stop bits: {config_ok['stopbits']}")
    print(f"  Slave ID:  {config_ok['slave_id']}")
    print()

    # Teste adicional: ler área 0x0A00
    print("[Teste 3] Testando leitura da área 0x0A00...")
    client = ModbusSerialClient(
        port=SERIAL_PORT,
        baudrate=config_ok['baudrate'],
        parity=config_ok['parity'],
        stopbits=config_ok['stopbits'],
        bytesize=8,
        timeout=2
    )

    if client.connect():
        result = client.read_holding_registers(
            address=2560,  # 0x0A00
            count=6,
            slave=config_ok['slave_id']
        )

        if not result.isError():
            print(f"✓ Área 0x0A00 lida com sucesso:")
            for i, val in enumerate(result.registers):
                print(f"  [0x{2560+i:04X}] = {val}")
        else:
            print(f"✗ Erro ao ler área 0x0A00: {result}")

        client.close()

    print()
    print("Comando mbpoll equivalente:")
    parity_map = {'N': 'none', 'E': 'even', 'O': 'odd'}
    print(f"  mbpoll -a {config_ok['slave_id']} -r {TEST_ADDRESS} -c 2 "
          f"-t 4 -b {config_ok['baudrate']} -P {parity_map[config_ok['parity']]} "
          f"-s {config_ok['stopbits']} {SERIAL_PORT}")

else:
    print("=" * 60)
    print(" NENHUMA CONFIGURAÇÃO FUNCIONOU")
    print("=" * 60)
    print()
    print("Possíveis causas:")
    print("  1. CLP não está ligado")
    print("  2. Cabo RS485 invertido (A/B trocados)")
    print("  3. Bit 0x00BE não está habilitado no ladder")
    print("  4. CLP usando baudrate/configuração diferente")
    print("  5. Problema no conversor USB-RS485")
    print()
    print("Próximos passos:")
    print("  1. Verificar LED do conversor RS485")
    print("  2. Verificar ladder do CLP (registros 0x1987, 0x1988)")
    print("  3. Testar com outro conversor/cabo")
