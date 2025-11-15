# Mapeamento Completo da IHM Expert Series Original

## Data Análise
2025-11-08

## Fonte
Arquivo `ladder_extract/Screen.dbf` - Configuração original da IHM Expert Series 4004.95C

## Especificações da IHM Física

**Modelo**: Atos Expert Series 4004.95C
**Display**: LCD 2 linhas x 20 caracteres (40 caracteres total)
**Teclado**:
- Numérico: K0-K9 (10 teclas)
- Funções: S1, S2 (2 teclas)
- Navegação: ↑ (Up), ↓ (Down) (2 teclas)
- Sistema: ESC, ENTER, EDIT, Lock (4 teclas)
**Total**: 18 teclas

## Mapeamento Modbus das Teclas

| Tecla | Função | Endereço Hex | Endereço Decimal | Observações |
|-------|--------|--------------|------------------|-------------|
| K0 | Número 0 | 00A9 | 169 | Teclado numérico |
| K1 | Número 1 | 00A0 | 160 | Teclado numérico + Seleção dobra 1 |
| K2 | Número 2 | 00A1 | 161 | Teclado numérico + Seleção dobra 2 |
| K3 | Número 3 | 00A2 | 162 | Teclado numérico + Seleção dobra 3 |
| K4 | Número 4 | 00A3 | 163 | Teclado numérico + Sentido |
| K5 | Número 5 | 00A4 | 164 | Teclado numérico + Sentido |
| K6 | Número 6 | 00A5 | 165 | Teclado numérico |
| K7 | Número 7 | 00A6 | 166 | Teclado numérico + Seleção velocidade |
| K8 | Número 8 | 00A7 | 167 | Teclado numérico |
| K9 | Número 9 | 00A8 | 168 | Teclado numérico |
| S1 | Função 1 | 00DC | 220 | Multi-função (contexto) |
| S2 | Função 2 | 00DD | 221 | Multi-função (contexto) |
| ↑ | Seta cima | 00AC | 172 | Navegação / Incremento |
| ↓ | Seta baixo | 00AD | 173 | Navegação / Decremento |
| ESC | Escape | 00BC | 188 | Cancelar / Voltar |
| ENTER | Enter | 0025 | 37 | Confirmar |
| EDIT | Editar | 0026 | 38 | Modo edição |
| Lock | Trava | 00F1 | 241 | Bloquear teclado |

## Telas Programadas (11 telas)

### Tela 0: Splash Screen / Apresentação
```
┌────────────────────┐
│**TRILLOR MAQUINAS**│
│**DOBRADEIRA HD    **│
└────────────────────┘
```
**Tipo**: Estática (sem navegação)
**Função**: Tela de boot/apresentação
**Campos**: Texto fixo
**Navegação**: Auto-avança para Tela 1

### Tela 1: Identificação do Cliente
```
┌────────────────────┐
│CAMARGO CORREIA CONS│
│AQUISICAO AGOSTO-06 │
└────────────────────┘
```
**Tipo**: Estática (sem navegação)
**Função**: Identificação do cliente/projeto
**Campos**: Texto fixo
**Navegação**: Auto-avança ou manual para próxima tela

### Tela 2: Seleção Modo Operação
```
┌────────────────────┐
│SELECAO DE AUTO/MAN │
│        [3]         │
└────────────────────┘
```
**Tipo**: Navegável
**Função**: Escolher modo AUTO ou MANUAL
**Campos**:
- Indicador de modo atual (estado interno)
**Teclas Ativas**:
- S1: Alterna AUTO/MANUAL
- ↑/↓: Navega telas
**Registros**:
- Lê estado do modo (bit de estado)

### Tela 3: Deslocamento Angular (Encoder)
```
┌────────────────────┐
│DESLOCAMENTO ANGULAR│
│PV=___° (___)       │
└────────────────────┘
```
**Tipo**: Navegável + Leitura
**Função**: Mostra posição angular atual (encoder)
**Campos**:
- PV = Valor Presente (Present Value) - ângulo atual em graus
- () = Valor interno do contador
**Registros Modbus**:
- 04D6/04D7 (1238/1239) - Contador encoder (32-bit)
**Cálculo**: Converter contagem para graus
**Atualização**: Tempo real (polling 250ms)

### Tela 4: Ajuste Ângulo 01 (Dobra 1)
```
┌────────────────────┐
│AJUSTE DO ANGULO 01 │
│AJ=___° PV=___°     │
└────────────────────┘
```
**Tipo**: Navegável + Editável
**Função**: Configurar ângulo da 1ª dobra
**Campos**:
- AJ = Ajuste (valor configurado pelo usuário)
- PV = Valor Presente (posição atual)
**Teclas Ativas**:
- EDIT: Entrar em modo edição
- K0-K9: Digitar valor
- ENTER: Confirmar
- ESC: Cancelar
**Registros Modbus**: A determinar (provável registr 0840-0842)
**Indicadores LED físicos**: K1 acende quando selecionado

### Tela 5: Ajuste Ângulo 02 (Dobra 2)
```
┌────────────────────┐
│AJUSTE DO ANGULO 02 │
│AJ=___° PV=___°     │
└────────────────────┘
```
**Função**: Configurar ângulo da 2ª dobra
**Indicadores LED físicos**: K2 acende quando selecionado

### Tela 6: Ajuste Ângulo 03 (Dobra 3)
```
┌────────────────────┐
│AJUSTE DO ANGULO 03 │
│AJ=___° PV=___°     │
└────────────────────┘
```
**Função**: Configurar ângulo da 3ª dobra
**Indicadores LED físicos**: K3 acende quando selecionado

### Tela 7: Seleção de Rotação (Velocidade)
```
┌────────────────────┐
│*SELECAO DA ROTACAO*│
│        [K]         │
└────────────────────┘
```
**Tipo**: Navegável + Configurável
**Função**: Selecionar velocidade do prato (5/10/15 RPM)
**Campos**:
- K = Classe de velocidade (1, 2 ou 3)
  - Classe 1 = 5 RPM
  - Classe 2 = 10 RPM
  - Classe 3 = 15 RPM
**Teclas Ativas**:
- K1 + K7 (simultâneo): Cicla entre classes
- Disponível apenas em modo MANUAL

### Tela 8: Status Carenagem
```
┌────────────────────┐
│CARENAGEM DOBRADEIRA│
│        [3]         │
└────────────────────┘
```
**Tipo**: Navegável + Leitura
**Função**: Indica estado da carenagem (sensor de proteção)
**Campos**:
- Indicador de sensor (3 ou 5)
**Registros**:
- Lê entrada digital (sensor carenagem - E5 provável 0x0105)

### Tela 9: Totalizador de Tempo
```
┌────────────────────┐
│TOTALIZADOR DE TEMPO│
│*****___:__h *****  │
└────────────────────┘
```
**Tipo**: Navegável + Leitura
**Função**: Contador de horas de operação
**Campos**:
- Horas:Minutos de operação total
**Registros Modbus**: A determinar (registro de totalizador)
**Função ladder**: Incrementa quando ciclo ativo

### Tela 10: Estado da Dobradeira
```
┌────────────────────┐
│ESTADO DA DOBRADEIRA│
│        [3]         │
└────────────────────┘
```
**Tipo**: Navegável + Leitura
**Função**: Status geral da máquina
**Campos**:
- Indicador de estado operacional
**Possíveis estados**:
- 0 = Parada
- 1 = Em operação
- 2 = Erro
- 3 = Standby/Pronto
**Registros**: Estado geral (bits de controle)

## Navegação Entre Telas

**Padrão de navegação**:
- Tecla ↑ (Up): Tela anterior (decrementa número da tela)
- Tecla ↓ (Down): Próxima tela (incrementa número da tela)
- ESC: Volta para tela inicial ou cancela edição
- Telas 0 e 1: Não navegáveis (splash screens)
- Telas 2-10: Navegação circular
- Em modo EDIT: ↑/↓ incrementa/decrementa valor

**Navegação direta** (atalhos):
- K1: Vai para Tela 4 (Ajuste Ângulo 01)
- K2: Vai para Tela 5 (Ajuste Ângulo 02)
- K3: Vai para Tela 6 (Ajuste Ângulo 03)
- S1: Contexto dependente da tela
- S2: Contexto dependente da tela

## Variáveis Importantes (A serem mapeadas)

### Registros já conhecidos:
- **04D6/04D7** (1238/1239): Encoder (32-bit) - Posição angular
- **0100-0107** (256-263): Entradas digitais E0-E7
- **0180-0187** (384-391): Saídas digitais S0-S7

### Registros a mapear (análise do ladder):
- **Ângulo AJ 01/02/03**: Setpoints dos ângulos (provável 0840-0852)
- **Modo AUTO/MAN**: Bit de estado (provável 0x02FF ou similar)
- **Classe velocidade**: Registro (provável relacionado a 0x0360-0x0373)
- **Totalizador tempo**: Registro de contador (a determinar)
- **Estado dobra atual**: Qual dobra está ativa (K1/K2/K3 LED)

## LEDs Físicos (Simular na IHM Web)

A IHM física possui LEDs integrados nas teclas:

| LED | Tecla | Significado |
|-----|-------|-------------|
| LED K1 | K1 | Dobra 1 selecionada/ativa |
| LED K2 | K2 | Dobra 2 selecionada/ativa |
| LED K3 | K3 | Dobra 3 selecionada/ativa |
| LED K4 | K4 | Sentido anti-horário (esquerda) |
| LED K5 | K5 | Sentido horário (direita) |
| LED S1 | S1 | Modo AUTO ativo |
| LED S2 | S2 | (função a determinar) |

**Implementação Web**: Trocar cor da tecla quando LED ativo

## Notas do Engenheiro

### Retrofit Profissional - Requisitos

1. **Display LCD 2x20**: Simular com fonte monoespaçada, fundo verde, texto preto
2. **Teclado virtual**: Botões grandes, organizados como o físico
3. **LEDs integrados**: Brilho/cor nas teclas quando ativo
4. **Polling contínuo**: Atualizar PV a cada 250ms
5. **Modo EDIT**: Visual distinto quando editando valor
6. **Navegação fluida**: Transições entre telas
7. **Indicadores visuais**: Cursor piscando, campos editáveis destacados

### Próximas Etapas

1. ✅ Mapear todas as 11 telas
2. ⏳ Identificar registros Modbus de cada variável (análise do ladder)
3. ⏳ Criar componente Display LCD (HTML/CSS)
4. ⏳ Criar componente Teclado Virtual (HTML/CSS/JS)
5. ⏳ Implementar máquina de estados de navegação
6. ⏳ Implementar modo EDIT para entrada de valores
7. ⏳ Conectar com backend Modbus (main_server.py)
8. ⏳ Testar navegação completa
9. ⏳ Validar com usuário final

### Referências Técnicas

- `Screen.dbf`: Configuração original das telas
- `Conf.dbf`: Configuração de variáveis e placas
- `CLAUDE.md`: Endereços Modbus já mapeados
- Manual Atos Expert Series: Programação de telas (páginas específicas)
- Manual NEOCOUDE: Operação da máquina (páginas 7-8)

---

**Engenheiro**: Claude Code
**Cliente**: W&CO / Camargo Corrêa
**Máquina**: NEOCOUDE-HD-15 (2007)
**CLP**: Atos MPC4004
**IHM Original**: Expert Series 4004.95C (danificada)
**Solução**: Retrofit IHM Web responsiva (tablet)
