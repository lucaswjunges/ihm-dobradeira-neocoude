#!/usr/bin/env python3
"""
Upload de arquivo para ESP32 via REPL
"""
import serial
import time
import sys

def upload_via_repl(port, local_file, remote_file):
    """Faz upload de arquivo via REPL do MicroPython"""

    print(f"📤 Upload: {local_file} → ESP32:{remote_file}")
    print()

    # Ler arquivo local
    with open(local_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Conectar ao ESP32
    print(f"🔌 Conectando em {port}...")
    ser = serial.Serial(port, 115200, timeout=2)
    time.sleep(0.5)

    # Interromper execução atual (Ctrl+C)
    print("⏸  Interrompendo execução...")
    ser.write(b'\x03\x03')
    time.sleep(0.3)
    ser.read(ser.in_waiting)  # Limpar buffer

    # Entrar no modo paste (Ctrl+E)
    print("📋 Entrando no modo paste...")
    ser.write(b'\x05')
    time.sleep(0.3)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')

    if 'paste mode' not in response.lower():
        print("⚠️  Modo paste não confirmado, continuando...")

    # Preparar código para escrever arquivo
    upload_code = f'''
# Upload via REPL
print("Escrevendo {remote_file}...")

content = """
{content}
"""

with open('{remote_file}', 'w') as f:
    f.write(content)

print("✅ Arquivo gravado: {remote_file}")
print(f"   Tamanho: {{len(content)}} bytes")
'''

    # Enviar código
    print(f"📝 Enviando {len(content)} bytes...")
    ser.write(upload_code.encode('utf-8'))
    time.sleep(0.5)

    # Sair do modo paste (Ctrl+D)
    print("✅ Finalizando upload...")
    ser.write(b'\x04')

    # Aguardar execução
    time.sleep(2)

    # Ler resposta
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print()
    print("📄 Resposta do ESP32:")
    print("-" * 60)
    print(response)
    print("-" * 60)

    ser.close()

    if '✅' in response or 'Arquivo gravado' in response:
        print()
        print("✅ Upload concluído com sucesso!")
        return True
    else:
        print()
        print("⚠️  Upload pode ter falhado. Verifique resposta acima.")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python3 upload_via_repl.py <arquivo_local> <arquivo_remoto>")
        print()
        print("Exemplo:")
        print("  python3 upload_via_repl.py modbus_client.py /modbus_client_esp32.py")
        sys.exit(1)

    local_file = sys.argv[1]
    remote_file = sys.argv[2]

    success = upload_via_repl('/dev/ttyACM0', local_file, remote_file)

    sys.exit(0 if success else 1)
