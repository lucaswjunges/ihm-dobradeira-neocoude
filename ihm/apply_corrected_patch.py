#!/usr/bin/env python3
"""
Script para aplicar patch corrigido no ESP32
Remove patch antigo (0x0840) e aplica novo (0x0A00 + triggers)
"""

import serial
import time
import sys

def send_command(ser, cmd, wait=0.5):
    """Envia comando e aguarda resposta"""
    ser.write(cmd.encode() + b'\r\n')
    time.sleep(wait)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    return response

def enter_paste_mode(ser):
    """Entra em paste mode (Ctrl+E)"""
    ser.write(b'\x05')  # Ctrl+E
    time.sleep(0.5)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    if 'paste mode' in response.lower():
        print("✅ Paste mode ativado")
        return True
    return False

def exit_paste_mode(ser):
    """Sai de paste mode (Ctrl+D)"""
    ser.write(b'\x04')  # Ctrl+D
    time.sleep(1)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(response)
    return response

def apply_corrected_patch(port='/dev/ttyACM0'):
    """Aplica patch corrigido"""

    print(f"Conectando em {port}...")
    ser = serial.Serial(port, 115200, timeout=2)
    time.sleep(1)

    # Parar execução atual
    print("Parando execução...")
    ser.write(b'\x03\x03')  # Ctrl+C
    time.sleep(0.5)
    ser.read(ser.in_waiting)  # Limpar buffer

    # Verificar se tem patch antigo
    print("\n1. Verificando patch atual...")
    resp = send_command(ser, "with open('/boot.py', 'r') as f: c = f.read()")
    resp = send_command(ser, "print('OLD_PATCH' if '0x0840' in c else 'NO_OLD_PATCH')")
    print(resp)

    # Aplicar novo patch via paste mode
    print("\n2. Aplicando patch corrigido...")

    if not enter_paste_mode(ser):
        print("❌ Erro ao entrar em paste mode")
        return False

    # Código do patch
    patch_code = '''
import time

def write_bend_angle_CORRECTED(self, bend_number, degrees):
    if bend_number not in [1, 2, 3]:
        return False
    mapping = {
        1: {'msw': 0x0A00, 'lsw': 0x0A02, 'trigger': 0x0390},
        2: {'msw': 0x0A04, 'lsw': 0x0A06, 'trigger': 0x0391},
        3: {'msw': 0x0A08, 'lsw': 0x0A0A, 'trigger': 0x0392},
    }
    addr = mapping[bend_number]
    value_32bit = int(degrees * 10)
    msw = (value_32bit >> 16) & 0xFFFF
    lsw = value_32bit & 0xFFFF
    ok_msw = self.write_register(addr['msw'], msw)
    ok_lsw = self.write_register(addr['lsw'], lsw)
    if not (ok_msw and ok_lsw):
        return False
    ok_t1 = self.write_coil(addr['trigger'], True)
    time.sleep(0.05)
    ok_t2 = self.write_coil(addr['trigger'], False)
    return ok_t1 and ok_t2

def read_bend_angle_CORRECTED(self, bend_number):
    if bend_number not in [1, 2, 3]:
        return None
    mapping = {
        1: {'msw': 0x0842, 'lsw': 0x0840},
        2: {'msw': 0x0848, 'lsw': 0x0846},
        3: {'msw': 0x0852, 'lsw': 0x0850},
    }
    addr = mapping[bend_number]
    msw = self.read_register(addr['msw'])
    lsw = self.read_register(addr['lsw'])
    if msw is None or lsw is None:
        return None
    value_32bit = (msw << 16) | lsw
    return value_32bit / 10.0

try:
    import modbus_client_esp32
    modbus_client_esp32.ModbusClientWrapper.write_bend_angle = write_bend_angle_CORRECTED
    modbus_client_esp32.ModbusClientWrapper.read_bend_angle = read_bend_angle_CORRECTED
    print("OK: Patch 0x0A00 aplicado - grava em Modbus Input + trigger")
except Exception as e:
    print("ERRO:", e)
'''

    ser.write(patch_code.encode())
    time.sleep(0.5)

    # Executar (Ctrl+D)
    print("\n3. Executando patch...")
    response = exit_paste_mode(ser)

    if 'OK: Patch 0x0A00' in response:
        print("✅ Patch aplicado com sucesso!")
    else:
        print("⚠️  Resposta:", response)

    # Testar
    print("\n4. Testando patch...")
    resp = send_command(ser, "import modbus_client_esp32 as mc", 0.3)
    resp = send_command(ser, "w = mc.ModbusClientWrapper()", 0.5)
    resp = send_command(ser, "print('Testing write...')", 0.3)
    resp = send_command(ser, "ok = w.write_bend_angle(1, 45.0)", 1.0)
    resp = send_command(ser, "print('Write result:', ok)", 0.5)
    print(resp)

    time.sleep(0.2)
    resp = send_command(ser, "print('Testing read...')", 0.3)
    resp = send_command(ser, "angle = w.read_bend_angle(1)", 1.0)
    resp = send_command(ser, "print('Angle read:', angle)", 0.5)
    print(resp)

    ser.close()
    print("\n✅ Concluído!")
    return True

if __name__ == '__main__':
    try:
        apply_corrected_patch()
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
