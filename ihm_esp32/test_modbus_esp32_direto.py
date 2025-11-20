"""
Teste DIRETO de Modbus no ESP32
Execute via: ampy --port /dev/ttyACM0 run test_modbus_esp32_direto.py
"""

def test():
    print("\n" + "="*50)
    print("TESTE MODBUS ESP32 <-> CLP")
    print("="*50)

    # Import
    import modbus_client_esp32 as mc
    import modbus_map as mm
    import time

    # Conecta
    print("\n1. Conectando CLP...")
    client = mc.ModbusClientWrapper(stub_mode=False, slave_id=1)
    print(f"   Conectado: {client.connected}")

    if not client.connected:
        print("\n   ERRO: Modbus não conectou!")
        print("   Verifique:")
        print("   - GPIO17/16/4 conectados ao MAX485")
        print("   - CLP ligado")
        print("   - Estado 0x00BE = ON no ladder")
        return

    # Teste 1: Ler encoder (teste simples)
    print("\n2. Testando leitura encoder...")
    encoder_msw = client.read_register(mm.ENCODER['ANGLE_MSW'])
    encoder_lsw = client.read_register(mm.ENCODER['ANGLE_LSW'])

    if encoder_msw is None or encoder_lsw is None:
        print(f"   ERRO: Timeout ao ler encoder")
        print(f"   MSW: {encoder_msw}, LSW: {encoder_lsw}")
        return
    else:
        value = (encoder_msw << 16) | encoder_lsw
        degrees = value / 10.0
        print(f"   OK: Encoder = {degrees}°")

    # Teste 2: Escrever ângulo
    print("\n3. Testando escrita ângulo...")
    test_angle = 95.5
    print(f"   Gravando {test_angle}° na Dobra 1...")

    success = client.write_bend_angle(1, test_angle)

    if not success:
        print("   ERRO: Falha ao gravar")
        return
    else:
        print(f"   OK: Gravado {test_angle}°")

    # Aguarda propagação
    print("\n4. Aguardando propagação (2s)...")
    time.sleep(2)

    # Teste 3: Ler de volta
    print("\n5. Lendo ângulo de volta...")
    read_angle = client.read_bend_angle(1)

    if read_angle is None:
        print("   ERRO: Falha ao ler")
        return
    else:
        print(f"   OK: Lido {read_angle:.1f}°")

        # Validação
        diff = abs(read_angle - test_angle)
        print(f"\n6. Validação:")
        print(f"   Esperado: {test_angle}°")
        print(f"   Lido: {read_angle:.1f}°")
        print(f"   Diferença: {diff:.1f}°")

        if diff <= 0.5:
            print("\n   ✓ SUCESSO!")
        else:
            print("\n   ✗ FALHA: Diferença muito grande")

    print("\n" + "="*50)
    print("TESTE CONCLUÍDO")
    print("="*50)

# Executa
test()
