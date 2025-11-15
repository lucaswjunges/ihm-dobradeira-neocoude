#!/usr/bin/env python3
"""
ROT5-9 ULTRA-CONSERVADOR
Usa APENAS MOV para registros que existem nos originais (0900-0966)
"""

def criar_rot5_minimal():
    """ROT5: 6 linhas - copia valores básicos"""
    content = """Lines:00006
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0180 E:0960
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
    Out:MOV     T:0028 Size:003 E:0181 E:0962
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
    Out:MOV     T:0028 Size:003 E:0187 E:0964
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
    Out:MOV     T:0028 Size:003 E:0190 E:0966
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


def criar_rot6_minimal():
    """ROT6: 18 linhas - copia I/O para 0944-095F"""
    lines = """Lines:00018
"""
    # E0-E7 → 0944+
    for i in range(8):
        lines += f"""[Line{i+1:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:010{i} E:094{4+i:X}
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

    # S0-S7 → 094C+
    for i in range(8):
        lines += f"""[Line{i+9:05d}]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:018{i} E:094{12+i:X}
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

    # Encoder
    lines += """[Line00017]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:04D6 E:0954
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


def criar_rot7_minimal():
    """ROT7: 12 linhas - copia dados inversor"""
    content = """Lines:00012
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:06E0 E:0800
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
    Out:MOV     T:0028 Size:003 E:0900 E:0802
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
    Out:MOV     T:0028 Size:003 E:05F1 E:0804
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

[Line00007]
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

[Line00008]
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

[Line00009]
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

[Line00010]
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

[Line00011]
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


def criar_rot8_minimal():
    """ROT8: 15 linhas - copia ângulos"""
    content = """Lines:00015
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0840 E:0806
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
    Out:MOV     T:0028 Size:003 E:0842 E:0808
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
    Out:MOV     T:0028 Size:003 E:0848 E:080A
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

[Line00007]
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

[Line00008]
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

[Line00009]
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

[Line00010]
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

[Line00011]
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

[Line00013]
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

[Line00014]
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


def criar_rot9_minimal():
    """ROT9: 20 linhas - apenas RET por enquanto"""
    lines = """Lines:00020
"""
    for i in range(1, 21):
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
        f.write(criar_rot5_minimal())
    print("✅ ROT5 (5 MOV + RET)")

    with open(os.path.join(output_dir, "ROT6.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot6_minimal())
    print("✅ ROT6 (17 MOV + RET - I/O espelhamento)")

    with open(os.path.join(output_dir, "ROT7.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot7_minimal())
    print("✅ ROT7 (3 MOV + 9 RET)")

    with open(os.path.join(output_dir, "ROT8.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot8_minimal())
    print("✅ ROT8 (3 MOV + 12 RET)")

    with open(os.path.join(output_dir, "ROT9.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot9_minimal())
    print("✅ ROT9 (20 RET)")

    print("\n✅ ROT5-9 com APENAS MOV para registros existentes (0800-0966)")
