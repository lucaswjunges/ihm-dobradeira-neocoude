"""
Main Server ESP32 - IHM Web Dobradeira
Servidor HTTP simples + Modbus com threading
"""
import socket
import time
import json
import gc
import _thread
from machine import Pin
from modbus_client_esp32 import ModbusClientWrapper
import modbus_map as mm

# LED status (GPIO2)
led = Pin(5, Pin.OUT)  # Trocar para GPIO5 (GPIO2 usado pelo WiFi)

# Estado global
modbus = None
machine_state = {}

# Modo STUB (trocar para False quando conectar CLP)
STUB_MODE = False  # LIVE mode - comunica com CLP real
SLAVE_ID = 1

def init_system():
    """Inicializa sistema"""
    global modbus, machine_state

    print("\n" + "="*40)
    print("IHM WEB - SERVIDOR ESP32")
    print("="*40)

    # Inicializa Modbus
    print(f"\nModo: {'STUB (simulado)' if STUB_MODE else 'LIVE (CLP real)'}")
    modbus = ModbusClientWrapper(stub_mode=STUB_MODE, slave_id=SLAVE_ID)

    # Estado inicial
    machine_state = {
        'encoder_angle': 0.0,
        'bend_1_angle': 0.0,
        'bend_2_angle': 0.0,
        'bend_3_angle': 0.0,
        'speed_class': 1,
        'connected': modbus.connected
    }

    print("✓ Sistema inicializado")

def update_state():
    """Atualiza estado da máquina (executado em thread separada)"""
    global machine_state

    try:
        # Flag para detectar se QUALQUER leitura funcionou
        any_success = False

        # Encoder (32-bit) - com timeout implícito da biblioteca
        try:
            encoder_raw = modbus.read_register_32bit(mm.ENCODER['ANGLE_MSW'])
            if encoder_raw is not None:
                machine_state['encoder_angle'] = encoder_raw / 10.0
                any_success = True
        except:
            pass  # Timeout - não bloqueia

        # Ângulos setpoint
        try:
            bend1 = modbus.read_register(mm.BEND_ANGLES['BEND_1_SETPOINT'])
            if bend1 is not None:
                machine_state['bend_1_angle'] = bend1 / 10.0
                any_success = True
        except:
            pass

        try:
            bend2 = modbus.read_register(mm.BEND_ANGLES['BEND_2_SETPOINT'])
            if bend2 is not None:
                machine_state['bend_2_angle'] = bend2 / 10.0
                any_success = True
        except:
            pass

        try:
            bend3 = modbus.read_register(mm.BEND_ANGLES['BEND_3_SETPOINT'])
            if bend3 is not None:
                machine_state['bend_3_angle'] = bend3 / 10.0
                any_success = True
        except:
            pass

        # Velocidade (área de supervisão)
        try:
            speed_reg = modbus.read_register(mm.SUPERVISION_AREA['SPEED_CLASS'])
            if speed_reg is not None:
                # Converter classe (1,2,3) para RPM (5,10,15)
                speed_map = {1: 5, 2: 10, 3: 15}
                machine_state['speed_class'] = speed_map.get(speed_reg, 5)  # Default 5 rpm
                any_success = True
            # Se falhou, mantém valor anterior (não sobrescreve)
        except:
            pass  # Mantém valor anterior em caso de erro

        # Conexão OK se QUALQUER leitura funcionou
        machine_state['connected'] = any_success
    except Exception as e:
        print(f"⚠ Erro update_state: {e}")
        machine_state['connected'] = False

def modbus_worker():
    """Thread worker para polling Modbus contínuo"""
    print("✓ Thread Modbus iniciada")

    while True:
        try:
            update_state()
            time.sleep(0.5)  # Polling a cada 500ms
        except Exception as e:
            print(f"⚠ Erro modbus_worker: {e}")
            time.sleep(1)  # Espera mais em caso de erro

        # Garbage collection periódico
        gc.collect()

def handle_http_request(client_socket):
    """Processa requisição HTTP"""
    try:
        # Define timeout no socket cliente
        client_socket.settimeout(3.0)

        # Lê requisição
        request = client_socket.recv(2048).decode('utf-8')

        # Parse primeira linha
        if not request:
            return

        first_line = request.split('\r\n')[0]

        # GET /
        if 'GET / ' in first_line or 'GET /index.html' in first_line:
            try:
                # Lê e envia em chunks para economizar RAM
                with open('static/index.html', 'r') as f:
                    # Envia header primeiro
                    client_socket.send(b'HTTP/1.1 200 OK\r\n')
                    client_socket.send(b'Content-Type: text/html; charset=utf-8\r\n')
                    client_socket.send(b'Connection: close\r\n\r\n')

                    # Envia arquivo em chunks de 512 bytes
                    while True:
                        chunk = f.read(512)
                        if not chunk:
                            break
                        client_socket.send(chunk.encode('utf-8'))
                        gc.collect()  # Coleta após cada chunk

                print("✓ Serviu index.html")
            except Exception as e:
                print(f"✗ Erro ao ler index.html: {e}")
                client_socket.send(b'HTTP/1.1 500 Error\r\n\r\n')

        # Captive Portal Detection (Android/iOS)
        elif any(x in first_line for x in ['/generate_204', '/hotspot-detect.html',
                                             '/connecttest.txt', '/redirect']):
            # Responde 204 (success) para Android/iOS não reclamar
            client_socket.send(b'HTTP/1.1 204 No Content\r\n\r\n')
            print("✓ Captive portal check OK")

        # GET /api/state (endpoint para obter estado via polling)
        elif 'GET /api/state' in first_line:
            # NÃO chama update_state() - thread faz isso
            state_json = json.dumps(machine_state)

            response = 'HTTP/1.1 200 OK\r\n'
            response += 'Content-Type: application/json\r\n'
            response += 'Access-Control-Allow-Origin: *\r\n'
            response += f'Content-Length: {len(state_json)}\r\n'
            response += 'Connection: close\r\n\r\n'
            response += state_json

            client_socket.send(response.encode('utf-8'))

        # GET /api/test_modbus (endpoint de teste Modbus)
        elif 'GET /api/test_modbus' in first_line:
            # Testar leitura Modbus
            test_results = {
                'encoder_test': None,
                'bend1_test': None,
                'connected': modbus.connected
            }

            # Teste 1: Ler encoder
            try:
                encoder_val = modbus.read_register_32bit(mm.ENCODER['ANGLE_MSW'])
                test_results['encoder_test'] = {
                    'success': encoder_val is not None,
                    'value': encoder_val,
                    'degrees': encoder_val / 10.0 if encoder_val else 0
                }
            except Exception as e:
                test_results['encoder_test'] = {'success': False, 'error': str(e)}

            # Teste 2: Ler bend 1
            try:
                bend1_val = modbus.read_register(mm.BEND_ANGLES['BEND_1_SETPOINT'])
                test_results['bend1_test'] = {
                    'success': bend1_val is not None,
                    'value': bend1_val,
                    'degrees': bend1_val / 10.0 if bend1_val else 0
                }
            except Exception as e:
                test_results['bend1_test'] = {'success': False, 'error': str(e)}

            result_json = json.dumps(test_results)
            response = 'HTTP/1.1 200 OK\r\n'
            response += 'Content-Type: application/json\r\n'
            response += 'Access-Control-Allow-Origin: *\r\n'
            response += f'Content-Length: {len(result_json)}\r\n'
            response += 'Connection: close\r\n\r\n'
            response += result_json
            client_socket.send(response.encode('utf-8'))

        # GET /api/write_test?address=XXX&value=YYY (escrever registro de teste)
        elif 'GET /api/write_test' in first_line:
            # Extrair parâmetros da query string
            try:
                import re
                match_addr = re.search(r'address=(\d+)', first_line)
                match_val = re.search(r'value=(\d+)', first_line)

                if match_addr and match_val:
                    address = int(match_addr.group(1))
                    value = int(match_val.group(1))

                    success = modbus.write_register(address, value)
                    result = {
                        'success': success,
                        'address': address,
                        'value': value,
                        'message': 'OK' if success else 'FAILED'
                    }
                else:
                    result = {'success': False, 'message': 'Missing parameters'}

                result_json = json.dumps(result)
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/json\r\n'
                response += f'Content-Length: {len(result_json)}\r\n'
                response += 'Connection: close\r\n\r\n'
                response += result_json
                client_socket.send(response.encode('utf-8'))
            except Exception as e:
                error_msg = json.dumps({'success': False, 'error': str(e)})
                response = 'HTTP/1.1 500 Error\r\n'
                response += 'Content-Type: application/json\r\n'
                response += f'Content-Length: {len(error_msg)}\r\n'
                response += 'Connection: close\r\n\r\n'
                response += error_msg
                client_socket.send(response.encode('utf-8'))

        # GET /api/read_test?address=XXX (ler registro de teste)
        elif 'GET /api/read_test' in first_line:
            try:
                import re
                match_addr = re.search(r'address=(\d+)', first_line)

                if match_addr:
                    address = int(match_addr.group(1))
                    value = modbus.read_register(address)

                    result = {
                        'success': value is not None,
                        'address': address,
                        'value': value,
                        'hex': f'0x{value:04X}' if value else None
                    }
                else:
                    result = {'success': False, 'message': 'Missing address parameter'}

                result_json = json.dumps(result)
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/json\r\n'
                response += f'Content-Length: {len(result_json)}\r\n'
                response += 'Connection: close\r\n\r\n'
                response += result_json
                client_socket.send(response.encode('utf-8'))
            except Exception as e:
                error_msg = json.dumps({'success': False, 'error': str(e)})
                response = 'HTTP/1.1 500 Error\r\n\r\n' + error_msg
                client_socket.send(response.encode('utf-8'))

        # POST /api/command (endpoint para enviar comandos)
        elif 'POST /api/command' in first_line:
            # Extrai body JSON
            body_start = request.find('\r\n\r\n') + 4
            body = request[body_start:]

            try:
                cmd = json.loads(body)
                handle_command(cmd)

                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/json\r\n'
                response += 'Access-Control-Allow-Origin: *\r\n'
                response += 'Connection: close\r\n\r\n'
                response += '{"status":"ok"}'

                client_socket.send(response.encode('utf-8'))
                print(f"✓ Comando executado: {cmd.get('action')}")
            except Exception as e:
                print(f"✗ Erro comando: {e}")
                client_socket.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

        # 404
        else:
            client_socket.send(b'HTTP/1.1 404 Not Found\r\n\r\n')

    except OSError as e:
        # Timeout ou conexão fechada - normal
        pass
    except Exception as e:
        print(f"⚠ Erro HTTP: {e}")
    finally:
        try:
            client_socket.close()
        except:
            pass
        gc.collect()  # Coleta após cada requisição

def handle_command(cmd):
    """Processa comando recebido"""
    action = cmd.get('action')

    if action == 'press_key':
        key = cmd.get('key')
        addr = mm.KEYBOARD_FUNCTION.get(key) or mm.KEYBOARD_NUMERIC.get(key)
        if addr:
            modbus.press_key(addr)
            print(f"✓ Tecla: {key}")

    elif action == 'set_angle':
        bend = cmd.get('bend')
        value = int(cmd.get('value', 0) * 10)

        if bend == 1:
            modbus.write_register(mm.BEND_ANGLES['BEND_1_SETPOINT'], value)
        elif bend == 2:
            modbus.write_register(mm.BEND_ANGLES['BEND_2_SETPOINT'], value)
        elif bend == 3:
            modbus.write_register(mm.BEND_ANGLES['BEND_3_SETPOINT'], value)

        print(f"✓ Ângulo {bend} → {value/10}°")

    elif action == 'set_speed':
        speed_class = cmd.get('class', 1)
        modbus.write_register(mm.SUPERVISION_AREA['SPEED_CLASS'], speed_class)
        print(f"✓ Velocidade → Classe {speed_class}")

def start_server():
    """Inicia servidor HTTP"""
    # Iniciar thread Modbus ANTES do servidor HTTP
    if not STUB_MODE:
        print("Iniciando thread Modbus...")
        _thread.start_new_thread(modbus_worker, ())
        time.sleep(1)  # Aguardar primeira leitura

    # Socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', 80))
    server_socket.listen(2)  # Reduzido para 2 conexões simultâneas

    print("✓ Servidor HTTP iniciado em :80")
    print("✓ Pronto para receber conexões")
    print("="*40 + "\n")

    led.value(1)  # LED aceso = servidor rodando

    # Contador para GC agressivo
    request_count = 0

    # Loop principal
    while True:
        try:
            # Aceita conexão (timeout 1s para permitir outras tarefas)
            server_socket.settimeout(1.0)
            try:
                client_socket, addr = server_socket.accept()
                print(f"→ Cliente conectado: {addr[0]}")

                # Processa requisição
                handle_http_request(client_socket)

                # Incrementa contador
                request_count += 1

                # GC agressivo a cada 5 requisições
                if request_count >= 5:
                    gc.collect()
                    mem_free = gc.mem_free()
                    print(f"  [GC] RAM livre: {mem_free} bytes")
                    request_count = 0

            except OSError:
                # Timeout - sem problema, continua loop
                pass

        except KeyboardInterrupt:
            print("\n✗ Servidor encerrado pelo usuário")
            break
        except Exception as e:
            print(f"⚠ Erro servidor: {e}")
            gc.collect()
            time.sleep(1)

    server_socket.close()
    led.value(0)

# ========== MAIN ==========
try:
    init_system()
    start_server()
except Exception as e:
    print(f"✗ ERRO FATAL: {e}")
    import sys
    sys.print_exception(e)
