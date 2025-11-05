**Para:** Claude Code
**De:** [Seu Nome/Empresa de Automação]
**Assunto:** Desenvolvimento de uma IHM Web Completa para a Dobradeira de Vergalhão Trillor NEOCOUDE-HD-15 com CLP Atos MPC4004.

### 1. Visão Geral do Projeto

Sua missão é atuar como desenvolvedor sênior de automação full-stack. [cite_start]Você deve projetar e implementar o código para uma IHM moderna, baseada na web, para substituir a interface física obsoleta de uma dobradeira de vergalhão **Trillor NEOCOUDE-HD-15** (fabricada em 2007)[cite: 21372, 21381, 22139].

[cite_start]O cérebro da máquina é um CLP **Atos Série Expert (MCP4004)**[cite: 17701, 17761, 21409]. [cite_start]O software de programação original é o **WinSUP 2**[cite: 17707, 17708]. [cite_start]O programa ladder original do CLP (`clp.sup`) [cite: 13365-13370] está disponível para análise de seus nomes de arquivo, e os manuais de hardware (`M400423w2p_ATOS.pdf` e `NEOCOUDE-HD 15 - Camargo 2007.pdf`) estão anexados.

### 2. Diagnóstico Atual (O Problema a ser Resolvido)

O diagnóstico em campo revelou o seguinte:
* O CLP está **saudável**. [cite_start]O **LED STS (Status) pisca rápido (0,2s)**, o que os manuais confirmam ser o modo **RUN NORMAL**[cite: 21166].
* O programa de usuário (`DOBRADEIRA HC` / `clp.sup`) está **ativo e rodando**.
* [cite_start]O **problema principal** é que a IHM física (modelo **4004.95C**) [cite: 17793, 20958, 17958, 20954, 18187] está danificada pelo tempo e seus botões/visor não funcionam.
* **Nosso objetivo não é consertar o CLP, mas sim substituir a IHM quebrada.**

### 3. Arquitetura do Sistema

Para este projeto de desenvolvimento, você criará um **aplicativo de servidor no Ubuntu 25.04 (notebook)**, que servirá como um protótipo 1:1 da solução final que rodará em um `ESP32`.

1.  **CLP (Escravo):** `Atos MPC4004`.
2.  **Notebook (Mestre & Servidor):** `Ideapad 330` rodando `Ubuntu 25.04`.
3.  **Display (Cliente):** Um `Tablet` (qualquer OS) usando um navegador web padrão.
4.  **Comunicação (CLP <-> Notebook):** `RS485` (Canal B do CLP) via conversor `USB-RS485-FTDI` (que aparecerá no Ubuntu como `/dev/ttyUSB0` ou `/dev/ttyUSB1`).
5.  **Comunicação (Notebook <-> Tablet):** `WiFi`. Conforme a especificação, o **Tablet atuará como Hotspot/Roteador WiFi**, e o notebook Ubuntu se conectará a ele como um cliente.

### 4. Estratégia de Desenvolvimento (Web-First, Robusta, Modular)

Conforme solicitado, o desenvolvimento deve priorizar a aplicação web. A solução final para o ESP32 (MicroPython) deve ser quase idêntica à solução de prototipagem (Python) que você desenvolverá agora.

**Tecnologia Solicitada:**
* **Back-End (Notebook Ubuntu):** `Python 3`. Use `asyncio`, `websockets` (para o servidor web) e `pymodbus` (para a comunicação serial).
* **Front-End (Tablet):** `HTML5`, `CSS3` e `JavaScript` (vanilla, sem frameworks pesados), utilizando `WebSockets` para comunicação em tempo real.

O código deve ser **modular** e **robusto** para lidar com falhas de comunicação sem travar.

---

### Fase 1: Análise Crítica dos Manuais (A "Bíblia" do Projeto)

O sucesso deste projeto depende do nosso profundo entendimento dos manuais. Sua implementação deve se basear nestas descobertas:

#### 1.1. Ativação do Modbus (Pré-requisito JÁ REALIZADO)
O usuário (eu) já conectou ao CLP com o WinSUP 2 e modificou o programa ladder para forçar o **estado interno `0BE`** para LIGADO (usando o bit `00F7` "Sempre Ligado").
* **Sua Ação:** O seu script Python deve assumir que a porta RS485 (Canal B) do CLP já está falando **Modbus RTU** como um **Escravo**.
* [cite_start]**Referências:** [cite: 19449, 19450, 20261, 21138, 20868, 20872]

#### 1.2. Mapeamento da IHM Física (A "Chave de Ouro")
[cite_start]Sua aplicação **DEVE** replicar 100% do teclado físico da IHM (`4004.95C`)[cite: 17793, 20958, 22284]. [cite_start]O Back-End (Python) enviará comandos Modbus `Force Single Coil (0x05)` [cite: 20241, 20242, 20870, 20869, 21133] para os bits correspondentes.

| Tecla Física (IHM) | Bit de Estado Interno (CLP) | Referência no Manual |
| :--- | :--- | :--- |
| `K1` a `K9` | [cite_start]`00A0` a `00A8` | [cite: 19449, 19450, 20263, 21065, 21062] |
| `K0` | [cite_start]`00A9` | [cite: 19449, 19450, 20263, 21065, 21062] |
| `S1` | [cite_start]`00DC` | [cite: 19449, 19450, 20263, 21062, 20969, 20970] |
| `S2` | [cite_start]`00DD` | [cite: 19449, 19450, 20263, 21062, 20969, 20970] |
| `Seta Cima` (↑) | [cite_start]`00AC` | [cite: 19449, 19450, 20263, 21062] |
| `Seta Baixo` (↓) | [cite_start]`00AD` | [cite: 19449, 19450, 20263, 21062] |
| `ESC` | [cite_start]`00BC` | [cite: 19449, 19450, 20263, 21062] |
| `Lock` | [cite_start]`00F1` | [cite: 19445, 19446, 20257, 21062] |
| `EDITA` (Edição) | [cite_start]`0026` | [cite: 20264, 20971, 20979] |
| `ENTRA` (Seta →) | [cite_start]`0025` | [cite: 20264, 20971, 20979] |

#### 1.3. Mapeamento de Dados (O "Mapa do Tesouro")
Crie um módulo de configuração centralizado (ex: `modbus_map.py`) para todos os endereços. [cite_start]O usuário (eu) preencherá os endereços específicos do programa `clp.sup` [cite: 13365-13370] após a análise do ladder.

**Valores Conhecidos (dos manuais):**
* [cite_start]**Leitura do Encoder (Ângulo):** Registros `04D6`/`04D7` (Efetivo do Contador Rápido da CPU)[cite: 20143, 20144, 20145, 20770].
* [cite_start]**Entradas Digitais (Diagnóstico):** `0100` - `0107` (Mapeamento de E0-E7 da CPU)[cite: 19445, 19446, 19477, 19468, 19469, 19470].
* [cite_start]**Saídas Digitais (Diagnóstico):** `0180` - `0187` (Mapeamento de S0-S7 da CPU)[cite: 19445, 19446, 19491, 19468, 19469, 19470].

**Valores a Mapear (Placeholders):**
* `REG_SETPOINT_ANGULO_1`, `_2`, `_3` (Registros para os 3 ângulos de dobra).
* `REG_SETPOINT_QUANTIDADE_1`, `_2`, `_3` (Registros para as 3 quantidades).
* `REG_CONTADOR_PECAS_ATUAL` (Registro do contador de peças do programa).
* `BIT_CICLO_ATIVO` (Estado interno que indica que a máquina está em movimento).
* `BIT_EMERGENCIA` (Estado interno do botão de emergência).
* ... (Adicione outros placeholders que julgar necessários para uma dobradeira).

---

### Fase 2: Estrutura do Software (Foco em Robustez)

Por favor, gere o código Python 3 para os módulos do Back-End e o HTML/CSS/JS para o Front-End. O código deve ser modular.

**Módulos do Back-End (Python 3 para Ubuntu 25.04):**

1.  **`modbus_map.py` (O Mapa de Memória):**
    * Crie um ficheiro Python contendo um dicionário (`dict`) com todos os endereços de Coils e Registos que conhecemos (K1, S1, Encoder, E/S). Use endereços decimais.
    * Inclua os placeholders para os registos do programa que eu terei de preencher (`REG_SETPOINT_ANGULO_1`, etc.).

2.  **`modbus_client.py` (O Módulo de Hardware):**
    * Crie uma classe `ModbusClient`.
    * **Modo Stub (para Web-first):** Deve ter um modo `stub_mode = True` que, quando ativado, retorna dados falsos (ex: `read_encoder()` retorna um número aleatório) sem tentar ligar-se à porta serial.
    * **Modo Live:** A classe deve usar `pymodbus.client.ModbusSerialClient` para se conectar ao `/dev/ttyUSB0` (ou `COM7`) com `baudrate=57600`, `parity='N'`, `stopbits=1`, `bytesize=8`.
    * **Robustez:** Todas as funções de leitura/escrita (`read_coils`, `read_holding_registers`, `write_coil`, `write_register`) DEVEM ter tratamento de exceções (try/except) para `ModbusException` e timeouts. Se falhar, deve retornar `None` ou `False`, **nunca travar**.
    * **Funções de Simulação de Tecla:** Crie uma função `press_key(address)` que executa `write_coil(address, True)` seguido de um `asyncio.sleep(0.1)` e `write_coil(address, False)` para simular um toque de botão.

3.  **`state_manager.py` (O "Gêmeo Digital"):**
    * Crie um loop `asyncio` (`poll_clp_data`) que, a cada 250ms, chama o `modbus_client` para ler todos os dados vitais da máquina (Encoder, status de E/S, contadores) e os armazena num dicionário de estado (`machine_state`).
    * Este módulo é a **única fonte da verdade** para o servidor web.

4.  **`main_server.py` (O Servidor Principal):**
    * Deve usar `asyncio` e `websockets`.
    * Inicia o `state_manager` para começar o polling em segundo plano.
    * Inicia um servidor WebSocket em `localhost:8080`.
    * **Lógica do WebSocket:**
        * `on_connect`: Envia o `machine_state` completo para o novo cliente (o tablet).
        * `push_updates`: Deve observar o `machine_state` e, sempre que um valor mudar, enviar *apenas essa mudança* (um "delta") para todos os tablets conectados (ex: `{'angulo': 90.5}`).
        * `on_message`: Deve receber comandos JSON do tablet (ex: `{'action': 'press', 'key': 'K1'}`).
        * **Lógica de Ação:** Ao receber um comando, ele o traduz e chama a função correta no `modbus_client` (ex: `modbus_client.press_key(modbus_map.COILS['K1'])`).
    * **Lógica de Internet (Futuro):** Deve incluir funções *stub* (vazias) chamadas `send_telegram_alert(message)` e `log_to_sheets(data)` para mostrar como a conectividade do Ubuntu pode ser usada.

---

### Fase 3: Front-End (A IHM Web - `ihm.html`)

Por favor, gere um **ficheiro `index.html` único** (incluindo CSS e JavaScript) que sirva como a IHM.

* **Design:** Moderno, limpo, intuitivo e responsivo (para se adaptar a qualquer tablet). Use CSS flexbox ou grid.
* **Robustez:** O JavaScript deve usar `WebSocket` para ligar-se ao `ws://localhost:8080`.
* **Gestão de Erros:**
    * O JS DEVE mostrar um *overlay* (camada) ou banner vermelho "DESLIGADO" se o WebSocket desconectar.
    * O JS DEVE mostrar um *overlay* "FALHA CLP" se o Back-End (Python) reportar um erro de Modbus.
    * Todos os botões devem ser desabilitados durante falhas.
* **Estrutura da UI (Abas):**

    1.  **Aba "Operação":**
        * Um grande "Manómetro" ou display digital para o **Ângulo do Encoder** (lido do `04D6`/`04D7`).
        * Campos de entrada para os **Setpoints** (Ângulo, Quantidade).
        * [cite_start]Botões grandes para **replicar o teclado da IHM** (`K0-K9`, `S1`, `S2`, `Setas`, `ESC`, `EDIT`, `ENTER`) [cite: 22247-22277].
    2.  **Aba "Diagnóstico":**
        * Uma secção "Digital Twin" que simula o painel.
        * [cite_start]**Entradas:** LEDs virtuais para `E0` a `E7` (baseado nos bits `0100`-`0107`)[cite: 19445, 19446, 19477, 19468, 19469, 19470, 19476].
        * [cite_start]**Saídas:** LEDs virtuais para `S0` a `S7` (baseado nos bits `0180`-`0187`)[cite: 19445, 19446, 19491, 19468, 19469, 19470, 19488].
        * **(Futuro) Sensores ESP32:** Um espaço reservado para "Novos Sensores".
    3.  **Aba "Logs e Produção":**
        * Um **Contador de Tempo de Uso** (que funciona quando o `BIT_CICLO_ATIVO` está ON).
        * Um log de texto para **Alertas** (ex: "Emergência ativada", "Falha de comunicação").
    4.  **Aba "Configuração":**
        * Campos de texto (desabilitados por agora) para "SSID do Tablet" e "Senha do WiFi" (para quando isto migrar para o ESP32).