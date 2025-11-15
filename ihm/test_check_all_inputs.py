#!/usr/bin/env python3
"""
Verificação Completa de Entradas Digitais

Lê todos os inputs E0-E7 para entender o estado da máquina.
"""

from modbus_client import ModbusClientWrapper
import modbus_map as mm

def check_all_inputs():
    """Verifica estado de todas as entradas digitais."""

    print("=" * 60)
    print("VERIFICAÇÃO DE ENTRADAS DIGITAIS")
    print("=" * 60)
    print()

    client = ModbusClientWrapper(stub_mode=False)

    if not client.connected:
        print("❌ Falha ao conectar com CLP")
        return False

    print("✅ Conectado ao CLP")
    print()

    print("Estado das Entradas:")
    print("-" * 60)
    print("Entrada | Endereço | Estado | Observação")
    print("-" * 60)

    # Verificar cada entrada
    for name, addr in sorted(mm.DIGITAL_INPUTS.items()):
        status = client.read_coil(addr)

        if status is not None:
            state_text = "ATIVA ✓" if status else "INATIVA"

            # Observações sobre entradas específicas
            obs = ""
            if name == "E6" and not status:
                obs = "← PROBLEMA: S1 depende de E6!"
            elif name == "E0":
                obs = "(Emergência?)"
            elif name == "E1":
                obs = "(Sensor?)"

            print(f"{name:7} | 0x{addr:04X}   | {state_text:11} | {obs}")
        else:
            print(f"{name:7} | 0x{addr:04X}   | ERRO       |")

    print()

    # Verificar também saídas para contexto
    print("Estado das Saídas:")
    print("-" * 60)
    print("Saída  | Endereço | Estado")
    print("-" * 60)

    for name, addr in sorted(mm.DIGITAL_OUTPUTS.items()):
        status = client.read_coil(addr)

        if status is not None:
            state_text = "ATIVA ✓" if status else "INATIVA"
            print(f"{name:6} | 0x{addr:04X}   | {state_text}")
        else:
            print(f"{name:6} | 0x{addr:04X}   | ERRO")

    print()

    # Verificar estado 00BE (Modbus habilitado)
    print("Estados Críticos:")
    print("-" * 60)

    modbus_enabled = client.read_coil(0x00BE)
    print(f"00BE (Modbus habilitado): {'✓ ON' if modbus_enabled else '✗ OFF'}")

    mode_bit = client.read_coil(0x02FF)
    print(f"02FF (Modo AUTO/MANUAL): {'AUTO ✓' if mode_bit else 'MANUAL'}")

    print()

    # Disconnect
    if hasattr(client.client, 'close'):
        client.client.close()

    print("=" * 60)
    print("ANÁLISE")
    print("=" * 60)
    print()
    print("Se E6 está inativa, o CLP pode estar bloqueando mudança de modo.")
    print("Verifique:")
    print("1. E6 conectado fisicamente?")
    print("2. E6 precisa de condição específica (máquina parada, etc.)?")
    print("3. Ladder pode ter lógica condicional para S1 funcionar")
    print()

    return True


if __name__ == "__main__":
    check_all_inputs()
