#!/usr/bin/env python3
"""
MODBUS SCANNER AVANÇADO
========================
Testa múltiplos slave addresses e varre range completo de registros.
"""
import time
import sys
from pymodbus.client import ModbusSerialClient

# Configurações
PORT = "/dev/ttyUSB0"
BAUDRATE = 57600
TIMEOUT = 1.0

# Ranges para testar
SLAVE_ADDRESSES = [1, 2, 3, 4, 5, 10]  # Testar vários IDs
REGISTER_RANGES = [
    (0x0000, 0x0100, "Área de Estados (0x0000-0x00FF)"),
    (0x0100, 0x0108, "Digital I/O Status (0x0100-0x0107)"),
    (0x0400, 0x0480, "Timer/Counter (0x0400-0x047F)"),
    (0x04D0, 0x04E0, "High-Speed Counter (0x04D0-0x04DF) - ENCODER ESPERADO"),
    (0x0500, 0x0540, "Angle Setpoints (0x0500-0x053F)"),
    (0x1980, 0x1990, "Communication Config (0x1980-0x198F)"),
]

def test_read(client, slave_id, address, count=1, fc=3):
    """Tenta ler registros com uma função específica."""
    try:
        if fc == 3:  # HOLDING REGISTERS
            result = client.read_holding_registers(address, count=count, slave=slave_id)
        elif fc == 4:  # INPUT REGISTERS
            result = client.read_input_registers(address, count=count, slave=slave_id)
        else:
            return None

        if not result.isError():
            return result.registers
        return None
    except Exception as e:
        return None

def scan_slave(client, slave_id):
    """Varre todos os ranges para um slave específico."""
    print(f"\n{'='*80}")
    print(f"TESTANDO SLAVE ID: {slave_id}")
    print(f"{'='*80}\n")

    found_any = False

    for start, end, description in REGISTER_RANGES:
        count = end - start

        print(f"\n📍 {description}")
        print(f"   Range: 0x{start:04X} até 0x{end:04X} ({start} até {end} decimal)")
        print(f"   Total: {count} registros")

        # Testar HOLDING REGISTERS (FC 0x03)
        print(f"\n   Testando HOLDING REGISTERS (FC 0x03)...")
        registers = test_read(client, slave_id, start, count, fc=3)

        if registers:
            print(f"   ✓ SUCESSO! Lidos {len(registers)} registros")
            # Mostrar primeiros 8 valores
            print(f"   Valores: ", end="")
            for i, val in enumerate(registers[:8]):
                print(f"[{start+i:04X}]={val:04X} ", end="")
            if len(registers) > 8:
                print("...")
            else:
                print()
            found_any = True
        else:
            print(f"   ✗ Falha ao ler")

        # Testar INPUT REGISTERS (FC 0x04)
        print(f"   Testando INPUT REGISTERS (FC 0x04)...")
        registers = test_read(client, slave_id, start, count, fc=4)

        if registers:
            print(f"   ✓ SUCESSO! Lidos {len(registers)} registros")
            print(f"   Valores: ", end="")
            for i, val in enumerate(registers[:8]):
                print(f"[{start+i:04X}]={val:04X} ", end="")
            if len(registers) > 8:
                print("...")
            else:
                print()
            found_any = True
        else:
            print(f"   ✗ Falha ao ler")

    return found_any

def main():
    print("="*80)
    print("MODBUS SCANNER AVANÇADO")
    print("="*80)
    print(f"\n🔌 Conectando em {PORT} @ {BAUDRATE} bps...")

    # Conectar ao Modbus
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=TIMEOUT
    )

    if not client.connect():
        print(f"✗ ERRO: Não foi possível conectar em {PORT}")
        return 1

    print(f"✓ Modbus conectado!")

    # Testar cada slave address
    slaves_found = []

    for slave_id in SLAVE_ADDRESSES:
        if scan_slave(client, slave_id):
            slaves_found.append(slave_id)

    # Resumo
    print("\n" + "="*80)
    print("RESUMO")
    print("="*80)

    if slaves_found:
        print(f"\n✓ Slave IDs que responderam: {slaves_found}")
        print("\nPróximo passo:")
        print("  1. Use o slave ID que respondeu")
        print("  2. Gire o eixo e veja qual registro muda")
        print("  3. Esse será o endereço do encoder!")
    else:
        print("\n✗ NENHUM slave respondeu!")
        print("\nPossíveis problemas:")
        print("  1. Slave address não está na lista testada")
        print("  2. Baudrate incorreto (testamos 57600)")
        print("  3. Estado 00BE (Modbus slave) não está habilitado no CLP")
        print("  4. Problema na comunicação RS485 (A/B invertidos, sem GND)")
        print("\nSugestões:")
        print("  • Verificar estado 00BE no ladder (deve estar ON)")
        print("  • Ler registro 0x1988 (6536) para ver slave address real")
        print("  • Testar baudrates: 9600, 19200, 38400, 57600, 115200")

    client.close()
    print("\n✓ Conexão fechada")

    return 0 if slaves_found else 1

if __name__ == "__main__":
    sys.exit(main())
