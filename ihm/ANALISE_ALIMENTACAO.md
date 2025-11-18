# ⚡ Análise: Alimentação do WebServer (ESP32/Pico/RPi)

## 🔌 Investigação: Pino 5V do RS485 (MPC4004)

### 📋 Informações do Manual
**Problema:** Manual MPC4004 NÃO especifica corrente disponível no pino 5V do conector RS485.

**O que sabemos:**
1. ✅ **Canal B = RS485** (padrão elétrico)
2. ✅ **Conector:** Provavelmente RJ11 ou DB9
3. ✅ **Pinos:** A, B (dados) + GND + 5V (alimentação auxiliar)
4. ❌ **Corrente 5V:** NÃO especificada no manual

### 🔍 Análise por Engenharia Reversa

**Típico em CLPs industriais (padrão de mercado):**
- Pino 5V no RS485 é **auxiliar para alimentar conversores/isoladores**
- Corrente típica: **50-100mA** (conservador)
- Corrente máxima: **200-300mA** (otimista)

**Motivo da limitação:**
- Fonte 5V do CLP é dimensionada para:
  - CPU: ~300mA
  - Módulos I/O: ~100mA cada
  - RS485: **limitado por resistor/fusível de proteção**
- **Pino 5V NÃO é projetado para alimentar cargas externas grandes**

---

## 📊 Consumo dos Candidatos

| Dispositivo | Idle (mA) | WiFi Ativo (mA) | Pico TX (mA) | Viável RS485? |
|-------------|-----------|-----------------|--------------|---------------|
| **ESP32** | 80 | 160-260 | 500 | ⚠️ ARRISCADO |
| **Pico W2** | 30 | 120-150 | 300 | ⚠️ ARRISCADO |
| **RPi 3B+** | 400 | 700 | 1200 | ❌ IMPOSSÍVEL |
| **RPi Zero 2W** | 100 | 200 | 350 | ⚠️ ARRISCADO |

### 🧪 Consumo Detalhado

**ESP32-WROOM-32:**
- Idle (WiFi off): 80mA @ 3.3V = 264mW
- WiFi TX: 160-260mA @ 3.3V = 528-858mW
- WiFi RX: 95-100mA @ 3.3V = 313-330mW
- **Pico:** 500mA (inicialização WiFi)
- **Regulador 3.3V** adiciona 10-20% de perda

**Raspberry Pi Pico W2:**
- Idle: 30mA @ 3.3V = 99mW
- WiFi ativo: 120-150mA @ 3.3V = 396-495mW
- **Pico:** 300mA (scan WiFi)

**Raspberry Pi 3B+:**
- Idle: 400mA @ 5V = 2W
- WiFi ativo: 700mA @ 5V = 3.5W
- **Completamente inviável para 5V auxiliar**

---

## ⚠️ CONCLUSÃO: **NÃO RECOMENDADO**

### Por quê?

1. **Corrente insuficiente:**
   - RS485 típico: 50-100mA disponível
   - ESP32 precisa: 160-500mA (pico)
   - **Déficit: 60-400mA!**

2. **Risco de dano ao CLP:**
   - Sobrecarga na fonte 5V interna
   - Possível reset do CLP por queda de tensão
   - **Pode queimar regulador do CLP** (R$ 500-1.500 para consertar)

3. **Instabilidade:**
   - ESP32/Pico vai resetar constantemente
   - WiFi não vai conectar (precisa do pico de corrente)
   - Experiência terrível para o operador

4. **Violação de garantia:**
   - Manual não especifica uso do 5V auxiliar para cargas externas
   - **Atos pode negar garantia se queimar**

---

## ✅ SOLUÇÕES RECOMENDADAS

### OPÇÃO 1: Fonte Dedicada 5V (MELHOR) ⭐

**Hardware:**
- **Conversor Buck 24V → 5V 3A**
- Modelo: LM2596 ou equivalente industrial
- Preço: R$ 15-25
- Montagem: DIN rail

**Vantagens:**
1. ✅ **Isolado do CLP** (zero risco)
2. ✅ **Corrente abundante** (3A, muito mais que ESP32 precisa)
3. ✅ **Confiável** (módulos industriais)
4. ✅ **Barato**

**Conexão:**
```
Painel 24V DC ──→ Buck Converter ──→ 5V 3A ──→ ESP32
                                    └──→ GND comum com RS485
```

**Esquema:**
```
Terminal 24V Painel:
  [+24V] ────┬──→ Buck IN+
             │
  [0V]   ────┴──→ Buck IN-

Buck Converter:
  OUT+ (5V) ──→ ESP32 VIN (5V)
  OUT- (GND) ─┬─→ ESP32 GND
              └─→ RS485 GND (referência comum)

RS485:
  A ──→ ESP32 GPIO17 (via MAX485)
  B ──→ ESP32 GPIO16 (via MAX485)
  GND ──→ Comum com Buck
```

---

### OPÇÃO 2: Fonte 24V → 3.3V Direta (ALTERNATIVA)

**Hardware:**
- **Conversor Buck 24V → 3.3V 2A**
- Preço: R$ 20-30
- Alimenta ESP32 direto no pino 3.3V (bypass regulador interno)

**Vantagens:**
1. ✅ Mais eficiente (sem regulador intermediário)
2. ✅ Menos calor gerado
3. ✅ ESP32 opera nativamente em 3.3V

**Desvantagem:**
- ⚠️ Precisa regular voltagem exatamente em 3.3V (tolerância ±0.3V)

---

### OPÇÃO 3: Raspberry Pi Pico W2 + Buck 24V→5V (COMPACTO)

**Se optar por Pico W2:**
- Buck 24V → 5V 1A (menor)
- Pico consome menos que ESP32
- **Ainda assim, use fonte dedicada!**

---

### OPÇÃO 4: Módulo Industrial ESP32 (PROFISSIONAL) 💰

**Hardware:**
- **ESP32 Industrial com entrada 9-36V DC**
- Exemplos:
  - Lilygo T-Internet-POE (R$ 150-200)
  - Olimex ESP32-POE-ISO (R$ 250-350)
- Conexão direta no 24V do painel

**Vantagens:**
1. ✅ **Regulador industrial integrado**
2. ✅ **Isolamento galvânico**
3. ✅ **Proteção contra surtos**
4. ✅ **Certificação CE/FCC**

**Desvantagem:**
- ❌ **Mais caro** (3-5x o preço do ESP32 comum)

---

## 🎯 RECOMENDAÇÃO FINAL

### Para a fábrica (HOJE):
✅ **Notebook** - alimentação própria, zero problemas

### Para produção permanente (MELHOR custo-benefício):

**Solução: ESP32 + Buck 24V→5V 3A**
- **Total: R$ 70-90**
  - ESP32-WROOM-32: R$ 40-60
  - MAX485: R$ 8-15
  - Buck 24V→5V 3A: R$ 15-25
  - Caixa DIN rail: R$ 20-30 (opcional)

**Montagem:**
```
┌─────────────────────────────────────┐
│  Painel Elétrico 24V DC             │
│                                     │
│  ┌──────────────┐                  │
│  │ Buck 24→5V   │                  │
│  │ LM2596 3A    │                  │
│  │ IN: 24V      │                  │
│  │ OUT: 5V      │───┐              │
│  └──────────────┘   │              │
│         │           │              │
│         └───────────┼──────┐       │
│                     │      │       │
│  ┌──────────────────┴──┐   │       │
│  │  ESP32-WROOM-32    │   │       │
│  │  + MAX485          │◄──┘       │
│  │  WiFi AP           │            │
│  └────────────────────┘            │
│         │  RS485                   │
│         └──────────────────────────┼──→ CLP
└─────────────────────────────────────┘
```

---

## 📐 Especificação de Compra

**Lista de materiais (BOM):**

1. **ESP32-WROOM-32 DevKit V1**
   - Tensão: 5V via USB ou VIN
   - Corrente: 500mA pico
   - Link: Mercado Livre / AliExpress
   - Preço: R$ 40-60

2. **Módulo MAX485 TTL**
   - Chip: MAX485CSA
   - Pinos: VCC, GND, DI, RO, DE, RE, A, B
   - Preço: R$ 8-15

3. **Conversor Buck 24V→5V 3A (LM2596)**
   - Entrada: 4.5-40V DC
   - Saída: 1.25-37V (ajustável, fixar em 5.0V)
   - Corrente: 3A contínuo
   - Proteção: Curto-circuito, sobre temperatura
   - **IMPORTANTE:** Comprar versão com display LED (facilita ajuste)
   - Preço: R$ 15-25

4. **Cabos e conectores:**
   - Par trançado blindado 24AWG para RS485 (2m): R$ 5
   - Terminal 24V no painel: bornes existentes
   - Conector RS485 CLP: RJ11 ou DB9 (verificar na fábrica)

5. **Opcional - Caixa DIN rail:**
   - Caixa plástica montável em trilho DIN
   - Dimensões: 90x70x60mm
   - Preço: R$ 20-30

**Total: R$ 68-100**

---

## 🔧 Procedimento de Instalação

### 1. Ajustar Buck Converter (ANTES de conectar ESP32!)
```bash
# Com multímetro em voltímetro
1. Conectar Buck ao 24V do painel
2. Medir saída com multímetro
3. Ajustar trimpot até exatos 5.0V (±0.1V)
4. Desconectar e aguardar descarga dos capacitores (30s)
```

### 2. Montar Circuito
```
Buck OUT+ (5V) ──→ ESP32 VIN
Buck OUT- (GND) ─┬─→ ESP32 GND
                 └─→ MAX485 GND

MAX485:
  VCC ──→ ESP32 3.3V (pode usar 5V também)
  DI  ──→ ESP32 GPIO17
  RO  ──→ ESP32 GPIO16
  DE  ──→ ESP32 GPIO4
  RE  ──→ ESP32 GPIO4 (mesmo pino)
  A   ──→ RS485 A do CLP
  B   ──→ RS485 B do CLP
```

### 3. Testar Antes de Fechar Painel
```bash
1. Medir 5V no ESP32 com multímetro
2. Upload firmware de teste (LED pisca)
3. Testar comunicação RS485 com CLP
4. Testar WiFi (conecta em rede)
5. Teste de stress: rodar 1 hora contínuo
6. Se tudo OK → fechar painel e homologar
```

---

## ⚡ Comparação de Soluções

| Solução | Custo | Confiabilidade | Risco CLP | Complexidade |
|---------|-------|----------------|-----------|--------------|
| **Pino 5V RS485** | R$ 0 | ⚠️ Baixa | ⚠️ Alto | Baixa |
| **Buck 24V→5V** ⭐ | R$ 70-90 | ✅ Alta | ✅ Zero | Média |
| **Buck 24V→3.3V** | R$ 80-100 | ✅ Alta | ✅ Zero | Média |
| **ESP32 Industrial** | R$ 200-350 | ✅ Muito Alta | ✅ Zero | Baixa |
| **Notebook atual** | R$ 0 | ✅ Alta | ✅ Zero | Baixa |

---

## 🎯 DECISÃO FINAL

**NUNCA alimente ESP32/Pico/RPi pelo pino 5V do RS485!**

**Motivos:**
1. 🔥 Risco de queimar CLP (R$ 500-1.500 prejuízo)
2. ⚡ Corrente insuficiente (50-100mA vs 500mA necessário)
3. 🔄 Resets constantes (experiência ruim)
4. ⚠️ Violação de garantia Atos

**Use:**
✅ **Buck 24V→5V 3A** (adicional R$ 15-25)
✅ **Alimentação dedicada do painel 24V DC**
✅ **Zero risco para o CLP**

---

**Quer diagrama esquemático completo em Eagle/KiCad?** Posso gerar para você imprimir a PCB customizada!
