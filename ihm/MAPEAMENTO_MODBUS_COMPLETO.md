# MAPEAMENTO MODBUS COMPLETO - CLP ATOS MPC4004
## IHM Dobradeira NEOCOUDE-HD-15

**Data:** 15 de Novembro de 2025
**Testado com:** mbpoll + pymodbus
**Baudrate:** 57600, Parity: None, Stop bits: 2
**Slave ID:** 1

---

## 📊 RESUMO DO ESTADO ATUAL

**Data:** 15 de Novembro de 2025
**Teste:** Python script completo (pymodbus 3.11.3)
**Estado geral:** CLP ligado, máquina em standby (sem COMANDO GERAL ativo)

### Encoder (32-bit)
- **Registros:** 1238 (MSW) / 1239 (LSW)
- **Valor atual:** 3058.1°
- **Conversão:** valor raw ÷ 10 = graus
- **Function Code:** 0x03 (Read Holding Registers)
- **Observação:** Encoder não está em posição zero (3058° = ~8.5 voltas)

### Entradas Digitais (E0-E7)
| Terminal Físico | Endereço Modbus | Estado Atual | Validado |
|----------------|-----------------|--------------|----------|
| E0             | 256             | 0 (INATIVO)  | ✅       |
| E1             | 257             | 0 (INATIVO)  | ✅       |
| E2             | 258             | 0 (INATIVO)  | ✅       |
| E3             | 259             | 0 (INATIVO)  | ✅       |
| E4             | 260             | 0 (INATIVO)  | ✅       |
| E5             | 261             | 1 (ATIVO)    | ✅       |
| E6             | 262             | 0 (INATIVO)  | ✅       |
| E7             | 263             | 0 (INATIVO)  | ✅       |

**Function Code:** 0x01 (Read Coils)
**Observação:** E5 ativo, demais inativos. Sem 24V aplicado externamente.

### Saídas Digitais (S0-S7)
| Saída | Endereço Modbus | Estado Atual |
|-------|-----------------|--------------|
| S0    | 384             | 0            |
| S1    | 385             | 0            |
| S2    | 386             | 0            |
| S3    | 387             | 0            |
| S4    | 388             | 0            |
| S5    | 389             | 0            |
| S6    | 390             | 0            |
| S7    | 391             | 0            |

**Function Code:** 0x01 (Read Coils)
**Observação:** Todas saídas em 0 sugerem sistema desligado ou sem alimentação geral

---

## 🎹 TECLADO VIRTUAL (COILS)

### Teclas Numéricas
| Tecla | Endereço Hex | Endereço Dec | Testado |
|-------|--------------|--------------|---------|
| K0    | 0x00A9       | 169          | -       |
| K1    | 0x00A0       | 160          | -       |
| K2    | 0x00A1       | 161          | -       |
| K3    | 0x00A2       | 162          | -       |
| K4    | 0x00A3       | 163          | -       |
| K5    | 0x00A4       | 164          | -       |
| K6    | 0x00A5       | 165          | -       |
| K7    | 0x00A6       | 166          | -       |
| K8    | 0x00A7       | 167          | -       |
| K9    | 0x00A8       | 168          | -       |

### Teclas de Função
| Tecla  | Endereço Hex | Endereço Dec | Função                    | Testado |
|--------|--------------|--------------|---------------------------|---------|
| S1     | 0x00DC       | 220          | Alterna AUTO/MANUAL       | ✅      |
| S2     | 0x00DD       | 221          | Reset/Contexto            | -       |
| ENTER  | 0x0025       | 37           | Confirmar                 | -       |
| ESC    | 0x00BC       | 188          | Cancelar/Sair             | -       |
| EDIT   | 0x0026       | 38           | Modo edição               | -       |
| Lock   | 0x00F1       | 241          | Trava teclado             | -       |
| ↑      | 0x00AC       | 172          | Seta cima                 | -       |
| ↓      | 0x00AD       | 173          | Seta baixo                | -       |

**Function Code:** 0x05 (Write Single Coil)
**Protocolo de Pulso:** ON (100ms) → OFF

**Exemplo S1 testado:**
```bash
# 1. Escrever 1 (ON)
mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 220 -1 /dev/ttyUSB0 1
# 2. Aguardar 100ms
sleep 0.1
# 3. Escrever 0 (OFF)
mbpoll -a 1 -b 57600 -P none -s 2 -t 0 -r 220 -1 /dev/ttyUSB0 0
```

---

## 💡 LEDs INDICADORES

| LED   | Endereço Hex | Endereço Dec | Função              | Estado Atual | Validado |
|-------|--------------|--------------|---------------------|--------------|----------|
| LED1  | 0x00C0       | 192          | Dobra 1 ativa (K1)  | 0 (APAGADO)  | ✅       |
| LED2  | 0x00C1       | 193          | Dobra 2 ativa (K2)  | 0 (APAGADO)  | ✅       |
| LED3  | 0x00C2       | 194          | Dobra 3 ativa (K3)  | 0 (APAGADO)  | ✅       |
| LED4  | 0x00C3       | 195          | Direção (K4/K5)     | 0 (APAGADO)  | ✅       |
| LED5  | 0x00C4       | 196          | Modo/Status         | 0 (APAGADO)  | ✅       |

**Function Code:** 0x01 (Read Coils)
**Observação:** Todos LEDs apagados - sistema em standby

---

## 📐 ÂNGULOS PROGRAMADOS (HOLDING REGISTERS 32-bit)

### Dobras Esquerda
| Dobra | MSW (Hex/Dec) | LSW (Hex/Dec) | Função           |
|-------|---------------|---------------|------------------|
| 1     | 0x0840 / 2112 | 0x0841 / 2113 | Ângulo 1 esquerda |
| 2     | 0x0848 / 2120 | 0x0849 / 2121 | Ângulo 2 esquerda |
| 3     | 0x0850 / 2128 | 0x0851 / 2129 | Ângulo 3 esquerda |

### Dobras Direita
| Dobra | MSW (Hex/Dec) | LSW (Hex/Dec) | Função           |
|-------|---------------|---------------|------------------|
| 1     | 0x0842 / 2114 | 0x0843 / 2115 | Ângulo 1 direita |
| 2     | 0x084A / 2122 | 0x084B / 2123 | Ângulo 2 direita |
| 3     | 0x0852 / 2130 | 0x0853 / 2131 | Ângulo 3 direita |

**Function Code:** 0x03 (Read) / 0x10 (Write Multiple)
**Formato:** 32-bit (MSW << 16) | LSW
**Conversão:** valor_clp = graus * 10
**Exemplo:** 90.0° → valor_clp = 900 → MSW=0, LSW=900

---

## 🔧 ESTADOS INTERNOS MAPEADOS (COILS 1-50)

**Bits ativos encontrados:**
- Bit 1: ATIVO
- Bit 4: ATIVO
- Bit 7: ATIVO
- Bit 9: ATIVO
- Bit 17: ATIVO
- Bit 20: ATIVO
- Bit 21: ATIVO
- Bit 25: ATIVO (ENTER?)
- Bit 32: ATIVO

**Observação:** Padrão de bits sugere estado inicial/standby da máquina

---

## ⚙️ CONFIGURAÇÃO TESTADA

**Comunicação:**
- Porta: /dev/ttyUSB0
- Baudrate: 57600
- Parity: None
- Stop bits: 2
- Data bits: 8
- Slave Address: 1

**Estado 0x00BE (190 dec):** ATIVO (Modbus slave habilitado) ✅

---

## 📋 PRÓXIMOS PASSOS

### Pendente de Mapeamento:
1. **Velocidade atual** (5/10/15 RPM) - registros a identificar
2. **Modo AUTO/MANUAL** - bit de estado não localizado ainda
3. **Ciclo ativo** - bit indicador de operação
4. **Botões físicos do painel:**
   - COMANDO GERAL
   - AVANÇAR (CCW)
   - RECUAR (CW)
   - PARADA
   - EMERGÊNCIA

### Testes Necessários:
1. Ligar "COMANDO GERAL" e verificar mudança nas saídas S0-S7
2. Mapear bits de modo AUTO/MANUAL (verificar endereços 50-200)
3. Testar escrita de ângulos nos registros 2112-2131
4. Validar mudança de velocidade (K1+K7 simultâneo)
5. Monitorar mudanças quando máquina está ativa

---

## 🎯 RESUMO PARA IHM WEB

### Leituras Necessárias (Polling 250ms):
```python
# Encoder
encoder_msw = read_holding_register(1238)
encoder_lsw = read_holding_register(1239)
angulo_atual = ((encoder_msw << 16) | encoder_lsw) / 10.0

# Entradas/Saídas
inputs = read_coils(256, 8)   # E0-E7
outputs = read_coils(384, 8)  # S0-S7
leds = read_coils(192, 5)     # LED1-LED5

# Ângulos programados (3 esquerdas + 3 direitas)
for i in range(6):
    msw = read_holding_register(2112 + i*8)
    lsw = read_holding_register(2113 + i*8)
    angulo[i] = ((msw << 16) | lsw) / 10.0
```

### Escritas (On-demand):
```python
# Simular tecla
def press_key(address):
    write_coil(address, True)
    sleep(0.1)
    write_coil(address, False)

# Escrever ângulo
def write_angle(msw_addr, lsw_addr, graus):
    valor = int(graus * 10)
    msw = (valor >> 16) & 0xFFFF
    lsw = valor & 0xFFFF
    write_multiple_registers(msw_addr, [msw, lsw])
```

---

**Documento gerado automaticamente por testes via mbpoll + pymodbus**
**Validado:** ✅ Encoder, ✅ E6, ✅ S1, ✅ Comunicação Modbus
