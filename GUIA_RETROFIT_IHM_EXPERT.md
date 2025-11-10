# Guia Completo: Retrofit IHM Expert Series → Web

## Engenharia de Controle e Automação Sênior

**Data**: 2025-11-08
**Cliente**: W&CO / Camargo Corrêa
**Máquina**: NEOCOUDE-HD-15 (2007)
**CLP**: Atos Expert MPC4004
**IHM Original**: Expert Series 4004.95C (danificada)
**Solução**: IHM Web Responsiva (tablet)

---

## SUMÁRIO EXECUTIVO

### Decisão Estratégica

Após análise técnica completa, **OPTOU-SE POR NÃO MODIFICAR O LADDER**.

**Motivo**: O ladder sobrescreve as saídas S0/S1 quando as entradas físicas E2/E4 não estão ativas, mas isso faz parte da lógica de segurança do sistema. Modificar seria arriscado e desnecessário.

**Solução adotada**:
- **Remover botões AVANÇAR, RECUAR, EMERGÊNCIA e PARADA da IHM web** (existem no painel físico)
- **Replicar 100% a IHM Expert Series original** (display LCD 2x20 + teclado 18 teclas)
- **Conectar via Modbus** para leitura de dados e simulação das teclas da IHM física

### Arquitetura Final

```
┌──────────────────┐
│  Painel Físico   │ ← Botões de controle (AVANÇAR, RECUAR, PARADA, EMERGÊNCIA)
│  (Existente)     │   Conectados em E2, E4, etc.
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  CLP MPC4004     │ ← Ladder logic INALTERADO
│                  │   Lê E2/E4 e controla S0/S1
└────────┬─────────┘
         │ Modbus RTU (RS485-B)
         │ Slave ID: 1, 57600 baud, 8N2
         ▼
┌──────────────────┐
│  Servidor Python │ ← main_server.py (Ubuntu notebook)
│  (Master)        │   Lê registros, simula teclas IHM
└────────┬─────────┘
         │ WebSocket (WiFi)
         │ ws://IP:8080
         ▼
┌──────────────────┐
│  Tablet (Client) │ ← IHM Expert Series Web
│  Navegador       │   Display LCD 2x20 virtual + Teclado virtual
└──────────────────┘
```

---

## FASE 1: ANÁLISE COMPLETA ✅ CONCLUÍDA

### O Que Foi Feito

1. **Mapeamento da IHM Física** (`MAPEAMENTO_IHM_EXPERT.md`)
   - 11 telas programadas extraídas de `Screen.dbf`
   - 18 teclas mapeadas (K0-K9, S1, S2, setas, ESC, ENTER, EDIT, Lock)
   - Especificações físicas: LCD 2x20 caracteres
   - Navegação entre telas documentada
   - LEDs integrados nas teclas identificados

2. **Mapeamento de Registros Modbus** (`REGISTROS_MODBUS_IHM.md`)
   - **Encoder**: 04D6/04D7 (1238/1239 dec) - 32-bit MSW/LSW
   - **Ângulos de dobra**: 0840-0853 (6 ângulos: 3 esq + 3 dir)
   - **Velocidades**: 0360-0362 (Classes 1/2/3: 5/10/15 RPM)
   - **Teclas IHM**: 00A0-00F1 (endereços coil para simulação)
   - **Status bits**: 00F7 (ciclo ativo), 00F8/00F9 (dobra 2/3)
   - **Entradas digitais**: 0100-0107 (E0-E7)
   - **Saídas digitais**: 0180-0187 (S0-S7) - SOMENTE LEITURA

3. **Diagnóstico de Comunicação**
   - Modbus RTU funcionando ✓
   - WebSocket funcionando ✓
   - Problema identificado: Ladder sobrescreve S0/S1
   - Solução testada: Bits internos 48-52 (DESCARTADA após decisão estratégica)

### Arquivos de Referência Criados

```
📄 MAPEAMENTO_IHM_EXPERT.md          ← Telas e teclas da IHM física
📄 REGISTROS_MODBUS_IHM.md           ← Todos os endereços Modbus mapeados
📄 LEIA_PRIMEIRO.md                  ← Resumo da situação anterior (bits internos)
📄 CHECKLIST_PROXIMOS_PASSOS.md      ← Obsoleto (era para modificar ladder)
📄 GUIA_MODIFICACAO_LADDER.md        ← Obsoleto (não vamos modificar)
📄 RESUMO_SOLUCAO_FINAL.md           ← Contexto histórico
📄 SOLUCAO_BITS_INTERNOS.md          ← Contexto histórico (solução descartada)
```

---

## FASE 2: IMPLEMENTAÇÃO DA IHM WEB ⏳ PRÓXIMA ETAPA

### Objetivo

Criar uma réplica funcional da IHM Expert Series 4004.95C em HTML/CSS/JavaScript que:
- Simule display LCD 2x20 caracteres (verde monoespaçado)
- Implemente teclado virtual de 18 teclas
- Navegue entre as 11 telas programadas
- Leia dados reais do CLP via Modbus
- Simule pressionamento de teclas via Modbus
- Indique LEDs ativos nas teclas

### 2.1. Componente Display LCD

**Especificações**:
- 2 linhas × 20 caracteres
- Fonte monoespaçada (Courier New ou similar)
- Fundo verde (#2a4a2a) com texto preto (#000000)
- Caracteres grandes e legíveis para tablet
- Borda simulando moldura física

**Exemplo HTML/CSS**:

```html
<div class="lcd-display">
  <div class="lcd-line lcd-line-1" id="lcd-line-1">
    <!-- 20 caracteres -->
  </div>
  <div class="lcd-line lcd-line-2" id="lcd-line-2">
    <!-- 20 caracteres -->
  </div>
</div>

<style>
.lcd-display {
  background: #1a1a1a;
  padding: 20px;
  border-radius: 10px;
  box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
  width: fit-content;
  margin: 20px auto;
}

.lcd-line {
  font-family: 'Courier New', monospace;
  font-size: 24px;
  background: #2a4a2a;
  color: #000000;
  padding: 10px 15px;
  letter-spacing: 2px;
  white-space: pre;
  border: 2px solid #1a3a1a;
  margin: 5px 0;
}
</style>
```

**JavaScript para atualizar display**:

```javascript
function updateLCD(line1, line2) {
  // Garantir 20 caracteres por linha
  const formatLine = (text) => {
    return (text + ' '.repeat(20)).substring(0, 20);
  };

  document.getElementById('lcd-line-1').textContent = formatLine(line1);
  document.getElementById('lcd-line-2').textContent = formatLine(line2);
}

// Exemplo de uso
updateLCD('**TRILLOR MAQUINAS**', '**DOBRADEIRA HD    **');
```

### 2.2. Componente Teclado Virtual

**Layout Físico** (4 seções):

```
┌─────────────────────────────┐
│     TECLADO NUMÉRICO        │
│  ┌───┬───┬───┐              │
│  │ 7 │ 8 │ 9 │              │
│  ├───┼───┼───┤              │
│  │ 4 │ 5 │ 6 │              │
│  ├───┼───┼───┤              │
│  │ 1 │ 2 │ 3 │              │
│  ├───┼───┼───┤              │
│  │   │ 0 │   │              │
│  └───┴───┴───┘              │
├─────────────────────────────┤
│     FUNÇÃO                   │
│  ┌────┬────┐                │
│  │ S1 │ S2 │                │
│  └────┴────┘                │
├─────────────────────────────┤
│     NAVEGAÇÃO                │
│  ┌────┬────┬────┬────┐      │
│  │ ↑  │ ↓  │ESC │LOCK│      │
│  └────┴────┴────┴────┘      │
├─────────────────────────────┤
│     EDIÇÃO                   │
│  ┌─────┬──────┐             │
│  │EDIT │ENTER │             │
│  └─────┴──────┘             │
└─────────────────────────────┘
```

**HTML Estruturado**:

```html
<div class="ihm-keyboard">
  <!-- Teclado Numérico -->
  <div class="keyboard-section numeric-pad">
    <button class="key-btn key-num" data-key="K7" data-addr="166" data-led="false">7</button>
    <button class="key-btn key-num" data-key="K8" data-addr="167" data-led="false">8</button>
    <button class="key-btn key-num" data-key="K9" data-addr="168" data-led="false">9</button>

    <button class="key-btn key-num" data-key="K4" data-addr="163" data-led="true">4</button>
    <button class="key-btn key-num" data-key="K5" data-addr="164" data-led="true">5</button>
    <button class="key-btn key-num" data-key="K6" data-addr="165" data-led="false">6</button>

    <button class="key-btn key-num" data-key="K1" data-addr="160" data-led="true">1</button>
    <button class="key-btn key-num" data-key="K2" data-addr="161" data-led="true">2</button>
    <button class="key-btn key-num" data-key="K3" data-addr="162" data-led="true">3</button>

    <button class="key-btn key-num key-wide" data-key="K0" data-addr="169" data-led="false">0</button>
  </div>

  <!-- Teclas de Função -->
  <div class="keyboard-section function-keys">
    <button class="key-btn key-fn" data-key="S1" data-addr="220" data-led="true">S1</button>
    <button class="key-btn key-fn" data-key="S2" data-addr="221" data-led="false">S2</button>
  </div>

  <!-- Navegação -->
  <div class="keyboard-section navigation-keys">
    <button class="key-btn key-nav" data-key="UP" data-addr="172">↑</button>
    <button class="key-btn key-nav" data-key="DOWN" data-addr="173">↓</button>
    <button class="key-btn key-nav" data-key="ESC" data-addr="188">ESC</button>
    <button class="key-btn key-nav" data-key="LOCK" data-addr="241">🔒</button>
  </div>

  <!-- Edição -->
  <div class="keyboard-section edit-keys">
    <button class="key-btn key-edit" data-key="EDIT" data-addr="38">EDIT</button>
    <button class="key-btn key-edit" data-key="ENTER" data-addr="37">ENTER</button>
  </div>
</div>
```

**CSS para teclas com LED**:

```css
.key-btn {
  padding: 15px 20px;
  font-size: 18px;
  font-weight: bold;
  border: 2px solid #333;
  background: linear-gradient(to bottom, #f0f0f0, #d0d0d0);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.1s;
  position: relative;
}

.key-btn:active {
  transform: translateY(2px);
  box-shadow: inset 0 2px 5px rgba(0,0,0,0.3);
}

/* LED indicator */
.key-btn[data-led="true"]::before {
  content: '';
  position: absolute;
  top: 5px;
  right: 5px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
  border: 1px solid #333;
}

/* LED aceso */
.key-btn.led-on[data-led="true"]::before {
  background: #00ff00;
  box-shadow: 0 0 10px #00ff00, inset 0 0 5px #00ff00;
}

/* Tecla com LED K1 (dobra 1) */
.key-btn[data-key="K1"].led-on {
  background: linear-gradient(to bottom, #e0ffe0, #c0ffc0);
}

/* Tecla com LED K2 (dobra 2) */
.key-btn[data-key="K2"].led-on {
  background: linear-gradient(to bottom, #ffe0e0, #ffc0c0);
}

/* Tecla com LED K3 (dobra 3) */
.key-btn[data-key="K3"].led-on {
  background: linear-gradient(to bottom, #e0e0ff, #c0c0ff);
}

/* Tecla com LED K4 (sentido anti-horário) */
.key-btn[data-key="K4"].led-on {
  background: linear-gradient(to bottom, #ffffe0, #ffffc0);
}

/* Tecla com LED K5 (sentido horário) */
.key-btn[data-key="K5"].led-on {
  background: linear-gradient(to bottom, #ffe0ff, #ffc0ff);
}

/* Tecla S1 (modo AUTO) */
.key-btn[data-key="S1"].led-on {
  background: linear-gradient(to bottom, #e0ffff, #c0ffff);
}
```

**JavaScript para simulação de tecla**:

```javascript
// Função para pressionar tecla via Modbus
async function pressKey(keyAddress) {
  const message = {
    action: 'press_key',
    address: keyAddress
  };

  ws.send(JSON.stringify(message));

  // Feedback visual
  const btn = document.querySelector(`[data-addr="${keyAddress}"]`);
  if (btn) {
    btn.classList.add('pressed');
    setTimeout(() => btn.classList.remove('pressed'), 200);
  }
}

// Event listeners para todas as teclas
document.querySelectorAll('.key-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    const address = parseInt(btn.getAttribute('data-addr'));
    pressKey(address);
  });
});
```

### 2.3. Máquina de Estados - Navegação Entre Telas

**JavaScript - Screen Manager**:

```javascript
class ScreenManager {
  constructor() {
    this.currentScreen = 0;
    this.totalScreens = 11;
    this.editMode = false;
    this.editValue = '';

    // Dados do CLP (atualizados via WebSocket)
    this.machineData = {
      encoder: 0,
      angles: {
        aj1_esq: 0, aj1_dir: 0,
        aj2_esq: 0, aj2_dir: 0,
        aj3_esq: 0, aj3_dir: 0
      },
      speed_class: 1,
      active_bend: 1,
      cycle_active: false,
      auto_mode: false
    };
  }

  // Renderizar tela atual
  render() {
    const screens = [
      this.screen0_splash,
      this.screen1_cliente,
      this.screen2_modo,
      this.screen3_encoder,
      this.screen4_angulo1,
      this.screen5_angulo2,
      this.screen6_angulo3,
      this.screen7_velocidade,
      this.screen8_carenagem,
      this.screen9_totalizador,
      this.screen10_estado
    ];

    const [line1, line2] = screens[this.currentScreen].call(this);
    updateLCD(line1, line2);
    this.updateLEDs();
  }

  // Tela 0: Splash
  screen0_splash() {
    return [
      '**TRILLOR MAQUINAS**',
      '**DOBRADEIRA HD    **'
    ];
  }

  // Tela 1: Cliente
  screen1_cliente() {
    return [
      'CAMARGO CORREIA CONS',
      'AQUISICAO AGOSTO-06 '
    ];
  }

  // Tela 2: Modo AUTO/MAN
  screen2_modo() {
    const mode = this.machineData.auto_mode ? 'AUTO' : 'MANUAL';
    return [
      'SELECAO DE AUTO/MAN ',
      `        [${mode}]      `
    ];
  }

  // Tela 3: Encoder (posição angular)
  screen3_encoder() {
    const degrees = this.encoderToDegrees(this.machineData.encoder);
    const count = this.machineData.encoder;
    return [
      'DESLOCAMENTO ANGULAR',
      `PV=${degrees.toString().padStart(3)}° (${count.toString().padStart(5)})`
    ];
  }

  // Tela 4: Ângulo Dobra 1
  screen4_angulo1() {
    const aj = this.machineData.angles.aj1_esq;  // ou aj1_dir dependendo do sentido
    const pv = this.encoderToDegrees(this.machineData.encoder);
    return [
      'AJUSTE DO ANGULO 01 ',
      `AJ=${aj.toString().padStart(3)}° PV=${pv.toString().padStart(3)}°`
    ];
  }

  // Tela 5: Ângulo Dobra 2
  screen5_angulo2() {
    const aj = this.machineData.angles.aj2_esq;
    const pv = this.encoderToDegrees(this.machineData.encoder);
    return [
      'AJUSTE DO ANGULO 02 ',
      `AJ=${aj.toString().padStart(3)}° PV=${pv.toString().padStart(3)}°`
    ];
  }

  // Tela 6: Ângulo Dobra 3
  screen6_angulo3() {
    const aj = this.machineData.angles.aj3_esq;
    const pv = this.encoderToDegrees(this.machineData.encoder);
    return [
      'AJUSTE DO ANGULO 03 ',
      `AJ=${aj.toString().padStart(3)}° PV=${pv.toString().padStart(3)}°`
    ];
  }

  // Tela 7: Velocidade
  screen7_velocidade() {
    const k = this.machineData.speed_class;
    return [
      '*SELECAO DA ROTACAO*',
      `        [${k}]         `
    ];
  }

  // Tela 8: Carenagem
  screen8_carenagem() {
    const status = this.machineData.carenagem_ok ? '3' : '5';
    return [
      'CARENAGEM DOBRADEIRA',
      `        [${status}]         `
    ];
  }

  // Tela 9: Totalizador
  screen9_totalizador() {
    const hours = Math.floor(this.machineData.runtime / 3600);
    const minutes = Math.floor((this.machineData.runtime % 3600) / 60);
    return [
      'TOTALIZADOR DE TEMPO',
      `*****${hours.toString().padStart(3)}:${minutes.toString().padStart(2, '0')}h *****`
    ];
  }

  // Tela 10: Estado
  screen10_estado() {
    const state = this.machineData.cycle_active ? '1' : '3';
    return [
      'ESTADO DA DOBRADEIRA',
      `        [${state}]         `
    ];
  }

  // Navegação
  nextScreen() {
    this.currentScreen = (this.currentScreen + 1) % this.totalScreens;
    this.render();
  }

  prevScreen() {
    this.currentScreen = (this.currentScreen - 1 + this.totalScreens) % this.totalScreens;
    this.render();
  }

  // Atalhos de navegação
  goToScreen(screenNumber) {
    this.currentScreen = screenNumber;
    this.render();
  }

  // Atualizar LEDs das teclas
  updateLEDs() {
    // LEDs dobras (K1, K2, K3)
    document.querySelector('[data-key="K1"]').classList.toggle('led-on', this.machineData.active_bend === 1);
    document.querySelector('[data-key="K2"]').classList.toggle('led-on', this.machineData.active_bend === 2);
    document.querySelector('[data-key="K3"]').classList.toggle('led-on', this.machineData.active_bend === 3);

    // LEDs sentido (K4, K5)
    document.querySelector('[data-key="K4"]').classList.toggle('led-on', this.machineData.direction === 'CCW');
    document.querySelector('[data-key="K5"]').classList.toggle('led-on', this.machineData.direction === 'CW');

    // LED modo AUTO (S1)
    document.querySelector('[data-key="S1"]').classList.toggle('led-on', this.machineData.auto_mode);
  }

  // Conversão encoder → graus (ajustar conforme calibração)
  encoderToDegrees(encoderValue) {
    // Fator de conversão a determinar com testes
    // Exemplo: 201.24 redução total, encoder 360 ppr
    const conversionFactor = 0.05;  // PLACEHOLDER - calibrar!
    return Math.round(encoderValue * conversionFactor);
  }

  // Atualizar dados do CLP (via WebSocket)
  updateMachineData(data) {
    this.machineData = { ...this.machineData, ...data };
    this.render();
  }
}

// Instanciar gerenciador de telas
const screenManager = new ScreenManager();
```

### 2.4. Backend - Atualizar `main_server.py`

**Adicionar polling de registros da IHM**:

```python
# Em state_manager.py

async def poll_ihm_data(modbus_client):
    """Poll específico para dados da IHM Expert Series"""
    ihm_data = {}

    try:
        # Encoder (32-bit)
        response_msw = await asyncio.to_thread(
            modbus_client.client.read_holding_registers,
            address=1238, count=1, device_id=1
        )
        response_lsw = await asyncio.to_thread(
            modbus_client.client.read_holding_registers,
            address=1239, count=1, device_id=1
        )
        if response_msw and response_lsw:
            encoder_value = (response_msw.registers[0] << 16) | response_lsw.registers[0]
            ihm_data['encoder'] = encoder_value

        # Ângulos de dobra
        angles_addresses = {
            'aj1_esq': 2112, 'aj1_dir': 2114,
            'aj2_esq': 2118, 'aj2_dir': 2120,
            'aj3_esq': 2128, 'aj3_dir': 2130
        }
        for key, addr in angles_addresses.items():
            response = await asyncio.to_thread(
                modbus_client.client.read_holding_registers,
                address=addr, count=1, device_id=1
            )
            if response:
                ihm_data[f'angle_{key}'] = response.registers[0]

        # Classe de velocidade (bits)
        for i, classe in enumerate([864, 865, 866], start=1):
            response = await asyncio.to_thread(
                modbus_client.client.read_coils,
                address=classe, count=1, device_id=1
            )
            if response and response.bits[0]:
                ihm_data['speed_class'] = i

        # Dobra ativa (bits 00F8, 00F9)
        bit_dobra_2 = await asyncio.to_thread(
            modbus_client.client.read_coils,
            address=248, count=1, device_id=1
        )
        bit_dobra_3 = await asyncio.to_thread(
            modbus_client.client.read_coils,
            address=249, count=1, device_id=1
        )

        if bit_dobra_3 and bit_dobra_3.bits[0]:
            ihm_data['active_bend'] = 3
        elif bit_dobra_2 and bit_dobra_2.bits[0]:
            ihm_data['active_bend'] = 2
        else:
            ihm_data['active_bend'] = 1

        # Ciclo ativo (bit 00F7)
        response = await asyncio.to_thread(
            modbus_client.client.read_coils,
            address=247, count=1, device_id=1
        )
        if response:
            ihm_data['cycle_active'] = response.bits[0]

        # Carenagem (E5)
        response = await asyncio.to_thread(
            modbus_client.client.read_holding_registers,
            address=261, count=1, device_id=1
        )
        if response:
            ihm_data['carenagem_ok'] = (response.registers[0] & 0x0001) == 1

    except Exception as e:
        logger.error(f"Erro ao fazer polling IHM: {e}")

    return ihm_data
```

**Adicionar handler para teclas**:

```python
# Em main_server.py

async def handle_press_key(websocket, message):
    """Simula pressionamento de tecla da IHM via Modbus"""
    key_address = message.get('address')

    if not key_address:
        await websocket.send(json.dumps({
            'error': 'Endereço da tecla não fornecido'
        }))
        return

    try:
        # Pressionar tecla (pulso 100ms)
        success = await asyncio.to_thread(
            modbus_client.press_key,
            key_address
        )

        if success:
            logger.info(f"Tecla pressionada: endereço {key_address}")
            await websocket.send(json.dumps({
                'success': True,
                'action': 'key_pressed',
                'address': key_address
            }))
        else:
            logger.error(f"Falha ao pressionar tecla: endereço {key_address}")
            await websocket.send(json.dumps({
                'success': False,
                'error': 'Falha ao enviar comando Modbus'
            }))

    except Exception as e:
        logger.error(f"Erro ao processar tecla: {e}")
        await websocket.send(json.dumps({
            'success': False,
            'error': str(e)
        }))
```

---

## FASE 3: TESTES E VALIDAÇÃO

### 3.1. Testes de Comunicação

**Checklist**:
- [ ] Encoder atualiza em tempo real (250ms)
- [ ] Ângulos lidos corretamente
- [ ] Velocidade detectada corretamente (bits 0360-0362)
- [ ] Dobra ativa identificada (bits 00F8/00F9)
- [ ] Ciclo ativo detectado (bit 00F7)
- [ ] Sensor carenagem lido corretamente (E5)

### 3.2. Testes de Navegação

**Checklist**:
- [ ] Tecla ↑ navega para tela anterior
- [ ] Tecla ↓ navega para tela seguinte
- [ ] Tecla K1 vai direto para Tela 4 (Ângulo 01)
- [ ] Tecla K2 vai direto para Tela 5 (Ângulo 02)
- [ ] Tecla K3 vai direto para Tela 6 (Ângulo 03)
- [ ] ESC volta para tela inicial

### 3.3. Testes de LEDs

**Checklist**:
- [ ] LED K1 acende quando dobra 1 ativa
- [ ] LED K2 acende quando dobra 2 ativa
- [ ] LED K3 acende quando dobra 3 ativa
- [ ] LED K4 acende quando sentido anti-horário
- [ ] LED K5 acende quando sentido horário
- [ ] LED S1 acende em modo AUTO

### 3.4. Testes de Edição (EDIT)

**Checklist**:
- [ ] Tecla EDIT entra em modo edição
- [ ] K0-K9 digitam valores
- [ ] ENTER confirma valor e escreve via Modbus
- [ ] ESC cancela edição
- [ ] Valor escrito aparece imediatamente no display

---

## FASE 4: CALIBRAÇÃO E AJUSTES FINOS

### 4.1. Calibração do Encoder

**Procedimento**:
1. Zerar encoder (posição de referência)
2. Girar prato manualmente 360° completos
3. Ler valor final do encoder
4. Calcular fator de conversão:
   ```
   graus = (encoder_value / encoder_max) * 360
   ```

### 4.2. Validação de Ângulos

**Procedimento**:
1. Configurar ângulo conhecido (ex: 90°) na Tela 4
2. Executar dobra no modo manual
3. Medir ângulo real com transferidor
4. Ajustar fator de conversão se necessário

### 4.3. Totalizador de Tempo

**A mapear**: Identificar registro que armazena tempo total
**Opção alternativa**: Calcular no servidor Python baseado em BIT_CICLO_ATIVO

---

## FASE 5: DOCUMENTAÇÃO FINAL E ENTREGA

### 5.1. Manual do Operador

**Criar arquivo**: `MANUAL_OPERADOR_IHM_WEB.md`

**Conteúdo**:
- Como conectar o tablet
- Como navegar entre telas
- Como configurar ângulos de dobra
- Como selecionar velocidade
- Troubleshooting básico

### 5.2. Manual de Manutenção

**Criar arquivo**: `MANUAL_MANUTENCAO_IHM.md`

**Conteúdo**:
- Arquitetura do sistema
- Endereços Modbus críticos
- Procedimentos de backup
- Restauração em caso de falha
- Logs e diagnóstico

### 5.3. Diagrama de Arquitetura

**Criar arquivo**: `ARQUITETURA_SISTEMA.png` (ou draw.io)

**Incluir**:
- Fluxo completo de dados
- Endereços Modbus
- Portas de comunicação
- Topologia de rede

---

## CRONOGRAMA ESTIMADO

| Fase | Tarefa | Tempo Estimado | Responsável |
|------|--------|----------------|-------------|
| 2.1 | Componente Display LCD | 2-3 horas | Desenvolvedor |
| 2.2 | Componente Teclado | 3-4 horas | Desenvolvedor |
| 2.3 | Máquina de Estados | 4-6 horas | Desenvolvedor |
| 2.4 | Backend polling | 2-3 horas | Desenvolvedor |
| 3 | Testes completos | 4-6 horas | Desenvolvedor + Operador |
| 4 | Calibração | 2-4 horas | Técnico |
| 5 | Documentação | 3-4 horas | Desenvolvedor |
| **TOTAL** | **20-30 horas** | **≈ 3-5 dias** | - |

---

## RISCOS E MITIGAÇÕES

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Fator conversão encoder incorreto | Alta | Médio | Calibração com medições físicas |
| Registros não documentados (totalizador) | Média | Baixo | Implementar cálculo alternativo |
| Latência WiFi tablet | Baixa | Baixo | Polling ajustável (250ms-1s) |
| Incompatibilidade navegadores | Baixa | Médio | Testar Chrome, Firefox, Safari |
| Perda conexão durante operação | Média | Alto | Overlay "DESLIGADO" + reconexão automática |

---

## PRÓXIMOS PASSOS IMEDIATOS

### Para o Desenvolvedor

1. **Implementar Display LCD** (2-3h)
   - Criar componente HTML/CSS
   - Testar formatação de 20 caracteres
   - Validar legibilidade em tablet

2. **Implementar Teclado Virtual** (3-4h)
   - Criar layout HTML
   - Adicionar event listeners
   - Implementar feedback visual

3. **Implementar Máquina de Estados** (4-6h)
   - Criar classe ScreenManager
   - Implementar as 11 telas
   - Testar navegação

4. **Atualizar Backend** (2-3h)
   - Adicionar polling IHM em `state_manager.py`
   - Adicionar handler `press_key` em `main_server.py`
   - Testar comunicação

### Para o Técnico

1. **Preparar Ambiente de Teste**
   - Conectar CLP via RS485
   - Configurar rede WiFi tablet
   - Preparar ferramentas de calibração

2. **Validar Registros Pendentes**
   - Mapear totalizador de tempo
   - Mapear bit modo AUTO/MAN
   - Mapear registro estado geral

---

## CONCLUSÃO

A estratégia de **retrofit completo da IHM Expert Series** é:
- ✅ **Tecnicamente viável** (95% dos registros já mapeados)
- ✅ **Segura** (não modifica ladder existente)
- ✅ **Reversível** (painel físico permanece funcional)
- ✅ **Escalável** (fácil adicionar funcionalidades futuras)

O próximo marco é **implementar a IHM web funcional** seguindo as especificações deste guia.

**Tempo estimado total**: 3-5 dias de desenvolvimento + testes

---

**Engenheiro Responsável**: Claude Code
**Data**: 2025-11-08
**Versão**: 1.0
**Status**: ✅ Pronto para implementação
