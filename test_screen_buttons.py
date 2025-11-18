#!/usr/bin/env python3
"""
Teste de Mudança de Tela via Botões
====================================

Emula a IHM física pressionando botões K1, K2, K3, ESC
e verifica se o registro 0FEE (tela atual) muda.
"""

from pymodbus.client import ModbusSerialClient
import time

# Configuração
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

# Registros
REG_TELA_ATUAL = 0x0FEE  # 4078 decimal

# Botões (coils)
BTN_K1 = 0x00A0     # 160 - Dobra 1
BTN_K2 = 0x00A1     # 161 - Dobra 2
BTN_K3 = 0x00A2     # 162 - Dobra 3
BTN_ESC = 0x00BC    # 188 - Voltar/Cancelar
BTN_ENTER = 0x0025  # 37 - Confirmar
BTN_S1 = 0x00DC     # 220 - Modo AUTO/MANUAL

def press_button(client, button_addr, button_name):
    """Simula pressionar um botão da IHM física"""
    print(f"\n  → Pressionando {button_name}...", end=" ", flush=True)

    try:
        # Passo 1: Coil ON
        result = client.write_coil(button_addr, True, device_id=SLAVE_ID)
        if result.isError():
            print(f"✗ Erro ao ligar coil: {result}")
            return False

        # Passo 2: Hold 100ms
        time.sleep(0.1)

        # Passo 3: Coil OFF
        result = client.write_coil(button_addr, False, device_id=SLAVE_ID)
        if result.isError():
            print(f"✗ Erro ao desligar coil: {result}")
            return False

        print("✓ OK")

        # Passo 4: Aguarda processamento
        time.sleep(0.2)
        return True

    except Exception as e:
        print(f"✗ Exceção: {e}")
        return False

def read_screen(client):
    """Lê o registro de tela atual"""
    try:
        result = client.read_holding_registers(
            address=REG_TELA_ATUAL,
            count=1,
            device_id=SLAVE_ID
        )

        if result.isError():
            return None

        return result.registers[0]
    except:
        return None

print("=" * 70)
print("TESTE DE MUDANÇA DE TELA VIA BOTÕES")
print("=" * 70)
print(f"Porta: {PORT}")
print(f"Slave ID: {SLAVE_ID}\n")

# Conecta
client = ModbusSerialClient(
    port=PORT,
    baudrate=BAUDRATE,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1.0
)

if not client.connect():
    print("✗ ERRO: Não foi possível conectar")
    exit(1)

print("✓ Conexão Modbus estabelecida\n")

# Lê tela inicial
print("[Estado Inicial]")
screen = read_screen(client)
if screen is not None:
    print(f"  Tela atual: {screen} (0x{screen:04X})")
else:
    print("  ✗ Não foi possível ler tela inicial")
    client.close()
    exit(1)

initial_screen = screen

# Teste 1: Pressionar K1 (Dobra 1)
print("\n" + "-" * 70)
print("[Teste 1] Botão K1 - Selecionar Dobra 1")
print("-" * 70)

if press_button(client, BTN_K1, "K1"):
    screen = read_screen(client)
    if screen is not None:
        if screen != initial_screen:
            print(f"  ✓ TELA MUDOU! De {initial_screen} → {screen}")
        else:
            print(f"  • Tela permaneceu: {screen} (sem mudança)")
    else:
        print("  ✗ Erro ao ler tela após K1")

# Teste 2: Pressionar K2 (Dobra 2)
print("\n" + "-" * 70)
print("[Teste 2] Botão K2 - Selecionar Dobra 2")
print("-" * 70)

screen_before = read_screen(client)
if press_button(client, BTN_K2, "K2"):
    screen = read_screen(client)
    if screen is not None:
        if screen != screen_before:
            print(f"  ✓ TELA MUDOU! De {screen_before} → {screen}")
        else:
            print(f"  • Tela permaneceu: {screen} (sem mudança)")
    else:
        print("  ✗ Erro ao ler tela após K2")

# Teste 3: Pressionar K3 (Dobra 3)
print("\n" + "-" * 70)
print("[Teste 3] Botão K3 - Selecionar Dobra 3")
print("-" * 70)

screen_before = read_screen(client)
if press_button(client, BTN_K3, "K3"):
    screen = read_screen(client)
    if screen is not None:
        if screen != screen_before:
            print(f"  ✓ TELA MUDOU! De {screen_before} → {screen}")
        else:
            print(f"  • Tela permaneceu: {screen} (sem mudança)")
    else:
        print("  ✗ Erro ao ler tela após K3")

# Teste 4: Pressionar ESC (Voltar)
print("\n" + "-" * 70)
print("[Teste 4] Botão ESC - Voltar")
print("-" * 70)

screen_before = read_screen(client)
if press_button(client, BTN_ESC, "ESC"):
    screen = read_screen(client)
    if screen is not None:
        if screen != screen_before:
            print(f"  ✓ TELA MUDOU! De {screen_before} → {screen}")
        else:
            print(f"  • Tela permaneceu: {screen} (sem mudança)")
    else:
        print("  ✗ Erro ao ler tela após ESC")

# Teste 5: Sequência K1 → ENTER
print("\n" + "-" * 70)
print("[Teste 5] Sequência K1 → ENTER")
print("-" * 70)

screen_before = read_screen(client)
if press_button(client, BTN_K1, "K1"):
    time.sleep(0.1)
    if press_button(client, BTN_ENTER, "ENTER"):
        screen = read_screen(client)
        if screen is not None:
            if screen != screen_before:
                print(f"  ✓ TELA MUDOU! De {screen_before} → {screen}")
            else:
                print(f"  • Tela permaneceu: {screen} (sem mudança)")
        else:
            print("  ✗ Erro ao ler tela após sequência")

# Teste 6: Monitorar por 3 segundos para capturar mudanças
print("\n" + "-" * 70)
print("[Teste 6] Monitoramento contínuo (3 segundos)")
print("-" * 70)
print("  Verificando se tela muda espontaneamente...")

last_screen = read_screen(client)
for i in range(6):
    screen = read_screen(client)
    if screen is not None and screen != last_screen:
        print(f"  [{i*0.5:.1f}s] ✓ Mudança detectada: {last_screen} → {screen}")
        last_screen = screen
    elif screen is not None:
        print(f"  [{i*0.5:.1f}s] Tela: {screen}")
    time.sleep(0.5)

# Resultado final
print("\n" + "=" * 70)
print("TESTE CONCLUÍDO")
print("=" * 70)

final_screen = read_screen(client)
print(f"\nTela inicial: {initial_screen}")
print(f"Tela final:   {final_screen}")

if final_screen != initial_screen:
    print(f"\n✓ HOUVE MUDANÇA DE TELA! ({initial_screen} → {final_screen})")
    print("  → Registro 0FEE é atualizado pelo ladder")
    print("  → IHM web PODE sincronizar com tela do CLP!")
else:
    print(f"\n• Tela permaneceu em {initial_screen} durante todos os testes")
    print("  Possíveis causas:")
    print("    1. Registro 0FEE não é usado no ladder atual")
    print("    2. CLP está em modo que não permite mudança de tela")
    print("    3. Precisamos usar método alternativo (escrever em 0FEC)")

client.close()
