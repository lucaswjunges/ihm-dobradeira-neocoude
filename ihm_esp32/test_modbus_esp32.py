"""
Teste Modbus ESP32 - Diagnóstico de Comunicação
Testar conexão com CLP Atos MPC4004
"""
import time
from machine import Pin, UART
from lib.umodbus.serial import ModbusRTU
import modbus_map as mm

print("\n" + "="*50)
print("TESTE MODBUS ESP32 - DIAGNÓSTICO CLP")
print("="*50)

# Configuração
SLAVE_ID = 1
BAUDRATE = 57600
TX_PIN = 17
RX_PIN = 16
DE_PIN = 4

print(f"\nConfiguração:")
print(f"  UART: 2")
print(f"  Baudrate: {BAUDRATE}")
print(f"  TX: GPIO{TX_PIN}")
print(f"  RX: GPIO{RX_PIN}")
print(f"  DE/RE: GPIO{DE_PIN}")
print(f"  Slave ID: {SLAVE_ID}")

# Inicializa Modbus
print(f"\n[1/4] Inicializando Modbus...")
try:
    modbus = ModbusRTU(
        uart_id=2,
        baudrate=BAUDRATE,
        tx_pin=TX_PIN,
        rx_pin=RX_PIN,
        ctrl_pin=DE_PIN
    )
    print("✓ Modbus inicializado")
except Exception as e:
    print(f"✗ Erro ao inicializar: {e}")
    import sys
    sys.exit(1)

# Teste 1: Ler encoder (registros 04D6/04D7 = 1238/1239 decimal)
print(f"\n[2/4] Teste 1: Lendo encoder (32-bit)...")
print(f"  Endereços: {mm.ENCODER['ANGLE_MSW']} (MSW) + {mm.ENCODER['ANGLE_LSW']} (LSW)")

try:
    # Tenta ler 2 registros de uma vez
    result = modbus.read_holding_registers(SLAVE_ID, mm.ENCODER['ANGLE_MSW'], 2)

    if result:
        msw = result[0]
        lsw = result[1]
        encoder_raw = (msw << 16) | lsw
        encoder_angle = encoder_raw / 10.0

        print(f"✓ Leitura OK:")
        print(f"  MSW (reg {mm.ENCODER['ANGLE_MSW']}): 0x{msw:04X} ({msw})")
        print(f"  LSW (reg {mm.ENCODER['ANGLE_LSW']}): 0x{lsw:04X} ({lsw})")
        print(f"  Valor 32-bit: {encoder_raw}")
        print(f"  Ângulo: {encoder_angle}°")
    else:
        print(f"✗ Sem resposta do CLP")

except Exception as e:
    print(f"✗ Erro na leitura: {e}")
    import sys
    sys.print_exception(e)

time.sleep(1)

# Teste 2: Ler ângulo dobra 1 (registro 500h = 1280 decimal)
print(f"\n[3/4] Teste 2: Lendo ângulo dobra 1...")
print(f"  Endereço: {mm.BEND_ANGLES['BEND_1_SETPOINT']}")

try:
    result = modbus.read_holding_registers(SLAVE_ID, mm.BEND_ANGLES['BEND_1_SETPOINT'], 1)

    if result:
        value = result[0]
        angle = value / 10.0
        print(f"✓ Leitura OK:")
        print(f"  Valor bruto: {value}")
        print(f"  Ângulo: {angle}°")
    else:
        print(f"✗ Sem resposta do CLP")

except Exception as e:
    print(f"✗ Erro na leitura: {e}")
    import sys
    sys.print_exception(e)

time.sleep(1)

# Teste 3: Ler entrada digital E0 (registro 0100h = 256 decimal)
print(f"\n[4/4] Teste 3: Lendo entrada digital E0...")
print(f"  Endereço: 256")

try:
    result = modbus.read_holding_registers(SLAVE_ID, 256, 1)

    if result:
        value = result[0]
        status = "ON" if (value & 0x01) else "OFF"
        print(f"✓ Leitura OK:")
        print(f"  Valor bruto: 0x{value:04X} ({value})")
        print(f"  E0 status: {status}")
    else:
        print(f"✗ Sem resposta do CLP")

except Exception as e:
    print(f"✗ Erro na leitura: {e}")
    import sys
    sys.print_exception(e)

# Resultado final
print("\n" + "="*50)
print("DIAGNÓSTICO COMPLETO")
print("="*50)
print("\nSe todos os testes falharam:")
print("  1. Verificar fiação RS485 (A/B não invertidos)")
print("  2. Verificar alimentação do MAX485")
print("  3. Verificar se CLP está ligado")
print("  4. Verificar se state 00BE (190) está ON no CLP")
print("  5. Tentar outros Slave IDs (1-10)")
print("\nSe alguns testes passaram:")
print("  ✓ Comunicação Modbus OK!")
print("  → Verificar endereços dos registros no ladder")
print("")
