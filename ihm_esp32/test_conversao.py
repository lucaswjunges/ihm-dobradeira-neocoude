#!/usr/bin/env python3
"""
Script de teste para validar conversões de ângulos
Data: 06/Jan/2026
"""

import modbus_map as mm

print("=" * 60)
print("TESTE DE CONVERSÕES - COMPENSAÇÃO DE INÉRCIA")
print("=" * 60)

# Teste 1: Encoder 376 pulsos -> IHM
print("\n1. ENCODER 376 PULSOS -> IHM")
print("-" * 60)
pulsos = 376
pulsos_norm = pulsos % 400
graus_disco = (pulsos_norm / 400.0) * 360.0
graus_ihm = graus_disco / 2.0

print(f"   Encoder RAW: {pulsos} pulsos (0x{pulsos:04X})")
print(f"   Encoder normalizado: {pulsos_norm} pulsos")
print(f"   Disco: {graus_disco:.1f}°")
print(f"   IHM: {graus_ihm:.1f}°")
print(f"   ✅ ESPERADO: ~169.2° IHM")

# Teste 2: IHM 90° -> CLP (com compensação)
print("\n2. IHM 90° -> CLP (GRAVAÇÃO)")
print("-" * 60)
ihm_90 = 90.0
clp_90 = mm.real_angle_to_clp(ihm_90)

disco_90 = ihm_90 * 2
escala_ideal = int((disco_90 / 360.0) * 2048)

print(f"   IHM: {ihm_90}°")
print(f"   Disco (×2): {disco_90}°")
print(f"   Escala ideal: {escala_ideal} (0x{escala_ideal:04X})")
print(f"   Escala compensada: {clp_90} (0x{clp_90:04X})")
print(f"   Compensação aplicada: -{escala_ideal - clp_90}")
print(f"   ✅ ESPERADO: 886 (0x0376)")

# Teste 3: CLP 886 -> IHM (leitura)
print("\n3. CLP 886 -> IHM (LEITURA)")
print("-" * 60)
clp_886 = 886
ihm_lido = mm.clp_to_real_angle(clp_886)

print(f"   CLP: {clp_886} (0x{clp_886:04X})")
print(f"   IHM lido: {ihm_lido:.1f}°")
print(f"   ✅ ESPERADO: 90.0° IHM")

# Teste 4: IHM 45° -> CLP
print("\n4. IHM 45° -> CLP (GRAVAÇÃO)")
print("-" * 60)
ihm_45 = 45.0
clp_45 = mm.real_angle_to_clp(ihm_45)

disco_45 = ihm_45 * 2
escala_ideal_45 = int((disco_45 / 360.0) * 2048)

print(f"   IHM: {ihm_45}°")
print(f"   Disco (×2): {disco_45}°")
print(f"   Escala ideal: {escala_ideal_45} (0x{escala_ideal_45:04X})")
print(f"   Escala compensada: {clp_45} (0x{clp_45:04X})")
print(f"   Compensação aplicada: -{escala_ideal_45 - clp_45}")
print(f"   ✅ ESPERADO: 374 (0x0176)")

# Teste 5: CLP 374 -> IHM
print("\n5. CLP 374 -> IHM (LEITURA)")
print("-" * 60)
clp_374 = 374
ihm_lido_45 = mm.clp_to_real_angle(clp_374)

print(f"   CLP: {clp_374} (0x{clp_374:04X})")
print(f"   IHM lido: {ihm_lido_45:.1f}°")
print(f"   ✅ ESPERADO: 45.0° IHM")

# Teste 6: Validação bidirecional
print("\n6. VALIDAÇÃO BIDIRECIONAL")
print("-" * 60)
test_angles = [10, 22.5, 45, 67.5, 90, 112.5, 135, 157.5, 180]

print(f"{'IHM':>8} | {'CLP':>6} | {'Lido':>8} | {'Erro':>8}")
print("-" * 40)
for angle in test_angles:
    clp_val = mm.real_angle_to_clp(angle)
    ihm_read = mm.clp_to_real_angle(clp_val)
    erro = abs(ihm_read - angle)
    status = "✅" if erro < 0.1 else "❌"
    print(f"{angle:>8.1f}° | {clp_val:>6} | {ihm_read:>8.1f}° | {erro:>7.3f}° {status}")

print("\n" + "=" * 60)
print("✅ TESTE COMPLETO!")
print("=" * 60)
