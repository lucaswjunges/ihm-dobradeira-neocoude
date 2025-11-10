#!/usr/bin/env python3
"""
test_outputs_safe.py
Ativa saídas digitais uma por vez para identificação SEGURA
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=" * 60)
print("TESTE DE SAÍDAS DIGITAIS (S0-S7) - MODO SEGURO")
print("=" * 60)
print("\n⚠️  ATENÇÃO:")
print("   - Este teste ATIVA saídas físicas")
print("   - Motor 380V DEVE estar DESLIGADO")
print("   - Observe LEDs, relés, contatores")
print("   - Anote o que cada saída controla")
print()

input("Confirme que 380V do motor está DESLIGADO. Pressione Enter para continuar...")

print("\nIniciando teste sequencial das saídas...\n")

for i in range(8):
    print("=" * 60)
    print(f"TESTE DA SAÍDA S{i} (Endereço Modbus: {384 + i})")
    print("=" * 60)

    # Ligar saída
    print(f"\n✓ Ligando S{i}...")
    result = client.write_coil(384 + i, True)

    if result and not result.isError():
        print(f"→ S{i} está LIGADA (ON)")
        print(f"\nObserve:")
        print(f"  - LEDs no painel?")
        print(f"  - Relés energizando (clique)?")
        print(f"  - Contatores?")
        print(f"  - Outros indicadores?")
        print(f"\n📝 Anote o que aconteceu:")
        print(f"   S{i} controla: ____________________")

        input("\nPressione Enter para DESLIGAR e continuar...")

        # Desligar saída
        client.write_coil(384 + i, False)
        print(f"✓ S{i} desligada (OFF)\n")
        time.sleep(0.5)
    else:
        print(f"✗ ERRO ao ativar S{i}: {result}")

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO!")
print("=" * 60)
print("\nRevise suas anotações e preencha a tabela:")
print()
print("| Saída | Controla              | Observações        |")
print("|-------|-----------------------|--------------------|")
for i in range(8):
    print(f"| S{i}    | _____________________ | __________________ |")
print()
