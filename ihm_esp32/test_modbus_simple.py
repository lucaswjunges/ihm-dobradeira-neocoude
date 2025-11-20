"""
Teste SIMPLES - Testa comunicacao Modbus e imprime resultado
Execute via: ampy --port /dev/ttyACM0 run test_modbus_simple.py
"""
from lib.umodbus.serial import ModbusRTU
import time

print("\n" + "="*50)
print("TESTE MODBUS - Diagnostico Basico")
print("="*50)

# 1. Inicializa UART
print("\n[1/3] Inicializando UART2...")
try:
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
    print("      OK: UART inicializado")
except Exception as e:
    print(f"      ERRO: {e}")
    import sys
    sys.exit(1)

# 2. Testa leitura encoder (registro 0x04D6)
print("\n[2/3] Testando leitura registro 0x04D6 (encoder)...")
print("      Slave ID: 1")
print("      Timeout: 500ms")

try:
    result = modbus.read_holding_registers(slave_addr=1, starting_addr=0x04D6, register_qty=1)

    if result and len(result) > 0 and result[0] is not None:
        print(f"      OK: CLP RESPONDEU!")
        print(f"      Valor lido: {result[0]} (0x{result[0]:04X})")
        print("\n*** COMUNICACAO MODBUS FUNCIONANDO ***")
    else:
        print("      ERRO: Resposta vazia ou None")
        print(f"      Resultado: {result}")
        print("\n*** CLP NAO RESPONDE ***")

except Exception as e:
    print(f"      ERRO: Exception: {e}")
    print("\n*** CLP NAO RESPONDE ***")

# 3. Diagnostico
print("\n[3/3] Diagnostico:")
print("  Se CLP nao responde, verificar:")
print("  - Estado 0x00BE esta ON no ladder?")
print("  - Slave ID = 1 correto?")
print("  - Baudrate CLP = 57600?")
print("  - Fios A/B corretos (nao invertidos)?")
print("  - GND comum ESP32-CLP?")
print("  - MAX485 funcionando?")

print("\n" + "="*50)
