#!/usr/bin/env python3
"""
ROT5-9 usando APENAS registros válidos descobertos:
- Destino MOV: 0942, 0944 (únicos válidos além de auto-refresh!)
- Origem: I/O, encoder, ângulos, status
- Padrão EXATO copiado do ROT4.lad original
"""

def criar_rot5_status():
    """ROT5: Copia status para 0942/0944"""
    content = """Lines:00006
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0191 E:0942
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
    Out:MOV     T:0028 Size:003 E:02FF E:0944
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
    Out:MOV     T:0028 Size:003 E:00BE E:0942
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
    Out:MOV     T:0028 Size:003 E:0400 E:0944
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


def criar_rot6_io_espelhamento():
    """ROT6: Espelha I/O ENTRADAS para 0942/0944 (alternando)"""
    lines = """Lines:00018
"""
    # E0-E7 alternando entre 0942 e 0944
    for i in range(8):
        dest = 0x0944 if i % 2 == 0 else 0x0942
        lines += f"""[Line{i+1:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:010{i} E:{dest:04X}
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

    # Encoder MSW e LSW
    lines += """[Line00009]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:04D6 E:0942
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
    Out:MOV     T:0028 Size:003 E:04D7 E:0944
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

    # Resto = RET
    for i in range(11, 19):
        lines += f"""[Line{i:05d}]
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
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""
    return lines


def criar_rot7_inversor():
    """ROT7: Dados inversor WEG para 0942/0944"""
    content = """Lines:00012
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:06E0 E:0942
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
    Out:MOV     T:0028 Size:003 E:0900 E:0944
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
    Out:MOV     T:0028 Size:003 E:05F1 E:0942
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
    Out:MOV     T:0028 Size:003 E:05F2 E:0944
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

    for i in range(5, 13):
        content += f"""[Line{i:05d}]
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
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""
    return content


def criar_rot8_angulos():
    """ROT8: Já é feito pelo ROT4! Apenas RET"""
    lines = """Lines:00015
"""
    for i in range(1, 16):
        lines += f"""[Line{i:05d}]
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
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""
    return lines


def criar_rot9_teclas():
    """ROT9: Emulação teclas - SETR validado"""
    lines = """Lines:00020
"""
    # K0-K9, S1, S2, ENTER, ESC, etc - usar SETR
    teclas = [
        (1, "00A9"),  # K0
        (2, "00A0"),  # K1
        (3, "00A1"),  # K2
        (4, "00A2"),  # K3
        (5, "00A3"),  # K4
        (6, "00A4"),  # K5
        (7, "00DC"),  # S1
        (8, "00DD"),  # S2
        (9, "0025"),  # ENTER
        (10, "00BC"), # ESC
    ]

    for linha, bit in teclas:
        # Condição: se 0942 ou 0944 contém comando
        lines += f"""[Line{linha:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:SETR    T:0043 Size:003 E:{bit}
    Height:01
  [Branch01]
    X1position:00
    X2position:13
    Yposition:00
    Height:01
    B1:00
    B2:00
    BInputnumber:01
    {{0;00;0942;-1;-1;-1;-1;00}}
    ###

"""

    # Resto = RET
    for i in range(11, 21):
        lines += f"""[Line{i:05d}]
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
    {{0;00;00F7;-1;-1;-1;-1;00}}
    ###

"""
    return lines


if __name__ == "__main__":
    import os

    output_dir = "v18_work"

    with open(os.path.join(output_dir, "ROT5.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot5_status())
    print("✅ ROT5 (status → 0942/0944)")

    with open(os.path.join(output_dir, "ROT6.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot6_io_espelhamento())
    print("✅ ROT6 (E0-E7, encoder → 0942/0944)")

    with open(os.path.join(output_dir, "ROT7.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot7_inversor())
    print("✅ ROT7 (inversor WEG → 0942/0944)")

    with open(os.path.join(output_dir, "ROT8.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot8_angulos())
    print("✅ ROT8 (RET - ângulos já em ROT4)")

    with open(os.path.join(output_dir, "ROT9.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot9_teclas())
    print("✅ ROT9 (teclas via SETR)")

    print("\n✅ Usando APENAS 0942/0944 como destino MOV!")
