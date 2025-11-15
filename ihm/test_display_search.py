#!/usr/bin/env python3
"""
Busca por informações do display LCD da IHM física
Procura em múltiplas áreas de memória por:
1. Número da tela (0-10)
2. Texto ASCII do display
3. Registros relacionados à IHM
"""

from pymodbus.client import ModbusSerialClient
import sys

# Configuração Modbus
SLAVE_ID = 1

client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=57600,
    parity='N',
    stopbits=2,
    bytesize=8,
    timeout=1
)

# Configura slave ID padrão
client.slave_id = SLAVE_ID

if not client.connect():
    print("❌ Erro ao conectar com o CLP")
    sys.exit(1)

print("✅ Conectado ao CLP via Modbus RTU")
print("=" * 70)

# Áreas a testar (endereço inicial, quantidade, descrição)
areas_to_test = [
    (0x0FE0, 32, "Área 0x0FE0-0x0FFF (próxima ao 0x0FEC encontrado)"),
    (0x1000, 64, "Área 0x1000-0x103F (registros do sistema)"),
    (0x1980, 16, "Área 0x1980-0x198F (config comunicação)"),
    (0x0500, 32, "Área 0x0500-0x051F (setpoints ângulos iniciais)"),
    (0x0860, 32, "Área 0x0860-0x087F (proposta supervisão)"),
]

results = []

for start_addr, count, description in areas_to_test:
    print(f"\n🔍 Testando: {description}")
    print(f"   Endereços: 0x{start_addr:04X} - 0x{start_addr+count-1:04X} ({start_addr} - {start_addr+count-1} dec)")

    try:
        result = client.read_holding_registers(address=start_addr, count=count)

        if result.isError():
            print(f"   ❌ Erro: Illegal data address ou timeout")
            continue

        # Analisa os valores
        registers = result.registers

        # Busca valores pequenos (possível número de tela)
        small_values = [(i, val) for i, val in enumerate(registers) if 0 <= val <= 15]
        if small_values:
            print(f"   📌 Valores pequenos encontrados (0-15, possível nº tela):")
            for offset, val in small_values[:5]:  # Mostra primeiros 5
                addr = start_addr + offset
                print(f"      [{addr:04X}] ({addr:04d}): {val}")

        # Busca padrões ASCII (texto do display)
        ascii_sequences = []
        for i in range(0, len(registers), 8):
            chunk = registers[i:i+8]
            # Converte para bytes
            text = ""
            for reg in chunk:
                high_byte = (reg >> 8) & 0xFF
                low_byte = reg & 0xFF
                # Checa se são caracteres ASCII imprimíveis
                if 32 <= high_byte <= 126:
                    text += chr(high_byte)
                if 32 <= low_byte <= 126:
                    text += chr(low_byte)

            # Se conseguiu pelo menos 4 caracteres ASCII seguidos
            if len(text) >= 4:
                addr_start = start_addr + i
                ascii_sequences.append((addr_start, text))

        if ascii_sequences:
            print(f"   📝 Possível texto ASCII encontrado:")
            for addr, text in ascii_sequences[:3]:  # Mostra primeiras 3
                print(f"      [0x{addr:04X}]: '{text}'")

        # Procura por padrão específico: "TRILLOR" ou "DOBRADEIRA"
        full_text = ""
        for reg in registers:
            high_byte = (reg >> 8) & 0xFF
            low_byte = reg & 0xFF
            if 32 <= high_byte <= 126:
                full_text += chr(high_byte)
            if 32 <= low_byte <= 126:
                full_text += chr(low_byte)

        if "TRILLOR" in full_text.upper() or "DOBRA" in full_text.upper():
            print(f"   🎯 ENCONTRADO! Texto do display detectado:")
            print(f"      '{full_text[:50]}'...")
            results.append((start_addr, "TEXTO DO DISPLAY ENCONTRADO!"))

        # Mostra primeiros valores para referência
        if not small_values and not ascii_sequences:
            print(f"   ℹ️  Primeiros valores (hex): ", end="")
            print(" ".join([f"{reg:04X}" for reg in registers[:8]]))

    except Exception as e:
        print(f"   ⚠️  Exceção: {e}")

print("\n" + "=" * 70)
print("📊 RESUMO DOS RESULTADOS")
print("=" * 70)

if results:
    print("\n🎉 Informações do display ENCONTRADAS:")
    for addr, desc in results:
        print(f"   • Endereço 0x{addr:04X} ({addr} dec): {desc}")
else:
    print("\n❌ Nenhuma informação clara do display foi encontrada.")
    print("\n💡 CONCLUSÃO:")
    print("   O display LCD da IHM física (Atos 4004.95C) provavelmente:")
    print("   1. NÃO espelha o texto no CLP MPC4004")
    print("   2. Gera o texto localmente na própria IHM")
    print("   3. O CLP apenas envia COMANDOS (ex: 'mostrar tela 4')")
    print("   4. A IHM interpreta e gera o texto 'TRILLOR', 'DOBRADEIRA', etc")
    print("\n   Solução: IHM Web deve gerar o texto localmente, assim como a física!")

client.close()
print("\n✅ Teste concluído")
