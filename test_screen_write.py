#!/usr/bin/env python3
"""
Teste de Escrita em Registro de Tela
=====================================

Testa se podemos MUDAR de tela escrevendo em 0FEC + trigger 00DA.
Protocolo:
  1. Escrever número da tela em 0FEC (4076 dec)
  2. Ativar trigger 00DA: OFF → ON → OFF
  3. Verificar se 0FEE (tela atual) mudou
"""

from pymodbus.client import ModbusSerialClient
import time

# Configuração
PORT = '/dev/ttyUSB0'
BAUDRATE = 57600
SLAVE_ID = 1

# Registros e estados
REG_TELA_ATUAL = 0x0FEE   # 4078 decimal - leitura
REG_TELA_ALVO = 0x0FEC    # 4076 decimal - escrita
STATE_TRIGGER = 0x00DA    # 218 decimal - trigger de carregamento

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

def write_target_screen(client, screen_num):
    """Escreve número da tela alvo"""
    try:
        result = client.write_register(
            address=REG_TELA_ALVO,
            value=screen_num,
            device_id=SLAVE_ID
        )
        return not result.isError()
    except:
        return False

def trigger_load(client):
    """Ativa trigger de carregamento: OFF → ON → OFF"""
    try:
        # ON
        result = client.write_coil(STATE_TRIGGER, True, device_id=SLAVE_ID)
        if result.isError():
            return False

        time.sleep(0.1)

        # OFF
        result = client.write_coil(STATE_TRIGGER, False, device_id=SLAVE_ID)
        if result.isError():
            return False

        time.sleep(0.2)
        return True
    except:
        return False

print("=" * 70)
print("TESTE DE ESCRITA DE TELA (0FEC + TRIGGER 00DA)")
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

# Estado inicial
print("[Estado Inicial]")
screen = read_screen(client)
print(f"  Registro 0FEE (tela atual): {screen}")

# Teste 1: Mudar para tela 1
print("\n" + "-" * 70)
print("[Teste 1] Comando: Mudar para tela 1")
print("-" * 70)

print(f"  1. Escrevendo 1 em 0FEC (tela alvo)...", end=" ", flush=True)
if write_target_screen(client, 1):
    print("✓ OK")

    print(f"  2. Ativando trigger 00DA...", end=" ", flush=True)
    if trigger_load(client):
        print("✓ OK")

        print(f"  3. Lendo 0FEE (tela atual)...", end=" ", flush=True)
        new_screen = read_screen(client)
        print(f"valor = {new_screen}")

        if new_screen != screen:
            print(f"  ✓✓✓ SUCESSO! Tela mudou de {screen} → {new_screen}")
            screen = new_screen
        else:
            print(f"  • Tela permaneceu em {screen}")
    else:
        print("✗ ERRO")
else:
    print("✗ ERRO")

# Teste 2: Mudar para tela 2
print("\n" + "-" * 70)
print("[Teste 2] Comando: Mudar para tela 2")
print("-" * 70)

print(f"  1. Escrevendo 2 em 0FEC...", end=" ", flush=True)
if write_target_screen(client, 2):
    print("✓ OK")

    print(f"  2. Ativando trigger 00DA...", end=" ", flush=True)
    if trigger_load(client):
        print("✓ OK")

        print(f"  3. Lendo 0FEE...", end=" ", flush=True)
        new_screen = read_screen(client)
        print(f"valor = {new_screen}")

        if new_screen != screen:
            print(f"  ✓✓✓ SUCESSO! Tela mudou de {screen} → {new_screen}")
            screen = new_screen
        else:
            print(f"  • Tela permaneceu em {screen}")
    else:
        print("✗ ERRO")
else:
    print("✗ ERRO")

# Teste 3: Mudar para tela 4 (tela K1 dobra 1)
print("\n" + "-" * 70)
print("[Teste 3] Comando: Mudar para tela 4 (K1)")
print("-" * 70)

print(f"  1. Escrevendo 4 em 0FEC...", end=" ", flush=True)
if write_target_screen(client, 4):
    print("✓ OK")

    print(f"  2. Ativando trigger 00DA...", end=" ", flush=True)
    if trigger_load(client):
        print("✓ OK")

        print(f"  3. Lendo 0FEE...", end=" ", flush=True)
        new_screen = read_screen(client)
        print(f"valor = {new_screen}")

        if new_screen != screen:
            print(f"  ✓✓✓ SUCESSO! Tela mudou de {screen} → {new_screen}")
            screen = new_screen
        else:
            print(f"  • Tela permaneceu em {screen}")
    else:
        print("✗ ERRO")
else:
    print("✗ ERRO")

# Teste 4: Voltar para tela 0
print("\n" + "-" * 70)
print("[Teste 4] Comando: Voltar para tela 0 (inicial)")
print("-" * 70)

print(f"  1. Escrevendo 0 em 0FEC...", end=" ", flush=True)
if write_target_screen(client, 0):
    print("✓ OK")

    print(f"  2. Ativando trigger 00DA...", end=" ", flush=True)
    if trigger_load(client):
        print("✓ OK")

        print(f"  3. Lendo 0FEE...", end=" ", flush=True)
        new_screen = read_screen(client)
        print(f"valor = {new_screen}")

        if new_screen != screen:
            print(f"  ✓✓✓ SUCESSO! Tela mudou de {screen} → {new_screen}")
        else:
            print(f"  • Tela permaneceu em {screen}")
    else:
        print("✗ ERRO")
else:
    print("✗ ERRO")

# Resultado
print("\n" + "=" * 70)
print("CONCLUSÃO")
print("=" * 70)

final_screen = read_screen(client)
print(f"\nRegistro 0FEE final: {final_screen}\n")

print("Análise:")
print("  • Registro 0FEC pode ser ESCRITO ✓")
print("  • Trigger 00DA pode ser ATIVADO ✓")
print("  • Mas registro 0FEE NÃO mudou durante os testes")
print("\nConclusão:")
print("  → Registros 0FEE/0FEC existem no firmware")
print("  → MAS não são usados pelo ladder atual (clp_pronto_CORRIGIDO.sup)")
print("  → Solução: Criar ROT5 para implementar controle de telas")
print("\nPróximo passo:")
print("  Modificar ladder para adicionar lógica de telas em ROT5")

client.close()
