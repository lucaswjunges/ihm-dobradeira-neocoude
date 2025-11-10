#!/usr/bin/env python3
"""
test_control_outputs.py
Testa ativação de saídas S0-S7 para descobrir qual controla cada função
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=" * 70)
print("TESTE DE ATIVAÇÃO DE SAÍDAS S0-S7")
print("=" * 70)
print("\n⚠️  IMPORTANTE:")
print("   - Motor 380V deve estar DESLIGADO")
print("   - Use multímetro para medir 24VDC nas saídas")
print("   - Cada saída será ativada por 2 segundos")
print()

input("Pressione Enter para iniciar testes...")

# Mapeamento de saídas (endereços Modbus)
# S0 = 384 (0x0180)
# S1 = 385 (0x0181)
# S2 = 386 (0x0182)
# S3 = 387 (0x0183)
# S4 = 388 (0x0184)
# S5 = 389 (0x0185)
# S6 = 390 (0x0186)
# S7 = 391 (0x0187)

outputs = [
    (384, "S0", "Função desconhecida"),
    (385, "S1", "Função desconhecida"),
    (386, "S2", "Função desconhecida"),
    (387, "S3", "Função desconhecida"),
    (388, "S4", "Função desconhecida"),
    (389, "S5", "Função desconhecida"),
    (390, "S6", "Função desconhecida"),
    (391, "S7", "Função desconhecida"),
]

print("\nIniciando teste sequencial...\n")

for addr, name, description in outputs:
    print("=" * 70)
    print(f"TESTANDO SAÍDA {name} (Endereço Modbus: {addr} / 0x{addr:04X})")
    print("=" * 70)

    # Ligar saída
    print(f"\n✓ Ativando {name}...")
    result = client.write_coil(addr, True)

    if result:
        print(f"→ {name} está LIGADA (ON)")
        print(f"\n📝 Meça com multímetro:")
        print(f"   - Ponta preta: GND do CLP")
        print(f"   - Ponta vermelha: Terminal {name}")
        print(f"   - Esperado: ~24VDC")
        print(f"\n   Anote o que aconteceu:")
        print(f"   → {name} controla: ____________________")

        # Manter ligado por 2 segundos
        for i in range(2, 0, -1):
            print(f"\r   Desligando em {i}s...", end='', flush=True)
            time.sleep(1)

        # Desligar saída
        client.write_coil(addr, False)
        print(f"\n✓ {name} desligada (OFF)\n")
        time.sleep(0.5)
    else:
        print(f"✗ ERRO ao ativar {name}")
        print()

print("\n" + "=" * 70)
print("TESTE CONCLUÍDO!")
print("=" * 70)
print("\nPreencha a tabela de mapeamento:\n")
print("| Saída | Endereço | Controla              | Para IHM Web    |")
print("|-------|----------|-----------------------|-----------------|")
for addr, name, _ in outputs:
    print(f"| {name:5s} | {addr:4d}     | _____________________ | _______________ |")
print()
print("Sugestões do que procurar:")
print("  - Contatores energizando")
print("  - LEDs acendendo")
print("  - Relés clicando")
print("  - Sinalizadores")
print()
