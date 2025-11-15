#!/usr/bin/env python3
"""
TESTE AUTOMATIZADO DE SINCRONIZAÇÃO
Envia comandos via WebSocket e valida respostas
"""

import asyncio
import websockets
import json
from datetime import datetime

async def test_sync():
    ws_uri = "ws://localhost:8765"

    print("╔" + "="*68 + "╗")
    print("║" + " "*10 + "TESTE AUTOMATIZADO DE SINCRONIZAÇÃO" + " "*22 + "║")
    print("╚" + "="*68 + "╝\n")

    # Conectar
    print("🔌 Conectando ao WebSocket...")
    ws = await websockets.connect(ws_uri)
    initial_msg = await ws.recv()
    initial_data = json.loads(initial_msg)

    # Extrair estado da mensagem (formato: {'type': 'full_state', 'data': {...}})
    if 'data' in initial_data:
        state = initial_data['data']
    else:
        state = initial_data

    print(f"✅ Conectado! Estado inicial recebido\n")

    # Função auxiliar para aguardar atualização
    async def wait_update(timeout=3.0):
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=timeout)
            msg_data = json.loads(msg)

            # Extrair dados da mensagem
            if 'data' in msg_data:
                state.update(msg_data['data'])
                return msg_data['data']
            else:
                state.update(msg_data)
                return msg_data
        except asyncio.TimeoutError:
            return None

    print("="*70)
    print("TESTE 1: Mudança de Modo (toggle_mode)")
    print("="*70)

    # Estado inicial
    mode_antes = state.get('mode_text', 'DESCONHECIDO')
    mode_bit_antes = state.get('mode_bit_02ff')
    print(f"📖 Modo ANTES: {mode_antes} (bit 0x02FF = {mode_bit_antes})")

    # Enviar comando toggle_mode
    print("🔄 Enviando comando toggle_mode...")
    await ws.send(json.dumps({'action': 'toggle_mode'}))

    # Aguardar atualização
    print("⏳ Aguardando atualização...")
    for _ in range(5):
        update = await wait_update(timeout=1.0)
        if update and 'mode_text' in update:
            break
        await asyncio.sleep(0.2)

    # Verificar resultado
    mode_depois = state.get('mode_text', 'DESCONHECIDO')
    mode_bit_depois = state.get('mode_bit_02ff')
    print(f"📖 Modo DEPOIS: {mode_depois} (bit 0x02FF = {mode_bit_depois})")

    if mode_depois != mode_antes:
        print("✅ PASSOU: Modo mudou corretamente!")
        test1_ok = True
    else:
        print("❌ FALHOU: Modo não mudou")
        test1_ok = False

    print("\n" + "="*70)
    print("TESTE 2: Leitura de LEDs")
    print("="*70)

    leds = state.get('leds', {})
    print(f"📖 LEDs atuais:")
    print(f"   LED1 (K1): {'🟢 ON' if leds.get('LED1') else '⚫ OFF'}")
    print(f"   LED2 (K2): {'🟢 ON' if leds.get('LED2') else '⚫ OFF'}")
    print(f"   LED3 (K3): {'🟢 ON' if leds.get('LED3') else '⚫ OFF'}")

    if leds:
        print("✅ PASSOU: LEDs sendo lidos corretamente")
        test2_ok = True
    else:
        print("⚠️  AVISO: Sem dados de LEDs")
        test2_ok = False

    print("\n" + "="*70)
    print("TESTE 3: Leitura de Ângulos")
    print("="*70)

    angles = state.get('angles', {})
    if angles:
        print(f"📖 Ângulos atuais:")
        for name, value in angles.items():
            print(f"   {name}: {value}°")
        print("✅ PASSOU: Ângulos sendo lidos corretamente")
        test3_ok = True
    else:
        print("⚠️  AVISO: Sem dados de ângulos")
        test3_ok = False

    print("\n" + "="*70)
    print("RESUMO FINAL")
    print("="*70)

    tests = [
        ("Mudança de modo", test1_ok),
        ("Leitura de LEDs", test2_ok),
        ("Leitura de ângulos", test3_ok)
    ]

    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)

    for name, ok in tests:
        symbol = "✅" if ok else "❌"
        print(f"{symbol} {name}")

    print(f"\n📊 Resultado: {passed}/{total} testes passaram ({100*passed/total:.0f}%)")

    if passed == total:
        print("\n🎉 SUCESSO COMPLETO!")
        print("✅ IHM Web está sincronizada e funcional")
    else:
        print(f"\n⚠️  {total-passed} teste(s) falharam")

    await ws.close()
    print("\n🔌 Desconectado")

    return passed == total

if __name__ == '__main__':
    try:
        success = asyncio.run(test_sync())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
