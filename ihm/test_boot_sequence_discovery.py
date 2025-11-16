#!/usr/bin/env python3
"""
🔬 ENGENHARIA REVERSA - DESCOBRIR ORIGEM DOS ÂNGULOS

Testa de onde o ladder LÊ os valores iniciais dos ângulos.

ESTRATÉGIA:
1. Ler TODAS as áreas suspeitas ANTES de qualquer operação
2. Comparar com valores em 0x0840-0x0852
3. Encontrar correlação

ÁREAS CANDIDATAS:
- NVRAM (0x0500-0x053F): Ângulos iniciais/finais não-voláteis
- Analog Inputs (0x05F0-0x05FF): Canais analógicos 1-8
- Analog Outputs (0x06E0-0x06EF): Saídas analógicas 1-8
- Timer/Counter Presets (0x0400-0x047F): Valores de preset
- Área desconhecida

Se encontrarmos área gravável que ladder LÊ → SOLUÇÃO DEFINITIVA!
"""

import sys
import time
from modbus_client import ModbusClientWrapper

def scan_all_suspicious_areas(client):
    """Varre todas as áreas que podem conter ângulos"""

    print("="*70)
    print("🔍 VARREDURA COMPLETA - PROCURANDO ORIGEM DOS ÂNGULOS")
    print("="*70)

    # 1. Ler ângulos atuais (referência)
    print("\n📐 ÂNGULOS ATUAIS (0x0840-0x0852):")
    print("-"*70)

    angles_current = {}
    for i, (name, msw, lsw) in enumerate([
        ("Dobra 1", 0x0842, 0x0840),
        ("Dobra 2", 0x0848, 0x0846),
        ("Dobra 3", 0x0852, 0x0850),
    ], 1):
        val = client.read_32bit(msw, lsw)
        angles_current[i] = val
        print(f"{name}: {val} ({val/10.0:.1f}°) - MSW=0x{msw:04X}, LSW=0x{lsw:04X}")

    # 2. Varrer NVRAM (0x0500-0x053F)
    print("\n\n💾 NVRAM - ÂNGULOS NÃO-VOLÁTEIS (0x0500-0x053F):")
    print("-"*70)

    nvram_matches = []
    for addr in range(0x0500, 0x0540, 2):  # Pares MSW/LSW
        msw_addr = addr
        lsw_addr = addr + 1

        if lsw_addr >= 0x0540:
            break

        val = client.read_32bit(msw_addr, lsw_addr)

        if val and val != 0:
            # Verificar se é similar a algum ângulo atual
            for bend_num, angle_val in angles_current.items():
                if abs(val - angle_val) < 50:  # Tolerância
                    print(f"✨ MATCH! 0x{msw_addr:04X}/0x{lsw_addr:04X} = {val} (similar a Dobra {bend_num})")
                    nvram_matches.append((msw_addr, lsw_addr, val, bend_num))
                    break
            else:
                # Apenas mostrar se valor razoável (0-3600 = 0-360°)
                if 0 < val < 3600:
                    print(f"0x{msw_addr:04X}/0x{lsw_addr:04X} = {val} ({val/10.0:.1f}°)")

    # 3. Varrer Analog Inputs Effective (0x05F0-0x05FF)
    print("\n\n📊 ANALOG INPUTS EFFECTIVE (0x05F0-0x05FF):")
    print("-"*70)

    for addr in range(0x05F0, 0x0600):
        val = client.read_register(addr)

        if val and val != 0:
            # Verificar se é similar a algum ângulo
            for bend_num, angle_val in angles_current.items():
                # Dividir por 10 para comparar (pode ser escala diferente)
                if abs(val - angle_val) < 50 or abs(val - angle_val/10) < 5:
                    print(f"✨ MATCH! 0x{addr:04X} = {val} (similar a Dobra {bend_num})")
                    break
            else:
                if 0 < val < 3600:
                    print(f"0x{addr:04X} = {val}")

    # 4. Varrer Analog Outputs Effective (0x06E0-0x06EF)
    print("\n\n📈 ANALOG OUTPUTS EFFECTIVE (0x06E0-0x06EF):")
    print("-"*70)

    for addr in range(0x06E0, 0x06F0):
        val = client.read_register(addr)

        if val and val != 0:
            for bend_num, angle_val in angles_current.items():
                if abs(val - angle_val) < 50 or abs(val - angle_val/10) < 5:
                    print(f"✨ MATCH! 0x{addr:04X} = {val} (similar a Dobra {bend_num})")
                    break
            else:
                if 0 < val < 3600:
                    print(f"0x{addr:04X} = {val}")

    # 5. Varrer Timer/Counter Presets (0x0400-0x047F)
    print("\n\n⏱️ TIMER/COUNTER PRESETS (0x0400-0x047F - apenas não-zero):")
    print("-"*70)

    preset_count = 0
    for addr in range(0x0400, 0x0480):
        val = client.read_register(addr)

        if val and val != 0:
            for bend_num, angle_val in angles_current.items():
                if abs(val - angle_val) < 50:
                    print(f"✨ MATCH! 0x{addr:04X} = {val} (similar a Dobra {bend_num})")
                    preset_count += 1
                    break

    if preset_count == 0:
        print("(Nenhum match encontrado)")

    # 6. Resultado
    print("\n\n" + "="*70)
    print("🎯 RESUMO DA DESCOBERTA")
    print("="*70)

    if nvram_matches:
        print(f"\n✅ ENCONTRADOS {len(nvram_matches)} MATCHES EM NVRAM!")
        print("\nEndereços NVRAM que correspondem a ângulos:")
        for msw, lsw, val, bend in nvram_matches:
            print(f"  Dobra {bend}: 0x{msw:04X}/0x{lsw:04X} = {val} ({val/10.0:.1f}°)")

        print("\n💡 PRÓXIMO PASSO:")
        print("1. Escrever em área NVRAM")
        print("2. Resetar CLP (desligar/ligar)")
        print("3. Verificar se ângulos foram carregados de NVRAM")

    else:
        print("\n❌ NENHUM MATCH ENCONTRADO!")
        print("\nPossíveis causas:")
        print("1. Ângulos vêm de área não testada")
        print("2. Ângulos são hard-coded no ladder")
        print("3. Ângulos vêm de EEPROM interna (não acessível via Modbus)")

        print("\n💡 PRÓXIMO PASSO:")
        print("Analisar ladder linha por linha no WinSUP para encontrar:")
        print("- Instruções MOVK que carregam valores em 0x0840-0x0852")
        print("- Instruções MOV que copiam de registros desconhecidos")


def main():
    print("🔬 ENGENHARIA REVERSA - DESCOBRIR ORIGEM DOS ÂNGULOS\n")

    client = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)

    if not client.connected:
        print("❌ CLP não conectado!")
        return 1

    print("✅ CLP conectado\n")

    scan_all_suspicious_areas(client)

    client.close()

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Varredura interrompida!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
