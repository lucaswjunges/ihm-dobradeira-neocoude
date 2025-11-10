#!/usr/bin/env python3
"""
test_find_angles.py
Busca registradores que podem conter ângulos programados
"""

from modbus_client import ModbusClient, ModbusConfig
import time

config = ModbusConfig(port='/dev/ttyUSB0')
client = ModbusClient(stub_mode=False, config=config)

print("=" * 70)
print("BUSCA DE REGISTRADORES DE ÂNGULOS")
print("=" * 70)
print("\nProcurando valores entre 0-360 que podem ser ângulos programados...")
print("Aguarde...\n")

# Áreas de memória para buscar (baseado no manual MPC4004)
search_ranges = [
    (1280, 1343, "Setpoints de Ângulos (0500h-053Fh)"),
    (1024, 1151, "Timers/Counters (0400h-047Fh)"),
    (1232, 1247, "High-Speed Counter Area (04D0h-04DFh)"),
]

candidates = []

for start, end, description in search_ranges:
    print(f"\n{'=' * 70}")
    print(f"Área: {description}")
    print(f"Registradores: {start}-{end} (0x{start:04X}-0x{end:04X})")
    print(f"{'=' * 70}\n")

    found_in_range = 0

    for addr in range(start, end + 1):
        try:
            result = client.read_holding_registers(addr, 1)

            if result and not result.isError():
                value = result.registers[0]

                # Critérios para ser candidato a ângulo:
                # 1. Valor entre 0 e 360 (ângulos válidos)
                # 2. OU valores múltiplos de 5/10 (comuns em setpoints)
                # 3. OU valores terminados em 0 ou 5
                is_angle_range = 0 <= value <= 360
                is_round_number = (value % 5 == 0) or (value % 10 == 0)
                is_common_angle = value in [0, 15, 30, 45, 60, 90, 120, 135, 180, 270, 360]

                if is_angle_range and (value > 0):
                    score = 0
                    if is_round_number:
                        score += 1
                    if is_common_angle:
                        score += 2

                    print(f"Reg {addr:4d} (0x{addr:04X}): {value:5d}° "
                          f"{'⭐' * score if score > 0 else ''}")

                    candidates.append({
                        'address': addr,
                        'value': value,
                        'score': score,
                        'range': description
                    })
                    found_in_range += 1

            time.sleep(0.01)  # Evitar sobrecarregar comunicação

        except Exception as e:
            print(f"Erro ao ler registrador {addr}: {e}")

    if found_in_range == 0:
        print("  (Nenhum candidato encontrado nesta área)")

# Resumo ordenado por score
print("\n" + "=" * 70)
print("RESUMO - MELHORES CANDIDATOS (ordenado por relevância)")
print("=" * 70)

if candidates:
    # Ordenar por score (maior primeiro)
    candidates.sort(key=lambda x: x['score'], reverse=True)

    print("\n| Endereço | Hex    | Valor | Score | Observação          |")
    print("|----------|--------|-------|-------|---------------------|")

    for c in candidates[:20]:  # Top 20
        stars = '⭐' * c['score'] if c['score'] > 0 else ''
        print(f"| {c['address']:4d}     | 0x{c['address']:04X} | {c['value']:3d}°  | {stars:5s} | {c['range'][:20]:20s}|")

    print("\n📝 PRÓXIMOS PASSOS:")
    print("  1. Anote os endereços mais promissores (com ⭐)")
    print("  2. Use a IHM física para ver ângulos programados atuais")
    print("  3. Compare com valores encontrados aqui")
    print("  4. Teste escrita em candidatos (script test_write_angle.py)")
else:
    print("\nNenhum candidato encontrado. Tente:")
    print("  1. Verificar se há ângulos programados na IHM física")
    print("  2. Programar ângulos conhecidos (ex: 90°, 45°)")
    print("  3. Rodar este script novamente")

print("\n" + "=" * 70)

# Sugestão de próximo teste
print("\nPara testar se um registrador controla ângulos:")
print("  1. Anote valor atual do registrador")
print("  2. Escreva valor de teste (ex: 45)")
print("  3. Verifique na IHM física se ângulo mudou")
print("  4. RESTAURE valor original!")
print()
print("Exemplo de teste:")
print(f"  python3 -c \"from modbus_client import *; c = ModbusClient(False, ModbusConfig()); c.write_register(1280, 45)\"")
print()
