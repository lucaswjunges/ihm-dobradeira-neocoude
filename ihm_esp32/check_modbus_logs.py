"""
Le logs do console ESP32 via UART para diagnosticar conexao Modbus
"""
import serial
import time

print("\n" + "="*60)
print("LENDO LOGS ESP32 - Diagnostico Modbus")
print("="*60)
print("\nPressione Ctrl+C para sair\n")

try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
    time.sleep(0.5)

    # Envia comando para testar Modbus manualmente
    print("[INFO] Enviando comando de teste Modbus via REPL...")
    ser.write(b'\r\n')
    time.sleep(0.2)

    # Le logs continuamente
    while True:
        if ser.in_waiting:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                # Destaca linhas importantes
                if 'ERRO' in line or 'timeout' in line or 'CLP' in line:
                    print(f">>> {line}")
                else:
                    print(line)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n[INFO] Finalizando...")
except Exception as e:
    print(f"\n[ERRO] {e}")
finally:
    if 'ser' in locals():
        ser.close()
