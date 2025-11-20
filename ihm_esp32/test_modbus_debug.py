"""
Teste DEBUG Modbus - Verifica comunicação baixo nível
"""

def test():
    print("\n" + "="*50)
    print("DEBUG MODBUS - BAIXO NÍVEL")
    print("="*50)

    from lib.umodbus.serial import ModbusRTU
    import time

    print("\n1. Inicializando UART2...")
    print("   GPIO17 (TX), GPIO16 (RX), GPIO4 (DE/RE)")

    try:
        # Inicializa ModbusRTU diretamente
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
        print("   ✓ UART2 inicializado")
    except Exception as e:
        print(f"   ✗ ERRO: {e}")
        return

    # Teste 1: Ler coils (função 0x01) - mais simples que registros
    print("\n2. Testando leitura de COIL (Function 0x01)...")
    print("   Lendo estado 0x00BE (190) - Modbus Slave Enabled")

    slave_id = 1
    coil_address = 0x00BE  # 190 decimal

    try:
        result = modbus.read_coils(slave_id, coil_address, 1)
        print(f"   ✓ SUCESSO: Estado 0x00BE = {result}")

        if result and result[0]:
            print("   ✓ Modbus slave ESTÁ habilitado no CLP")
        else:
            print("   ✗ AVISO: Modbus slave parece desabilitado")

    except Exception as e:
        print(f"   ✗ ERRO: {e}")
        print("\n   Possíveis causas:")
        print("   - Slave ID errado (tentando ID=1)")
        print("   - Baudrate errado (usando 57600)")
        print("   - Parity errado (usando None)")
        print("   - Stop bits errado (usando 2)")
        print("   - A/B invertidos no RS485")
        print("   - CLP não está respondendo")
        return

    # Teste 2: Ler entrada digital (mais simples)
    print("\n3. Testando leitura de entrada digital E0...")
    try:
        result = modbus.read_input_status(slave_id, 0x0100, 1)  # E0
        print(f"   ✓ SUCESSO: E0 = {result}")
    except Exception as e:
        print(f"   ✗ ERRO: {e}")

    # Teste 3: Ler holding register (função 0x03)
    print("\n4. Testando leitura de REGISTRO (Function 0x03)...")
    print("   Lendo encoder MSW (0x04D6 = 1238)")

    try:
        result = modbus.read_holding_registers(slave_id, 0x04D6, 1)
        print(f"   ✓ SUCESSO: Encoder MSW = {result}")

        if result:
            print(f"   Valor raw: {result[0]} (0x{result[0]:04X})")
    except Exception as e:
        print(f"   ✗ ERRO: {e}")
        return

    # Teste 4: Forçar coil (função 0x05)
    print("\n5. Testando ESCRITA de COIL (Function 0x05)...")
    print("   Tentando trigger 0x0390 (912) ON/OFF")

    try:
        # Liga
        result = modbus.write_single_coil(slave_id, 0x0390, True)
        print(f"   Trigger ON: {result}")
        time.sleep(0.1)

        # Desliga
        result = modbus.write_single_coil(slave_id, 0x0390, False)
        print(f"   Trigger OFF: {result}")
        print("   ✓ Escrita de coils OK")
    except Exception as e:
        print(f"   ✗ ERRO: {e}")

    # Teste 5: Escrever registro (função 0x06)
    print("\n6. Testando ESCRITA de REGISTRO (Function 0x06)...")
    print("   Tentando escrever em 0x0A00 (2560)")

    try:
        result = modbus.write_single_register(slave_id, 0x0A00, 123)
        print(f"   Escrita MSW: {result}")

        # Lê de volta
        read_back = modbus.read_holding_registers(slave_id, 0x0A00, 1)
        print(f"   Leitura: {read_back}")

        if read_back and read_back[0] == 123:
            print("   ✓ Escrita/leitura de registros OK")
        else:
            print(f"   ✗ Valor não bateu: esperado 123, lido {read_back}")
    except Exception as e:
        print(f"   ✗ ERRO: {e}")

    print("\n" + "="*50)
    print("DEBUG CONCLUÍDO")
    print("="*50)
    print("\nSe todos os testes passaram: Modbus OK")
    print("Se algum falhou: Verificar hardware/configuração")

# Executa
test()
