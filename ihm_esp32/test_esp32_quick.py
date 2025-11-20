"""
Teste Rápido ESP32 - Ângulos
Executa no próprio ESP32 via REPL
"""

def test_angles():
    import modbus_client_esp32 as mc
    import time

    print("\n" + "="*50)
    print("TESTE RÁPIDO - ÂNGULOS ESP32")
    print("="*50)

    # Conecta CLP (stub_mode=False para CLP real)
    print("\nConectando CLP...")
    client = mc.ModbusClientWrapper(stub_mode=False, slave_id=1)

    if not client.connected:
        print("ERRO: CLP não conectado!")
        return

    print("OK: CLP conectado\n")

    # Teste 1: Escreve ângulo
    print("="*50)
    print("TESTE 1: ESCRITA")
    print("="*50)
    angle = 90.5
    print(f"Gravando Dobra 1: {angle}°")

    ok = client.write_bend_angle(1, angle)
    if ok:
        print(f"  OK: Gravado {angle}°")
    else:
        print("  ERRO: Falha ao gravar")
        return

    # Aguarda propagação
    time.sleep(1)

    # Teste 2: Lê ângulo
    print("\n" + "="*50)
    print("TESTE 2: LEITURA")
    print("="*50)
    print("Lendo Dobra 1 (área SCADA 0x0B00)...")

    read_angle = client.read_bend_angle(1)
    if read_angle is not None:
        print(f"  OK: Lido {read_angle:.1f}°")

        # Valida
        diff = abs(read_angle - angle)
        print(f"\nValidação:")
        print(f"  Esperado: {angle:.1f}°")
        print(f"  Lido:     {read_angle:.1f}°")
        print(f"  Diferença: {diff:.1f}°")

        if diff <= 0.2:
            print("\n  SUCESSO!")
        else:
            print("\n  FALHA: Diferença muito grande")
    else:
        print("  ERRO: Falha ao ler")

    print("\n" + "="*50)
    print("TESTE CONCLUÍDO")
    print("="*50)

# Executa teste
if __name__ == '__main__':
    test_angles()
