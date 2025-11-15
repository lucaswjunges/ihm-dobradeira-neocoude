#!/usr/bin/env python3
"""
ROT5-9 PROFISSIONAL - Copiando EXATAMENTE o padrão de ROT0-4
- BInputnumber:00 com {0;00;00F7;...} = SEMPRE EXECUTA
- Height:03 para espaçamento visual
- Estrutura idêntica às originais
"""

def criar_rot5_heartbeat():
    """ROT5: 6 linhas - espelhamento status (padrão ROT4)"""
    content = """Lines:00006
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0191 E:0942
    Height:03
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
    Height:03
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
    Height:03
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
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0180 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0181 E:0944
    Height:03
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
    """ROT6: 18 linhas - E0-E7 + encoder (padrão ROT4)"""
    lines = """Lines:00018
"""
    # E0-E7 alternando 0942/0944
    for i in range(8):
        dest = 0x0944 if i % 2 == 0 else 0x0942
        lines += f"""[Line{i+1:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:010{i} E:{dest:04X}
    Height:03
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

    # S0-S7 alternando 0942/0944
    for i in range(8):
        dest = 0x0942 if i % 2 == 0 else 0x0944
        lines += f"""[Line{i+9:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:018{i} E:{dest:04X}
    Height:03
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
    lines += """[Line00017]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:04D6 E:0942
    Height:03
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

[Line00018]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:04D7 E:0944
    Height:03
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


def criar_rot7_inversor():
    """ROT7: 12 linhas - dados inversor WEG (padrão ROT4)"""
    content = """Lines:00012
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:06E0 E:0942
    Height:03
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
    Height:03
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
    Height:03
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
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0187 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0190 E:0944
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0100 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0101 E:0944
    Height:03
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0102 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0103 E:0944
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0104 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0105 E:0944
    Height:03
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


def criar_rot8_adicionais():
    """ROT8: 15 linhas - dados adicionais (padrão ROT4)"""
    content = """Lines:00015
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0106 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0107 E:0944
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0182 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0183 E:0944
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0184 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0185 E:0944
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0186 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:05F0 E:0944
    Height:03
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
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0400 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0401 E:0944
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0402 E:0942
    Height:03
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
    Out:MOV     T:0028 Size:003 E:0403 E:0944
    Height:03
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

[Line00013]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0404 E:0942
    Height:03
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

[Line00014]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0405 E:0944
    Height:03
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

[Line00015]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0406 E:0942
    Height:03
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


def criar_rot9_mais_dados():
    """ROT9: 20 linhas - ainda mais dados (padrão ROT4)"""
    lines = """Lines:00020
"""
    for i in range(20):
        src = 0x0407 + i
        dest = 0x0944 if i % 2 == 0 else 0x0942
        lines += f"""[Line{i+1:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:{src:04X} E:{dest:04X}
    Height:03
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
        f.write(criar_rot5_heartbeat())
    print("✅ ROT5 (status + I/O → 0942/0944)")

    with open(os.path.join(output_dir, "ROT6.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot6_io_espelhamento())
    print("✅ ROT6 (E0-E7, S0-S7, encoder → 0942/0944)")

    with open(os.path.join(output_dir, "ROT7.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot7_inversor())
    print("✅ ROT7 (inversor + E0-E5 → 0942/0944)")

    with open(os.path.join(output_dir, "ROT8.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot8_adicionais())
    print("✅ ROT8 (E6-E7, S2-S6, timers → 0942/0944)")

    with open(os.path.join(output_dir, "ROT9.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot9_mais_dados())
    print("✅ ROT9 (timers 0407-041A → 0942/0944)")

    print("\n✅ Padrão PROFISSIONAL copiado de ROT0-4!")
    print("   - Height:03 (espaçamento visual)")
    print("   - BInputnumber:00 com 00F7 (sempre executa)")
    print("   - T:0028 (tipo MOV correto)")
