#!/usr/bin/env python3
"""
Script de Diagnóstico Modbus RTU
Testa várias configurações para encontrar a correta
"""

import sys
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import time

# Cores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

def test_configuration(port, baudrate, parity, stopbits, bytesize, slave_id, register):
    """Testa uma configuração específica de Modbus"""

    config_str = f"Port={port}, Baud={baudrate}, Parity={parity}, Stop={stopbits}, Slave={slave_id}"

    try:
        # Criar cliente Modbus
        client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=1  # 1 segundo timeout
        )

        # Conectar
        if not client.connect():
            print_error(f"{config_str} - Falha ao conectar")
            return False

        # Tentar ler registro
        result = client.read_holding_registers(
            address=register,
            count=2,
            slave=slave_id
        )

        # Verificar resultado
        if result.isError():
            print_error(f"{config_str} - Erro: {result}")
            client.close()
            return False

        # Sucesso!
        print_success(f"{config_str} - SUCESSO!")
        print(f"  Registro {register}: {result.registers[0]} (0x{result.registers[0]:04X})")
        print(f"  Registro {register+1}: {result.registers[1]} (0x{result.registers[1]:04X})")

        # Calcular valor 32-bit (MSW << 16 | LSW)
        value_32bit = (result.registers[0] << 16) | result.registers[1]
        print(f"  Valor 32-bit: {value_32bit} (0x{value_32bit:08X})")

        client.close()
        return True

    except Exception as e:
        print_error(f"{config_str} - Exceção: {e}")
        return False

def main():
    print("=" * 70)
    print("DIAGNÓSTICO MODBUS RTU - CLP ATOS MPC4004")
    print("=" * 70)
    print()

    # Configurações fixas
    PORT = '/dev/ttyUSB0'
    REGISTER = 1238  # Encoder MSW

    # Configurações para testar
    configurations = [
        # (baudrate, parity, stopbits, bytesize, slave_ids)
        (57600, 'N', 2, 8, [1, 2, 3, 4, 5]),  # None, 2 stop
        (57600, 'N', 1, 8, [1, 2, 3, 4, 5]),  # None, 1 stop
        (57600, 'E', 1, 8, [1, 2, 3, 4, 5]),  # Even, 1 stop
        (57600, 'O', 1, 8, [1, 2, 3, 4, 5]),  # Odd, 1 stop
        (19200, 'N', 1, 8, [1]),              # Baudrate diferente
        (9600,  'N', 1, 8, [1]),              # Baudrate diferente
    ]

    print_info(f"Porta serial: {PORT}")
    print_info(f"Registro teste: {REGISTER} (encoder MSW)")
    print()

    found = False

    for baudrate, parity, stopbits, bytesize, slave_ids in configurations:
        print(f"\n{Colors.BLUE}━━━ Testando: Baud={baudrate}, Parity={parity}, Stop={stopbits} ━━━{Colors.RESET}")

        for slave_id in slave_ids:
            if test_configuration(PORT, baudrate, parity, stopbits, bytesize, slave_id, REGISTER):
                found = True
                print()
                print_success("CONFIGURAÇÃO ENCONTRADA!")
                print(f"  Baudrate: {baudrate}")
                print(f"  Parity: {parity}")
                print(f"  Stopbits: {stopbits}")
                print(f"  Slave ID: {slave_id}")

                # Não parar, continuar testando para ver se há mais respostas
                # return 0

            time.sleep(0.1)  # Pequeno delay entre tentativas

    print()
    print("=" * 70)
    if found:
        print_success("Teste concluído - configuração(ões) encontrada(s)!")
    else:
        print_error("Nenhuma configuração funcionou!")
        print()
        print_warning("Possíveis problemas:")
        print("  1. CLP não está ligado")
        print("  2. Cabo RS485 desconectado ou invertido (A↔B)")
        print("  3. Estado 00BE (Modbus slave) não está ativo no CLP")
        print("  4. Conversor USB-RS485 com defeito")
        print("  5. Terminação RS485 ausente (resistor 120Ω)")
    print("=" * 70)

    return 0 if found else 1

if __name__ == "__main__":
    sys.exit(main())
