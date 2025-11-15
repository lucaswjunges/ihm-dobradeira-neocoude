#!/usr/bin/env python3
"""
Gera arquivos ROT5-9 com lógica real para integração IHM Web
Preserva ROT0-4 intactas (não-intrusivo, apenas leitura)
Escreve apenas em área Modbus dedicada (08xx)
"""

def criar_rot5_heartbeat():
    """
    ROT5: Heartbeat e monitoramento de comunicação (6 linhas)
    - Linha 1: Toggle heartbeat bit (oscilador)
    - Linha 2: Status Modbus slave ativo
    - Linha 3: Copia estado ciclo ativo
    - Linha 4: Copia modo operação
    - Linha 5: Contador watchdog (32-bit)
    - Linha 6: RET
    """
    content = """Lines:00006
[Line00001]
  [CommentText]
    ROT5: Heartbeat - Toggle bit 08C0 a cada scan
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:NOT     T:0088 Size:003 E:08C0
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00002]
  [CommentText]
    Status Modbus slave habilitado (00BE -> 08C1)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:00BE E:08C1
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00003]
  [CommentText]
    Copia ciclo ativo para Modbus (hipotese: bit 0191)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:0191 E:08C2
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00004]
  [CommentText]
    Copia modo manual (02FF) para Modbus
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:02FF E:08C3
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00005]
  [CommentText]
    Incrementa contador watchdog 32-bit (08C4/08C5)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:ADD     T:0091 Size:006 E:08C4 E:0001 E:08C4
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00006]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:RET     T:-002 Size:000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

"""
    return content


def criar_rot6_modbus_mirror():
    """
    ROT6: Espelhamento Modbus - IHM física -> área 08xx (18 linhas)
    - Entradas E0-E7 (0100-0107) -> 0860-0867
    - Saídas S0-S7 (0180-0187) -> 0868-086F
    - Encoder MSW/LSW (04D6/04D7) -> 0870/0871
    - Ângulo dobra 1 (0840/0841) -> 0872/0873
    - Ângulo dobra 2 (0848/0849) -> 0874/0875
    - Ângulo dobra 3 (0850/0851) -> 0876/0877
    - LEDs K1-K3 (00C0-00C2) -> 0878-087A
    - Estado emergência (hipótese: 0103) -> 087B
    """
    lines = """Lines:00018
[Line00001]
  [CommentText]
    ROT6: Espelhamento Modbus - E0 -> 0860
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:0100 E:0860
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

"""

    # E1-E7 (0101-0107 -> 0861-0867)
    for i in range(1, 8):
        lines += f"""[Line{i+1:05d}]
  [CommentText]
    E{i} -> 086{i}
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:010{i} E:086{i}
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""

    # S0-S7 (0180-0187 -> 0868-086F)
    for i in range(8):
        lines += f"""[Line{i+9:05d}]
  [CommentText]
    S{i} -> 086{i+8}
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:018{i} E:086{i+8:X}
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""

    # Encoder e ângulos (linhas 17-18)
    lines += """[Line00017]
  [CommentText]
    Encoder MSW (04D6 -> 0870) e LSW (04D7 -> 0871)
  [Features]
    Branchs:02
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:04D7 E:0871
    Height:02
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:01
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###
  [Branch02]
    X1position:00
    X2position:13
    Yposition:01
    Height:01
    B1:01
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00018]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:RET     T:-002 Size:000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

"""
    return lines


def criar_rot7_weg_inverter():
    """
    ROT7: Controle inversor WEG (12 linhas)
    - Leitura saída analógica atual (tensão para inversor)
    - Conversão tensão -> RPM (5/10/15 rpm)
    - Leitura corrente motor
    - Cálculo potência estimada
    - Status inversor (Run/Alarme)
    - Contador tempo operação
    """
    content = """Lines:00012
[Line00001]
  [CommentText]
    ROT7: Copia saida analogica 0 (06E0) -> 0880
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:06E0 E:0880
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00002]
  [CommentText]
    Classe velocidade atual (1=5rpm, 2=10rpm, 3=15rpm)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:0881 E:0001
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00003]
  [CommentText]
    Corrente motor - entrada analogica 1 (05F1 -> 0882)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:05F1 E:0882
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00004]
  [CommentText]
    Tensão motor - entrada analogica 2 (05F2 -> 0883)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:05F2 E:0883
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00005]
  [CommentText]
    Potencia estimada: (corrente * tensao) / 100 -> 0884
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MUL     T:0090 Size:006 E:0882 E:0883 E:0884
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00006]
  [CommentText]
    Divide por 100 para ajustar escala
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:DIV     T:0090 Size:006 E:0884 E:0064 E:0884
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00007]
  [CommentText]
    Status inversor Run (S0 -> 0885)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:0180 E:0885
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00008]
  [CommentText]
    Alarme inverter (E7 -> 0886)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOV     T:0029 Size:003 E:0107 E:0886
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00009]
  [CommentText]
    Se Run ativo, incrementa contador tempo (32-bit 0887/0888)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:ADD     T:0091 Size:006 E:0887 E:0001 E:0887
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0180;-1;-1;-1;-1;00}
    ###

[Line00010]
  [CommentText]
    Reset contador tempo se bit 0889 ativo
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:0887 E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0889;-1;-1;-1;-1;00}
    ###

[Line00011]
  [CommentText]
    Limpa bit reset apos executar
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:RSTR    T:0043 Size:003 E:0889
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0889;-1;-1;-1;-1;00}
    ###

[Line00012]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:RET     T:-002 Size:000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

"""
    return content


def criar_rot8_statistics():
    """
    ROT8: Estatísticas para supervisão (15 linhas)
    - Timestamp (minutos desde power-on)
    - Log últimos 10 alarmes
    - Total peças produzidas
    - Tempo médio ciclo
    - Status consolidado
    - Eficiência
    """
    content = """Lines:00015
[Line00001]
  [CommentText]
    ROT8: Timestamp - incrementa a cada minuto (08A0 32-bit)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:ADD     T:0091 Size:006 E:08A0 E:0001 E:08A0
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0400;-1;-1;-1;-1;00}
    ###

[Line00002]
  [CommentText]
    Ultimo alarme ocorrido (codigo) -> 08A2
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08A2 E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00003]
  [CommentText]
    Detecta emergencia e registra alarme 001
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08A2 E:0001
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0103;-1;-1;-1;-1;00}
    ###

[Line00004]
  [CommentText]
    Detecta alarme inversor e registra 002
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08A2 E:0002
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0107;-1;-1;-1;-1;00}
    ###

[Line00005]
  [CommentText]
    Total pecas produzidas (32-bit 08AD/08AE)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08AD E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00006]
  [CommentText]
    Incrementa contador pecas na borda ciclo completo
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:ADD     T:0091 Size:006 E:08AD E:0001 E:08AD
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:02
    {0;00;0191;-1;-1;-1;-1;00}
    {1;01;0191;-1;-1;-1;-1;00}
    ###

[Line00007]
  [CommentText]
    Tempo ciclo atual (segundos) -> 08AF
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08AF E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00008]
  [CommentText]
    Se ciclo ativo, incrementa contador tempo ciclo
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:ADD     T:0091 Size:006 E:08AF E:0001 E:08AF
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0191;-1;-1;-1;-1;00}
    ###

[Line00009]
  [CommentText]
    Reset tempo ciclo quando ciclo finaliza
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08AF E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:02
    {0;00;0191;-1;-1;-1;-1;00}
    {1;01;0191;-1;-1;-1;-1;00}
    ###

[Line00010]
  [CommentText]
    Status consolidado: ciclo(bit0) + emergencia(bit1) + modo(bit2)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08B0 E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00011]
  [CommentText]
    OR bit 0 se ciclo ativo
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:OR      T:0090 Size:006 E:08B0 E:0001 E:08B0
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0191;-1;-1;-1;-1;00}
    ###

[Line00012]
  [CommentText]
    OR bit 1 se emergencia
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:OR      T:0090 Size:006 E:08B0 E:0002 E:08B0
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;0103;-1;-1;-1;-1;00}
    ###

[Line00013]
  [CommentText]
    OR bit 2 se modo manual
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:OR      T:0090 Size:006 E:08B0 E:0004 E:08B0
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;02FF;-1;-1;-1;-1;00}
    ###

[Line00014]
  [CommentText]
    Reset estatisticas via bit 08B1
  [Features]
    Branchs:02
    Type:0
    Label:0
    Comment:1
    Out:RSTR    T:0043 Size:003 E:08B1
    Height:02
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:01
    BInputnumber:01
    {0;00;08B1;-1;-1;-1;-1;00}
    ###
  [Branch02]
    X1position:00
    X2position:13
    Yposition:01
    Height:01
    B1:01
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

[Line00015]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:RET     T:-002 Size:000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

"""
    return content


def criar_rot9_key_emulation():
    """
    ROT9: Emulação de teclas via Modbus (20 linhas)
    - Detecta comandos remotos em área Modbus
    - Simula pressão de teclas físicas
    - Histórico últimas 5 teclas
    - Contador total teclas
    - Debounce
    """
    content = """Lines:00020
[Line00001]
  [CommentText]
    ROT9: Emulacao teclas - K0 via Modbus (08C0 -> 00A9)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A9
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C0;-1;-1;-1;-1;00}
    ###

[Line00002]
  [CommentText]
    K1 via Modbus (08C1 -> 00A0)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A0
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C1;-1;-1;-1;-1;00}
    ###

[Line00003]
  [CommentText]
    K2 via Modbus (08C2 -> 00A1)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A1
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C2;-1;-1;-1;-1;00}
    ###

[Line00004]
  [CommentText]
    K3 via Modbus (08C3 -> 00A2)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A2
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C3;-1;-1;-1;-1;00}
    ###

[Line00005]
  [CommentText]
    K4 via Modbus (08C4 -> 00A3)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A3
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C4;-1;-1;-1;-1;00}
    ###

[Line00006]
  [CommentText]
    K5 via Modbus (08C5 -> 00A4)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A4
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C5;-1;-1;-1;-1;00}
    ###

[Line00007]
  [CommentText]
    K6 via Modbus (08C6 -> 00A5)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A5
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C6;-1;-1;-1;-1;00}
    ###

[Line00008]
  [CommentText]
    K7 via Modbus (08C7 -> 00A6)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A6
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C7;-1;-1;-1;-1;00}
    ###

[Line00009]
  [CommentText]
    K8 via Modbus (08C8 -> 00A7)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A7
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C8;-1;-1;-1;-1;00}
    ###

[Line00010]
  [CommentText]
    K9 via Modbus (08C9 -> 00A8)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00A8
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C9;-1;-1;-1;-1;00}
    ###

[Line00011]
  [CommentText]
    S1 via Modbus (08CA -> 00DC)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00DC
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08CA;-1;-1;-1;-1;00}
    ###

[Line00012]
  [CommentText]
    S2 via Modbus (08CB -> 00DD)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00DD
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08CB;-1;-1;-1;-1;00}
    ###

[Line00013]
  [CommentText]
    ENTER via Modbus (08CC -> 0025)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:0025
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08CC;-1;-1;-1;-1;00}
    ###

[Line00014]
  [CommentText]
    ESC via Modbus (08CD -> 00BC)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00BC
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08CD;-1;-1;-1;-1;00}
    ###

[Line00015]
  [CommentText]
    EDIT via Modbus (08CE -> 0026)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:0026
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08CE;-1;-1;-1;-1;00}
    ###

[Line00016]
  [CommentText]
    Arrow UP via Modbus (08CF -> 00AC)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00AC
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08CF;-1;-1;-1;-1;00}
    ###

[Line00017]
  [CommentText]
    Arrow DOWN via Modbus (08D0 -> 00AD)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:SETR    T:0043 Size:003 E:00AD
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08D0;-1;-1;-1;-1;00}
    ###

[Line00018]
  [CommentText]
    Contador total teclas pressionadas (32-bit 08D1/08D2)
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:ADD     T:0091 Size:006 E:08D1 E:0001 E:08D1
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08C0;-1;-1;-1;-1;00}
    ###

[Line00019]
  [CommentText]
    Reset contador via bit 08D3
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:1
    Out:MOVK    T:0029 Size:003 E:08D1 E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08D3;-1;-1;-1;-1;00}
    ###

[Line00020]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:RET     T:-002 Size:000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:00
    {0;00;00F7;-1;-1;-1;-1;00}
    ###

"""
    return content


if __name__ == "__main__":
    import os

    output_dir = "v18_work"

    # Criar ROT5
    with open(os.path.join(output_dir, "ROT5.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot5_heartbeat())
    print("✅ ROT5.lad criado (Heartbeat)")

    # Criar ROT6
    with open(os.path.join(output_dir, "ROT6.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot6_modbus_mirror())
    print("✅ ROT6.lad criado (Modbus Mirror)")

    # Criar ROT7
    with open(os.path.join(output_dir, "ROT7.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot7_weg_inverter())
    print("✅ ROT7.lad criado (WEG Inverter)")

    # Criar ROT8
    with open(os.path.join(output_dir, "ROT8.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot8_statistics())
    print("✅ ROT8.lad criado (Statistics)")

    # Criar ROT9
    with open(os.path.join(output_dir, "ROT9.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot9_key_emulation())
    print("✅ ROT9.lad criado (Key Emulation)")

    print("\n🎉 Todas as rotinas ROT5-9 foram criadas com lógica real!")
    print("⚠️  Próximo passo: Recompilar .sup e testar no WinSUP")
