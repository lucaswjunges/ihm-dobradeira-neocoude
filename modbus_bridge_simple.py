#!/usr/bin/env python3
"""
Bridge Modbus TCP → RTU (versão simples)
Aceita conexões Modbus TCP e encaminha para Modbus RTU serial
"""

import socket
import threading
import time
from pymodbus.client import ModbusSerialClient

# Configuração
TCP_HOST = '0.0.0.0'
TCP_PORT = 5020
SERIAL_PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
PARITY = 'N'
STOPBITS = 2
SLAVE_ID = 1

print("=" * 60)
print("MODBUS TCP → RTU BRIDGE (Simples)")
print("=" * 60)
print(f"TCP Server: {TCP_HOST}:{TCP_PORT}")
print(f"Serial: {SERIAL_PORT} @ {BAUDRATE} 8{PARITY}{STOPBITS}")
print(f"Slave ID: {SLAVE_ID}")
print()

# Conectar ao CLP serial
print("Conectando ao CLP...")
serial_client = ModbusSerialClient(
    port=SERIAL_PORT,
    baudrate=BAUDRATE,
    parity=PARITY,
    stopbits=STOPBITS,
    bytesize=8,
    timeout=2.0
)

if not serial_client.connect():
    print("❌ ERRO: Não conectou ao CLP!")
    print("Verifique:")
    print("  - sudo chmod 666 /dev/ttyUSB0")
    print("  - ls -la /dev/ttyUSB*")
    exit(1)

print("✓ CLP conectado via serial\n")


def handle_modbus_tcp(client_socket, address):
    """Processa requisições Modbus TCP"""
    print(f"✓ Cliente conectado: {address}")

    try:
        while True:
            # Receber requisição Modbus TCP
            data = client_socket.recv(1024)
            if not data:
                break

            # Modbus TCP Header: [TID(2)][PID(2)][Len(2)][UID(1)][Function+Data]
            if len(data) < 8:
                continue

            transaction_id = data[0:2]
            protocol_id = data[2:4]
            length = int.from_bytes(data[4:6], 'big')
            unit_id = data[6]
            function_code = data[7]

            print(f"← TCP Request: Func={function_code:02X}, Unit={unit_id}, Len={length}")

            # Traduzir para comando Modbus RTU
            if function_code == 0x03:  # Read Holding Registers
                address = int.from_bytes(data[8:10], 'big')
                count = int.from_bytes(data[10:12], 'big')
                print(f"  Read Holding Regs: addr={address}, count={count}")

                result = serial_client.read_holding_registers(
                    address=address,
                    count=count,
                    device_id=unit_id
                )

                if not result.isError():
                    # Construir resposta Modbus TCP
                    registers = result.registers
                    byte_count = len(registers) * 2
                    response_data = bytearray([function_code, byte_count])

                    for reg in registers:
                        response_data.extend(reg.to_bytes(2, 'big'))

                    response_length = len(response_data) + 1  # +1 para unit_id
                    response = (
                        transaction_id +
                        protocol_id +
                        response_length.to_bytes(2, 'big') +
                        bytes([unit_id]) +
                        response_data
                    )

                    client_socket.send(response)
                    print(f"→ TCP Response: {len(registers)} registers, values={registers}")
                else:
                    print(f"✗ Modbus RTU error: {result}")

            elif function_code == 0x01:  # Read Coils
                address = int.from_bytes(data[8:10], 'big')
                count = int.from_bytes(data[10:12], 'big')
                print(f"  Read Coils: addr={address}, count={count}")

                result = serial_client.read_coils(
                    address, count, device_id=unit_id
                )

                if not result.isError():
                    bits = result.bits[:count]
                    byte_count = (count + 7) // 8
                    response_data = bytearray([function_code, byte_count])

                    # Converter bits para bytes
                    for i in range(0, count, 8):
                        byte_val = 0
                        for j in range(8):
                            if i + j < count and bits[i + j]:
                                byte_val |= (1 << j)
                        response_data.append(byte_val)

                    response_length = len(response_data) + 1
                    response = (
                        transaction_id +
                        protocol_id +
                        response_length.to_bytes(2, 'big') +
                        bytes([unit_id]) +
                        response_data
                    )

                    client_socket.send(response)
                    print(f"→ TCP Response: {count} coils")
                else:
                    print(f"✗ Modbus RTU error: {result}")

            elif function_code == 0x05:  # Write Single Coil
                address = int.from_bytes(data[8:10], 'big')
                value = int.from_bytes(data[10:12], 'big')
                print(f"  Write Coil: addr={address}, value={value}")

                result = serial_client.write_coil(
                    address, value != 0, device_id=unit_id
                )

                if not result.isError():
                    # Echo da requisição como resposta
                    response_data = data[8:12]
                    response_length = len(response_data) + 2
                    response = (
                        transaction_id +
                        protocol_id +
                        response_length.to_bytes(2, 'big') +
                        bytes([unit_id, function_code]) +
                        response_data
                    )
                    client_socket.send(response)
                    print(f"→ TCP Response: Write OK")
                else:
                    print(f"✗ Modbus RTU error: {result}")

            elif function_code == 0x06:  # Write Single Register
                address = int.from_bytes(data[8:10], 'big')
                value = int.from_bytes(data[10:12], 'big')
                print(f"  Write Register: addr={address}, value={value}")

                result = serial_client.write_register(
                    address, value, device_id=unit_id
                )

                if not result.isError():
                    response_data = data[8:12]
                    response_length = len(response_data) + 2
                    response = (
                        transaction_id +
                        protocol_id +
                        response_length.to_bytes(2, 'big') +
                        bytes([unit_id, function_code]) +
                        response_data
                    )
                    client_socket.send(response)
                    print(f"→ TCP Response: Write OK")
                else:
                    print(f"✗ Modbus RTU error: {result}")

            else:
                print(f"⚠ Função não suportada: {function_code:02X}")

    except Exception as e:
        print(f"✗ Erro: {e}")

    finally:
        print(f"✗ Cliente desconectado: {address}")
        client_socket.close()


# Servidor TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((TCP_HOST, TCP_PORT))
server_socket.listen(5)

print(f"✓ Servidor TCP escutando na porta {TCP_PORT}")
print("\nConfigure o WinSUP:")
print(f"  - Protocolo: Modbus TCP")
print(f"  - IP: 127.0.0.1")
print(f"  - Porta: {TCP_PORT}")
print(f"  - Slave ID: {SLAVE_ID}")
print("\nAguardando conexões...\n")

try:
    while True:
        client_socket, client_address = server_socket.accept()
        thread = threading.Thread(
            target=handle_modbus_tcp,
            args=(client_socket, client_address)
        )
        thread.daemon = True
        thread.start()

except KeyboardInterrupt:
    print("\n\nEncerrando...")
    serial_client.close()
    server_socket.close()
