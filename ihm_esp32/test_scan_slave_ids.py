"""
Testa vários Slave IDs para encontrar o CLP
"""

def test():
    print("\n" + "="*50)
    print("SCAN SLAVE IDs - BUSCAR CLP")
    print("="*50)

    from lib.umodbus.serial import ModbusRTU

    print("\nInicializando UART2...")
    modbus = ModbusRTU(
        uart_id=2,
        baudrate=57600,
        data_bits=8,
        stop_bits=2,
        parity=None,
        tx_pin=17,
        rx_pin=16,
        ctrl_pin=4
    )

    print("\nTestando Slave IDs de 1 a 10...\n")

    for slave_id in range(1, 11):
        print(f"Tentando Slave ID={slave_id}...", end=" ")

        try:
            # Tenta ler 1 registro (encoder MSW)
            result = modbus.read_holding_registers(slave_id, 0x04D6, 1)

            if result and result[0] is not None:
                print(f"✓ ENCONTRADO! Valor: {result[0]}")
                print(f"\n*** CLP RESPONDEU NO SLAVE ID={slave_id} ***\n")
                return slave_id
            else:
                print("timeout")
        except:
            print("erro")

    print("\n✗ Nenhum CLP encontrado nos IDs 1-10")
    print("\nVerifique:")
    print("- Fios A/B podem estar invertidos")
    print("- CLP pode estar com baudrate diferente")
    print("- Estado 0x00BE deve estar ON no ladder")

# Executa
test()
