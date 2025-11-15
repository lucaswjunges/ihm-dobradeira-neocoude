#!/usr/bin/env python3
"""
Gera ROT5-9 usando APENAS instruções válidas do Atos MPC4004:
MOV, MOVK, SETR, OUT, CMP, CNT, RET, MONOA, CTCPU, SFR

SEM: NOT, ADD, MUL, DIV, OR, AND, RSTR (não existem neste CLP!)
"""

def criar_rot5_heartbeat_simples():
    """
    ROT5: Heartbeat simplificado (6 linhas)
    - Copia registros de status para área Modbus
    - Sem operações aritméticas complexas
    """
    content = """Lines:00006
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00002]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00003]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00004]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:OUT     T:-008 Size:001 E:08C0
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

[Line00005]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0029 Size:003 E:0400 E:08C4
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


def criar_rot6_modbus_mirror_simples():
    """
    ROT6: Espelhamento Modbus simplificado (18 linhas)
    - Apenas MOV de origem → destino
    """
    lines = """Lines:00018
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

    # E1-E7
    for i in range(1, 8):
        lines += f"""[Line{i+1:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

    # S0-S7
    for i in range(8):
        lines += f"""[Line{i+9:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

    # Encoder (linha 17) e RET (linha 18)
    lines += """[Line00017]
  [Features]
    Branchs:02
    Type:0
    Label:0
    Comment:0
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
    {0;00;04D6;-1;-1;-1;-1;00}
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


def criar_rot7_inverter_simples():
    """
    ROT7: Inversor simplificado (12 linhas)
    - Apenas copiar valores analógicos e digitais
    - SEM cálculos (MUL/DIV não existem!)
    """
    content = """Lines:00012
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0029 Size:003 E:0900 E:0881
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00006]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00007]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00008]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOVK    T:0029 Size:003 E:0888 E:0000
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

[Line00009]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CNT     T:0059 Size:004 E:0413 E:FFFF
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0029 Size:003 E:0413 E:0887
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOVK    T:0029 Size:003 E:0413 E:0000
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


def criar_rot8_stats_simples():
    """
    ROT8: Estatísticas simplificadas (15 linhas)
    - Usa contadores CNT para incrementos
    - Copia valores de status
    """
    content = """Lines:00015
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CNT     T:0059 Size:004 E:0410 E:003C
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0029 Size:003 E:0410 E:08A0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00004]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00005]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00006]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CNT     T:0059 Size:004 E:0411 E:FFFF
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0029 Size:003 E:0411 E:08AD
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CNT     T:0059 Size:004 E:0412 E:FFFF
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0029 Size:003 E:0412 E:08AF
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

[Line00010]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOVK    T:0029 Size:003 E:0412 E:0000
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

[Line00011]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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

[Line00012]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:OUT     T:-008 Size:001 E:08B0
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

[Line00013]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOVK    T:0029 Size:003 E:0410 E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08B1;-1;-1;-1;-1;00}
    ###

[Line00014]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOVK    T:0029 Size:003 E:0411 E:0000
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {0;00;08B1;-1;-1;-1;-1;00}
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


def criar_rot9_keys_simples():
    """
    ROT9: Emulação de teclas simplificada (20 linhas)
    - Usa SETR para setar bits quando comandos Modbus ativos
    """
    content = """Lines:00020
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:CNT     T:0059 Size:004 E:0414 E:FFFF
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOVK    T:0029 Size:003 E:0414 E:0000
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

    # Criar ROT5-9 simplificadas com instruções válidas
    with open(os.path.join(output_dir, "ROT5.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot5_heartbeat_simples())
    print("✅ ROT5.lad (Heartbeat simplificado - MOV, OUT)")

    with open(os.path.join(output_dir, "ROT6.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot6_modbus_mirror_simples())
    print("✅ ROT6.lad (Espelhamento Modbus - MOV)")

    with open(os.path.join(output_dir, "ROT7.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot7_inverter_simples())
    print("✅ ROT7.lad (Inversor simplificado - MOV, CNT)")

    with open(os.path.join(output_dir, "ROT8.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot8_stats_simples())
    print("✅ ROT8.lad (Estatísticas - CNT, MOV)")

    with open(os.path.join(output_dir, "ROT9.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot9_keys_simples())
    print("✅ ROT9.lad (Emulação teclas - SETR)")

    print("\n🎉 ROT5-9 recriadas com APENAS instruções válidas!")
    print("✅ SEM: NOT, ADD, MUL, DIV, OR (não existem neste CLP)")
    print("✅ COM: MOV, MOVK, SETR, OUT, CNT, RET")
