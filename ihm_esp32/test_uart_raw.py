"""
Teste RAW UART - Ver se há ALGUM dado chegando
"""

def test():
    from machine import UART, Pin
    import time

    print("\n" + "="*50)
    print("TESTE RAW UART2 - BAIXO NÍVEL")
    print("="*50)

    # Configura GPIO4 (DE/RE) em HIGH
    de_re = Pin(4, Pin.OUT)
    de_re.value(1)
    print("\nGPIO4 (DE/RE) setado para HIGH")

    # Inicializa UART2
    uart = UART(2, baudrate=57600, bits=8, parity=None, stop=2, tx=17, rx=16)
    print("UART2 inicializado: 57600 8N2")

    # Limpa buffer
    uart.read()

    # Envia frame Modbus manualmente
    print("\n1. Enviando frame Modbus READ (0x03)...")
    # Slave=1, Func=0x03, Addr=0x04D6, Qty=1, CRC
    frame = bytes([0x01, 0x03, 0x04, 0xD6, 0x00, 0x01, 0x25, 0xC8])

    de_re.value(1)  # TX mode
    uart.write(frame)
    time.sleep_ms(10)  # Aguarda transmissão

    de_re.value(0)  # RX mode (TESTE!)
    print("   Frame enviado, aguardando resposta...")

    # Aguarda resposta (max 1s)
    timeout = 100  # 1000ms = 1s
    received = bytearray()

    while timeout > 0:
        if uart.any():
            byte = uart.read(1)
            if byte:
                received.extend(byte)
                print(f"   Byte recebido: 0x{byte[0]:02X}")
        time.sleep_ms(10)
        timeout -= 1

    if len(received) > 0:
        print(f"\n   ✓ RECEBEU {len(received)} bytes!")
        print(f"   Dados: {' '.join([f'{b:02X}' for b in received])}")
        print("\n   *** CLP ESTÁ RESPONDENDO! ***")
        print("   Problema pode ser no código MicroPython Modbus")
    else:
        print("\n   ✗ NENHUM byte recebido")
        print("\n   Problemas possíveis:")
        print("   1. GND não está comum (ESP32 ↔ CLP)")
        print("   2. Fios RX/TX invertidos")
        print("   3. Baudrate errado no CLP")
        print("   4. MAX485 com defeito")
        print("   5. CLP não está em modo Modbus (0x00BE=OFF)")

    # Teste 2: Modo RX contínuo
    print("\n2. Modo RX contínuo (5 segundos)...")
    print("   Se CLP estiver transmitindo algo, vai aparecer aqui...")

    de_re.value(0)  # RX mode
    uart.read()  # Limpa

    timeout = 500  # 5s
    count = 0

    while timeout > 0:
        if uart.any():
            data = uart.read()
            if data:
                count += len(data)
                print(f"   Dados: {' '.join([f'{b:02X}' for b in data])}")
        time.sleep_ms(10)
        timeout -= 1

    if count > 0:
        print(f"\n   Recebeu {count} bytes espontâneos")
    else:
        print("\n   Nenhum dado espontâneo (normal se CLP é slave)")

    print("\n" + "="*50)

test()
