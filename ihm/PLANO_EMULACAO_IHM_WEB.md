# PLANO DE EMULAÇÃO ARTIFICIAL PRECISA - IHM WEB

**Objetivo**: Emular sequências de operação da IHM física e validar se a IHM Web reflete EXATAMENTE os mesmos valores.

**Data**: 15/Nov/2025 04:00 BRT

---

## 📋 ESTRATÉGIA DE VALIDAÇÃO

### Fase 1: LEITURA DE ESTADO INICIAL
Ler todos os valores atuais do CLP e IHM Web para estabelecer baseline.

### Fase 2: EMULAÇÃO DE OPERAÇÕES
Simular operações via Modbus e verificar se IHM Web reflete as mudanças.

### Fase 3: VALIDAÇÃO DE SINCRONIZAÇÃO
Comparar valores lidos diretamente do CLP vs valores mostrados na IHM Web.

---

## 🎯 CENÁRIOS DE TESTE

### CENÁRIO 1: Mudança de Modo (MANUAL ↔ AUTO)

**Passos**:
1. Ler modo atual do CLP (bit 0x02FF)
2. Ler modo atual da IHM Web (via WebSocket)
3. Alternar modo via `change_mode_direct()`
4. Aguardar 500ms
5. Ler modo do CLP novamente
6. Ler modo da IHM Web novamente
7. **VALIDAÇÃO**: CLP e IHM Web devem mostrar o mesmo modo

**Valores esperados**:
- CLP bit 0x02FF: 0 = MANUAL, 1 = AUTO
- IHM Web `mode_bit_02ff`: 0 = MANUAL, 1 = AUTO
- IHM Web `mode_text`: "MANUAL" ou "AUTO"

---

### CENÁRIO 2: Ativação de LEDs (Dobras)

**Passos**:
1. Ler LEDs K1, K2, K3 do CLP (coils 0x00C0, 0x00C1, 0x00C2)
2. Ler LEDs da IHM Web (via WebSocket)
3. Forçar LED K1 ON via Modbus
4. Aguardar 500ms
5. Ler LEDs do CLP novamente
6. Ler LEDs da IHM Web novamente
7. **VALIDAÇÃO**: CLP e IHM Web devem mostrar LED K1 ON

**Valores esperados**:
- CLP coil 0x00C0: 1 (LED K1 ON)
- IHM Web `leds.LED1`: true
- IHM Web `bend_current`: 1 (inferido)

---

### CENÁRIO 3: Escrita de Ângulo

**Passos**:
1. Ler ângulo Dobra 1 Esquerda do CLP (0x0840/0x0842)
2. Ler ângulo da IHM Web (via WebSocket)
3. Escrever ângulo 90.5° via Modbus
4. Aguardar 500ms
5. Ler ângulo do CLP novamente
6. Ler ângulo da IHM Web novamente
7. **VALIDAÇÃO**: CLP e IHM Web devem mostrar 90.5°

**Valores esperados**:
- CLP registros 0x0840/0x0842: MSW=0, LSW=905 → 90.5°
- IHM Web `angles.bend_1_left`: 90.5

---

### CENÁRIO 4: Leitura de Tela (se disponível)

**Passos**:
1. Tentar ler registro de tela do CLP (se existir)
2. Ler tela inferida da IHM Web
3. **VALIDAÇÃO**: Verificar se inferência está correta

**Nota**: A tela pode não estar disponível no CLP (área 0x0940 vazia).

---

## 🔧 IMPLEMENTAÇÃO DO SCRIPT DE TESTE

### Script: `test_emulacao_ihm_web.py`

```python
#!/usr/bin/env python3
"""
TESTE DE EMULAÇÃO ARTIFICIAL - IHM WEB
Valida sincronização precisa entre CLP e IHM Web
"""

import asyncio
import websockets
import json
import time
from modbus_client import ModbusClientWrapper

class IHMWebValidator:
    def __init__(self):
        # Cliente Modbus para ler diretamente do CLP
        self.modbus = ModbusClientWrapper(port='/dev/ttyUSB0', stub_mode=False)
        
        # WebSocket para ler dados da IHM Web
        self.ws_uri = "ws://localhost:8765"
        self.ihm_web_state = {}
        
    async def connect_websocket(self):
        """Conecta ao WebSocket da IHM Web"""
        self.ws = await websockets.connect(self.ws_uri)
        msg = await self.ws.recv()
        data = json.loads(msg)
        if data['type'] == 'full_state':
            self.ihm_web_state = data['data']
        return True
    
    async def update_ihm_web_state(self):
        """Atualiza estado da IHM Web via WebSocket"""
        try:
            msg = await asyncio.wait_for(self.ws.recv(), timeout=1.0)
            data = json.loads(msg)
            if data['type'] in ['full_state', 'state_update']:
                self.ihm_web_state.update(data.get('data', {}))
        except asyncio.TimeoutError:
            pass
    
    def read_clp_mode(self):
        """Lê modo diretamente do CLP"""
        return self.modbus.read_coil(0x02FF)  # 0=MANUAL, 1=AUTO
    
    def read_ihm_web_mode(self):
        """Lê modo da IHM Web"""
        return self.ihm_web_state.get('mode_bit_02ff')
    
    def read_clp_leds(self):
        """Lê LEDs diretamente do CLP"""
        return {
            'LED1': self.modbus.read_coil(0x00C0),  # LED K1
            'LED2': self.modbus.read_coil(0x00C1),  # LED K2
            'LED3': self.modbus.read_coil(0x00C2),  # LED K3
        }
    
    def read_ihm_web_leds(self):
        """Lê LEDs da IHM Web"""
        return self.ihm_web_state.get('leds', {})
    
    def read_clp_angle(self, bend_num, direction):
        """Lê ângulo diretamente do CLP (32-bit)"""
        addr_map = {
            (1, 'left'):  (0x0840, 0x0842),
            (2, 'left'):  (0x0848, 0x084A),
            (3, 'left'):  (0x0850, 0x0852),
            (1, 'right'): (0x0841, 0x0843),
            (2, 'right'): (0x0849, 0x084B),
            (3, 'right'): (0x0851, 0x0853),
        }
        msw_addr, lsw_addr = addr_map[(bend_num, direction)]
        value_32bit = self.modbus.read_32bit(msw_addr, lsw_addr)
        return value_32bit / 10.0 if value_32bit is not None else None
    
    def read_ihm_web_angle(self, bend_num, direction):
        """Lê ângulo da IHM Web"""
        key = f"bend_{bend_num}_{direction}"
        return self.ihm_web_state.get('angles', {}).get(key)
    
    async def test_scenario_1_mode_change(self):
        """CENÁRIO 1: Mudança de Modo"""
        print("\n" + "="*70)
        print("CENÁRIO 1: MUDANÇA DE MODO (MANUAL ↔ AUTO)")
        print("="*70)
        
        # 1. Estado inicial
        print("\n1. ESTADO INICIAL")
        clp_mode_before = self.read_clp_mode()
        await self.update_ihm_web_state()
        ihm_mode_before = self.read_ihm_web_mode()
        
        print(f"   CLP (0x02FF):     {clp_mode_before} ({'AUTO' if clp_mode_before else 'MANUAL'})")
        print(f"   IHM Web:          {ihm_mode_before} ({'AUTO' if ihm_mode_before else 'MANUAL'})")
        
        # Validação inicial
        if clp_mode_before == ihm_mode_before:
            print(f"   ✅ SINCRONIZADO")
        else:
            print(f"   ❌ DESSINCRONIZADO!")
        
        # 2. Alternar modo
        print("\n2. ALTERNANDO MODO VIA MODBUS")
        new_mode = not clp_mode_before
        success = self.modbus.change_mode_direct(to_auto=new_mode)
        print(f"   Escrita: {'✅ Sucesso' if success else '❌ Falha'}")
        
        # 3. Aguardar sincronização
        print("\n3. AGUARDANDO SINCRONIZAÇÃO (500ms)")
        await asyncio.sleep(0.5)
        
        # 4. Estado final
        print("\n4. ESTADO FINAL")
        clp_mode_after = self.read_clp_mode()
        await self.update_ihm_web_state()
        ihm_mode_after = self.read_ihm_web_mode()
        
        print(f"   CLP (0x02FF):     {clp_mode_after} ({'AUTO' if clp_mode_after else 'MANUAL'})")
        print(f"   IHM Web:          {ihm_mode_after} ({'AUTO' if ihm_mode_after else 'MANUAL'})")
        
        # Validação final
        if clp_mode_after == ihm_mode_after == new_mode:
            print(f"   ✅ SINCRONIZADO E MUDOU CORRETAMENTE")
            return True
        else:
            print(f"   ❌ FALHA NA SINCRONIZAÇÃO!")
            return False
    
    async def test_scenario_2_led_activation(self):
        """CENÁRIO 2: Ativação de LEDs"""
        print("\n" + "="*70)
        print("CENÁRIO 2: ATIVAÇÃO DE LED K1 (DOBRA 1)")
        print("="*70)
        
        # 1. Estado inicial
        print("\n1. ESTADO INICIAL DOS LEDs")
        clp_leds_before = self.read_clp_leds()
        await self.update_ihm_web_state()
        ihm_leds_before = self.read_ihm_web_leds()
        
        print(f"   CLP LED K1:  {clp_leds_before['LED1']}")
        print(f"   IHM LED K1:  {ihm_leds_before.get('LED1')}")
        
        # 2. Forçar LED K1 ON
        print("\n2. FORÇANDO LED K1 = ON")
        success = self.modbus.write_coil(0x00C0, True)
        print(f"   Escrita: {'✅ Sucesso' if success else '❌ Falha'}")
        
        # 3. Aguardar
        print("\n3. AGUARDANDO SINCRONIZAÇÃO (500ms)")
        await asyncio.sleep(0.5)
        
        # 4. Estado final
        print("\n4. ESTADO FINAL DOS LEDs")
        clp_leds_after = self.read_clp_leds()
        await self.update_ihm_web_state()
        ihm_leds_after = self.read_ihm_web_leds()
        
        print(f"   CLP LED K1:  {clp_leds_after['LED1']}")
        print(f"   IHM LED K1:  {ihm_leds_after.get('LED1')}")
        
        # Validação
        if clp_leds_after['LED1'] == ihm_leds_after.get('LED1') == True:
            print(f"   ✅ SINCRONIZADO - LED K1 ATIVO")
            return True
        else:
            print(f"   ❌ FALHA NA SINCRONIZAÇÃO!")
            return False
    
    async def test_scenario_3_angle_write(self):
        """CENÁRIO 3: Escrita de Ângulo"""
        print("\n" + "="*70)
        print("CENÁRIO 3: ESCRITA DE ÂNGULO (Dobra 1 Esquerda = 90.5°)")
        print("="*70)
        
        # 1. Estado inicial
        print("\n1. ÂNGULO INICIAL")
        clp_angle_before = self.read_clp_angle(1, 'left')
        await self.update_ihm_web_state()
        ihm_angle_before = self.read_ihm_web_angle(1, 'left')
        
        print(f"   CLP:      {clp_angle_before}°")
        print(f"   IHM Web:  {ihm_angle_before}°")
        
        # 2. Escrever ângulo
        print("\n2. ESCREVENDO ÂNGULO 90.5°")
        success = self.modbus.write_angle(1, 'left', 90.5)
        print(f"   Escrita: {'✅ Sucesso' if success else '❌ Falha'}")
        
        # 3. Aguardar
        print("\n3. AGUARDANDO SINCRONIZAÇÃO (500ms)")
        await asyncio.sleep(0.5)
        
        # 4. Estado final
        print("\n4. ÂNGULO FINAL")
        clp_angle_after = self.read_clp_angle(1, 'left')
        await self.update_ihm_web_state()
        ihm_angle_after = self.read_ihm_web_angle(1, 'left')
        
        print(f"   CLP:      {clp_angle_after}°")
        print(f"   IHM Web:  {ihm_angle_after}°")
        
        # Validação (tolerância de 0.1°)
        if clp_angle_after is not None and ihm_angle_after is not None:
            if abs(clp_angle_after - 90.5) < 0.1 and abs(ihm_angle_after - 90.5) < 0.1:
                print(f"   ✅ SINCRONIZADO - ÂNGULO CORRETO")
                return True
        
        print(f"   ❌ FALHA NA SINCRONIZAÇÃO!")
        return False
    
    async def run_all_tests(self):
        """Executa todos os cenários de teste"""
        print("\n" + "╔" + "="*68 + "╗")
        print("║" + " "*15 + "TESTE DE EMULAÇÃO IHM WEB" + " "*28 + "║")
        print("╚" + "="*68 + "╝")
        
        # Conectar WebSocket
        print("\n📡 Conectando ao WebSocket...")
        await self.connect_websocket()
        print("✅ Conectado!")
        
        # Executar cenários
        results = {}
        results['modo'] = await self.test_scenario_1_mode_change()
        results['led'] = await self.test_scenario_2_led_activation()
        results['angulo'] = await self.test_scenario_3_angle_write()
        
        # Resumo
        print("\n" + "="*70)
        print("RESUMO DOS TESTES")
        print("="*70)
        
        passed = sum(1 for v in results.values() if v)
        total = len(results)
        
        for name, result in results.items():
            icon = "✅" if result else "❌"
            print(f"{icon} {name.upper():15s}: {'PASSOU' if result else 'FALHOU'}")
        
        print("\n" + "-"*70)
        print(f"RESULTADO: {passed}/{total} testes passaram ({passed*100//total}%)")
        print("-"*70)
        
        if passed == total:
            print("\n🎉 IHM WEB ESTÁ 100% SINCRONIZADA COM O CLP!")
        else:
            print("\n⚠️  VERIFICAR SINCRONIZAÇÃO")
        
        # Cleanup
        await self.ws.close()
        self.modbus.close()

# Execução
async def main():
    validator = IHMWebValidator()
    await validator.run_all_tests()

if __name__ == '__main__':
    asyncio.run(main())
```

---

## ✅ CHECKLIST DE VALIDAÇÃO

### PRÉ-REQUISITOS
- [ ] Servidor IHM Web rodando (PID verificado)
- [ ] CLP conectado em /dev/ttyUSB0
- [ ] WebSocket acessível em localhost:8765
- [ ] Modbus respondendo (teste com mbpoll)

### CENÁRIO 1: Modo
- [ ] Modo lido do CLP (bit 0x02FF)
- [ ] Modo lido da IHM Web (WebSocket)
- [ ] Valores iniciais sincronizados
- [ ] Modo alterado via Modbus
- [ ] CLP reflete mudança
- [ ] IHM Web reflete mudança
- [ ] Valores finais sincronizados

### CENÁRIO 2: LEDs
- [ ] LEDs lidos do CLP (coils 0x00C0-0x00C2)
- [ ] LEDs lidos da IHM Web
- [ ] Valores iniciais sincronizados
- [ ] LED K1 forçado ON via Modbus
- [ ] CLP mostra LED K1 = ON
- [ ] IHM Web mostra LED K1 = ON
- [ ] Valores finais sincronizados

### CENÁRIO 3: Ângulos
- [ ] Ângulo lido do CLP (0x0840/0x0842)
- [ ] Ângulo lido da IHM Web
- [ ] Valores iniciais sincronizados
- [ ] Ângulo 90.5° escrito via Modbus
- [ ] CLP mostra 90.5° (±0.1°)
- [ ] IHM Web mostra 90.5° (±0.1°)
- [ ] Valores finais sincronizados

---

## 📊 CRITÉRIOS DE SUCESSO

**TESTE PASSOU** se:
- ✅ 100% dos cenários passaram
- ✅ CLP e IHM Web sempre mostram valores idênticos
- ✅ Mudanças via Modbus refletem em ambos

**TESTE FALHOU** se:
- ❌ Qualquer cenário mostrou dessincronização
- ❌ IHM Web não reflete mudanças do CLP
- ❌ Valores divergem além da tolerância

---

## 🚀 EXECUÇÃO

```bash
# Garantir servidor rodando
lsof -i :8765

# Executar teste de emulação
python3 test_emulacao_ihm_web.py

# Analisar resultados
# Esperado: 3/3 testes passaram (100%)
```

---

**Próximo passo**: Implementar script e executar validação completa.
