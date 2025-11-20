#!/usr/bin/env python3
"""
Cliente Modbus RTU simplificado para CLP ATOS MPC4004
Lê dados do CLP em tempo real
"""

import sys
import time
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configuração Modbus (descoberta pelo diagnóstico)
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 1  # Ou 2, ambos funcionam
SLAVE_ID = 1

# Cores
class C:
    G = '\033[92m'  # Green
    R = '\033[91m'  # Red
    Y = '\033[93m'  # Yellow
    B = '\033[94m'  # Blue
    W = '\033[97m'  # White
    X = '\033[0m'   # Reset

def create_client():
    """Cria e conecta cliente Modbus"""
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=8,
        timeout=1
    )

    if not client.connect():
        print(f"{C.R}✗ Erro ao conectar em {PORT}{C.X}")
        return None

    return client

def read_encoder(client):
    """Lê valor do encoder (registros 1238-1239)"""
    try:
        result = client.read_holding_registers(
            address=1238,
            count=2,
            slave=SLAVE_ID
        )

        if result.isError():
            return None, f"Erro: {result}"

        # Combinar MSW e LSW em valor 32-bit
        msw = result.registers[0]
        lsw = result.registers[1]
        value_32 = (msw << 16) | lsw

        return value_32, None

    except Exception as e:
        return None, str(e)

def read_digital_inputs(client):
    """Lê entradas digitais E0-E7 (registros 256-263)"""
    try:
        result = client.read_holding_registers(
            address=256,
            count=8,
            slave=SLAVE_ID
        )

        if result.isError():
            return None

        # Extrair bit 0 de cada registro
        inputs = [reg & 0x01 for reg in result.registers]
        return inputs

    except:
        return None

def read_digital_outputs(client):
    """Lê saídas digitais S0-S7 (registros 384-391)"""
    try:
        result = client.read_holding_registers(
            address=384,
            count=8,
            slave=SLAVE_ID
        )

        if result.isError():
            return None

        # Extrair bit 0 de cada registro
        outputs = [reg & 0x01 for reg in result.registers]
        return outputs

    except:
        return None

def display_ios(inputs, outputs):
    """Exibe entradas e saídas em formato visual"""
    if inputs is None or outputs is None:
        return

    # Entradas
    print(f"\n{C.B}Entradas E0-E7:{C.X}", end="")
    for i, val in enumerate(inputs):
        color = C.G if val else C.W
        symbol = "●" if val else "○"
        print(f"  E{i}:{color}{symbol}{C.X}", end="")

    # Saídas
    print(f"\n{C.Y}Saídas  S0-S7:{C.X}", end="")
    for i, val in enumerate(outputs):
        color = C.G if val else C.W
        symbol = "●" if val else "○"
        print(f"  S{i}:{color}{symbol}{C.X}", end="")

    print()

def main():
    print(f"{C.B}{'='*70}")
    print("CLIENTE MODBUS RTU - CLP ATOS MPC4004")
    print(f"{'='*70}{C.X}\n")

    print(f"{C.W}Configuração:{C.X}")
    print(f"  Porta: {PORT}")
    print(f"  Baudrate: {BAUDRATE}")
    print(f"  Parity: {PARITY}")
    print(f"  Stopbits: {STOPBITS}")
    print(f"  Slave ID: {SLAVE_ID}\n")

    # Conectar
    print(f"{C.Y}Conectando...{C.X}")
    client = create_client()

    if client is None:
        return 1

    print(f"{C.G}✓ Conectado!{C.X}\n")
    print(f"{C.W}Lendo dados (Ctrl+C para parar)...{C.X}")
    print(f"{C.B}{'─'*70}{C.X}")

    try:
        while True:
            # Ler encoder
            encoder, error = read_encoder(client)

            if error:
                print(f"{C.R}✗ Erro ao ler encoder: {error}{C.X}")
                time.sleep(1)
                continue

            # Ler I/Os
            inputs = read_digital_inputs(client)
            outputs = read_digital_outputs(client)

            # Limpar linha anterior (ANSI escape)
            print("\033[F" * 5, end="")  # Voltar 5 linhas

            # Display
            print(f"\n{C.G}Encoder (1238-1239):{C.X} {encoder:10d} pulsos (0x{encoder:08X})")
            display_ios(inputs, outputs)
            print(f"{C.B}{'─'*70}{C.X}")

            time.sleep(0.5)  # Atualizar a cada 500ms

    except KeyboardInterrupt:
        print(f"\n\n{C.Y}Interrompido pelo usuário{C.X}")

    finally:
        client.close()
        print(f"{C.G}✓ Conexão fechada{C.X}\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
