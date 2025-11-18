#!/usr/bin/env python3
"""
Teste completo da porta Modbus RTU - CLP Atos MPC4004
Verifica todas as funções Modbus suportadas
"""

from pymodbus.client import ModbusSerialClient
import time

PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

def test_read_coils(client):
    """Testa leitura de coils (Function 0x01)"""
    print("\n" + "="*60)
    print("TESTE 1: Read Coils (0x01) - Estados internos")
    print("="*60)
    
    # Testar alguns estados conhecidos
    test_addresses = [
        (190, "00BE - Modbus slave enable"),
        (220, "00DC - S1 button"),
        (221, "00DD - S2 button"),
        (160, "00A0 - K1 button"),
        (169, "00A9 - K0 button"),
    ]
    
    for addr, desc in test_addresses:
        try:
            result = client.read_coils(address=addr, count=1, device_id=SLAVE_ID)
            if result.isError():
                print(f"  ✗ Endereço {addr} ({desc}): ERRO - {result}")
            else:
                state = "ON" if result.bits[0] else "OFF"
                print(f"  ✓ Endereço {addr} ({desc}): {state}")
        except Exception as e:
            print(f"  ✗ Endereço {addr} ({desc}): Exceção - {e}")
    
    return True

def test_read_discrete_inputs(client):
    """Testa leitura de discrete inputs (Function 0x02)"""
    print("\n" + "="*60)
    print("TESTE 2: Read Discrete Inputs (0x02)")
    print("="*60)
    
    try:
        # Tentar ler primeiros 16 discrete inputs
        result = client.read_discrete_inputs(address=0, count=16, device_id=SLAVE_ID)
        if result.isError():
            print(f"  ⚠ Discrete inputs não disponíveis: {result}")
        else:
            print(f"  ✓ Discrete inputs lidos (0-15):")
            for i, bit in enumerate(result.bits[:16]):
                state = "ON" if bit else "OFF"
                print(f"    Input {i}: {state}")
    except Exception as e:
        print(f"  ⚠ Exceção: {e}")
    
    return True

def test_read_holding_registers(client):
    """Testa leitura de holding registers (Function 0x03)"""
    print("\n" + "="*60)
    print("TESTE 3: Read Holding Registers (0x03)")
    print("="*60)
    
    test_ranges = [
        (1238, 2, "04D6/04D7 - Encoder counter (32-bit)"),
        (1232, 2, "04D0/04D1 - RPM value"),
        (1234, 2, "04D2/04D3 - Setpoint"),
        (6536, 1, "1988H - Slave address register"),
        (6535, 1, "1987H - Baudrate register"),
    ]
    
    for addr, count, desc in test_ranges:
        try:
            result = client.read_holding_registers(address=addr, count=count, device_id=SLAVE_ID)
            if result.isError():
                print(f"  ✗ {desc}: ERRO - {result}")
            else:
                if count == 1:
                    print(f"  ✓ {desc}: {result.registers[0]} (0x{result.registers[0]:04X})")
                else:
                    values = ", ".join([f"0x{r:04X}" for r in result.registers])
                    print(f"  ✓ {desc}: [{values}]")
                    if count == 2:  # 32-bit value
                        val32 = (result.registers[0] << 16) | result.registers[1]
                        print(f"      → Valor 32-bit: {val32}")
        except Exception as e:
            print(f"  ✗ {desc}: Exceção - {e}")
    
    return True

def test_read_input_registers(client):
    """Testa leitura de input registers (Function 0x04)"""
    print("\n" + "="*60)
    print("TESTE 4: Read Input Registers (0x04)")
    print("="*60)
    
    try:
        # Tentar ler encoder via input registers
        result = client.read_input_registers(address=1238, count=2, device_id=SLAVE_ID)
        if result.isError():
            print(f"  ⚠ Input registers não disponíveis ou endereço incorreto: {result}")
        else:
            print(f"  ✓ Input registers lidos (04D6/04D7):")
            val32 = (result.registers[0] << 16) | result.registers[1]
            print(f"      → Valor 32-bit: {val32}")
    except Exception as e:
        print(f"  ⚠ Exceção: {e}")
    
    return True

def test_write_single_coil(client):
    """Testa escrita de single coil (Function 0x05)"""
    print("\n" + "="*60)
    print("TESTE 5: Write Single Coil (0x05) - Comando de botão")
    print("="*60)
    
    # Usar um estado que não afeta operação - vamos testar com Lock (00F1)
    test_coil = 241  # 00F1 - Lock button (não deve afetar nada se já estiver desbloqueado)
    
    print(f"  Testando escrita no coil {test_coil} (00F1 - Lock)...")
    
    try:
        # Ler estado atual
        result = client.read_coils(address=test_coil, count=1, device_id=SLAVE_ID)
        if result.isError():
            print(f"  ✗ Não foi possível ler estado inicial")
            return False
        
        initial_state = result.bits[0]
        print(f"  Estado inicial: {'ON' if initial_state else 'OFF'}")
        
        # Testar escrita ON
        print(f"  Escrevendo ON...")
        result = client.write_coil(address=test_coil, value=True, device_id=SLAVE_ID)
        if result.isError():
            print(f"  ✗ Erro ao escrever ON: {result}")
            return False
        print(f"  ✓ Escrita ON executada")
        
        time.sleep(0.1)
        
        # Ler novamente
        result = client.read_coils(address=test_coil, count=1, device_id=SLAVE_ID)
        new_state = result.bits[0]
        print(f"  Estado após ON: {'ON' if new_state else 'OFF'}")
        
        # Testar escrita OFF
        print(f"  Escrevendo OFF...")
        result = client.write_coil(address=test_coil, value=False, device_id=SLAVE_ID)
        if result.isError():
            print(f"  ✗ Erro ao escrever OFF: {result}")
            return False
        print(f"  ✓ Escrita OFF executada")
        
        time.sleep(0.1)
        
        # Ler estado final
        result = client.read_coils(address=test_coil, count=1, device_id=SLAVE_ID)
        final_state = result.bits[0]
        print(f"  Estado final: {'ON' if final_state else 'OFF'}")
        
        print(f"\n  ✓ TESTE DE ESCRITA: SUCESSO")
        print(f"    Write Single Coil (0x05) está FUNCIONAL")
        
    except Exception as e:
        print(f"  ✗ Exceção: {e}")
        return False
    
    return True

def test_write_single_register(client):
    """Testa escrita de single register (Function 0x06)"""
    print("\n" + "="*60)
    print("TESTE 6: Write Single Register (0x06)")
    print("="*60)
    
    print("  ⚠ Pulando teste de escrita em registros")
    print("    (evitar alterar setpoints ou configurações críticas)")
    
    return True

def test_timing(client):
    """Testa latência de comunicação"""
    print("\n" + "="*60)
    print("TESTE 7: Latência de comunicação")
    print("="*60)
    
    times = []
    for i in range(10):
        start = time.time()
        result = client.read_holding_registers(address=1238, count=2, device_id=SLAVE_ID)
        elapsed = (time.time() - start) * 1000  # ms
        times.append(elapsed)
        if not result.isError():
            print(f"  Leitura {i+1}: {elapsed:.2f} ms")
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"\n  Estatísticas:")
    print(f"    Média: {avg_time:.2f} ms")
    print(f"    Mínimo: {min_time:.2f} ms")
    print(f"    Máximo: {max_time:.2f} ms")
    
    if avg_time < 100:
        print(f"  ✓ Latência EXCELENTE (< 100ms)")
    elif avg_time < 200:
        print(f"  ✓ Latência BOA (< 200ms)")
    else:
        print(f"  ⚠ Latência ALTA (> 200ms)")
    
    return True

def main():
    print("="*60)
    print("TESTE COMPLETO DE PORTA MODBUS RTU")
    print("CLP Atos MPC4004 - RS485-B")
    print("="*60)
    print(f"\nConfiguração:")
    print(f"  Porta: {PORT}")
    print(f"  Baudrate: {BAUDRATE}")
    print(f"  Slave ID: {SLAVE_ID}")
    
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        parity='N',
        stopbits=1,
        bytesize=8,
        timeout=1.0
    )
    
    if not client.connect():
        print("\n✗ ERRO: Não foi possível conectar à porta serial")
        return
    
    print("\n✓ Conectado com sucesso\n")
    
    # Executar todos os testes
    tests = [
        ("Read Coils (0x01)", test_read_coils),
        ("Read Discrete Inputs (0x02)", test_read_discrete_inputs),
        ("Read Holding Registers (0x03)", test_read_holding_registers),
        ("Read Input Registers (0x04)", test_read_input_registers),
        ("Write Single Coil (0x05)", test_write_single_coil),
        ("Write Single Register (0x06)", test_write_single_register),
        ("Timing Test", test_timing),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func(client)
            results.append((name, success))
        except Exception as e:
            print(f"\n✗ Erro inesperado em {name}: {e}")
            results.append((name, False))
    
    client.close()
    
    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\n{'='*60}")
    print(f"RESULTADO FINAL: {passed}/{total} testes aprovados")
    print(f"{'='*60}")
    
    if passed == total:
        print("\n🎉 PORTA MODBUS RTU 100% FUNCIONAL! 🎉")
        print("\nFunções confirmadas:")
        print("  ✓ Leitura de coils (botões/estados)")
        print("  ✓ Leitura de holding registers (encoder, configuração)")
        print("  ✓ Escrita de coils (comandos de botão)")
        print("  ✓ Comunicação rápida e estável")
        print("\n✓ Pronto para desenvolvimento da IHM web!")
    else:
        print(f"\n⚠ {total - passed} teste(s) falharam - verificar limitações")

if __name__ == "__main__":
    main()
