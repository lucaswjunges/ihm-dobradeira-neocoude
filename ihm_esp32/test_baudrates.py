"""
Testa diferentes baudrates e configurações
"""

def test():
    print("\n" + "="*50)
    print("TESTE MÚLTIPLOS BAUDRATES")
    print("="*50)

    from lib.umodbus.serial import ModbusRTU
    import time

    # Baudrates comuns CLP Atos
    baudrates = [9600, 19200, 38400, 57600, 115200]

    # Configurações parity (None, Even, Odd)
    configs = [
        (None, 1, "8N1"),
        (None, 2, "8N2"),
        (0, 1, "8E1"),
        (1, 1, "8O1"),
    ]

    print("\nTestando combinações baudrate + parity...\n")

    for baud in baudrates:
        for parity, stop_bits, name in configs:
            print(f"Tentando {baud} {name}...", end=" ")

            try:
                # Inicializa com configuração
                modbus = ModbusRTU(
                    uart_id=2,
                    baudrate=baud,
                    data_bits=8,
                    stop_bits=stop_bits,
                    parity=parity,
                    tx_pin=17,
                    rx_pin=16,
                    ctrl_pin=4
                )

                time.sleep(0.1)

                # Tenta ler encoder
                result = modbus.read_holding_registers(1, 0x04D6, 1)

                if result and result[0] is not None:
                    print(f"✓ ENCONTRADO! Valor: {result[0]}")
                    print(f"\n*** CLP RESPONDEU: {baud} {name} ***\n")
                    return
                else:
                    print("timeout")

            except Exception as e:
                print(f"erro: {e}")

            time.sleep(0.1)

    print("\n✗ Nenhuma configuração funcionou")
    print("\nProblema pode ser:")
    print("- Estado 0x00BE não está ON no CLP")
    print("- GPIO4 (DE/RE) não está em HIGH")
    print("- MAX485 com defeito")
    print("- GND não está comum entre ESP32 e CLP")

test()
