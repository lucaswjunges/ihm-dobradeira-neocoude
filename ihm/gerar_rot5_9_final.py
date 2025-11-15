#!/usr/bin/env python3
"""
ROT5-9 FINAL - Usando APENAS registros válidos como origem
Descoberta: Apenas ângulos (0840-0852) e registros especiais podem ser lidos com MOV!
Solução: Python lê I/O DIRETAMENTE (0100-0107, 0180-0187) - não precisa espelhar!
"""

def criar_rot5_angulos_esq():
    """ROT5: Copia ângulos esquerdos (análogo ao ROT4)"""
    content = """Lines:00006
[Line00001]
  [Features]
    Branchs:01
    Type:0
    Label:0
    Comment:0
    Out:MOV     T:0028 Size:003 E:0840 E:0944
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
    Out:MOV     T:0028 Size:003 E:0842 E:0942
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
    Out:MOV     T:0028 Size:003 E:0846 E:0944
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
    Out:MOV     T:0028 Size:003 E:0848 E:0942
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
    Out:MOV     T:0028 Size:003 E:0850 E:0944
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
    Out:MOV     T:0028 Size:003 E:0852 E:0942
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


def criar_rot6_rot9_simples():
    """ROT6-9: Apenas copiam ângulos repetidamente (seguro)"""
    lines = """Lines:00018
"""
    # Repete cópia de ângulos (sempre funciona)
    angulos = [0x0840, 0x0842, 0x0846, 0x0848, 0x0850, 0x0852]
    for i in range(18):
        src = angulos[i % 6]
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

    # ROT5: Ângulos esquerdos
    with open(os.path.join(output_dir, "ROT5.lad"), "w", encoding="utf-8", newline='\r\n') as f:
        f.write(criar_rot5_angulos_esq())
    print("✅ ROT5 (ângulos 0840-0852 → 0942/0944)")

    # ROT6-9: Copiam ângulos também (seguro)
    for rot_num, linhas in [(6, 18), (7, 12), (8, 15), (9, 20)]:
        content = f"Lines:000{linhas:02d}\n"
        angulos = [0x0840, 0x0842, 0x0846, 0x0848, 0x0850, 0x0852]
        for i in range(linhas):
            src = angulos[i % 6]
            dest = 0x0944 if i % 2 == 0 else 0x0942
            content += f"""[Line{i+1:05d}]
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
        with open(os.path.join(output_dir, f"ROT{rot_num}.lad"), "w", encoding="utf-8", newline='\r\n') as f:
            f.write(content)
        print(f"✅ ROT{rot_num} (ângulos 0840-0852 → 0942/0944)")

    print("\n✅ Usando APENAS registros válidos como origem!")
    print("   Origem: 0840, 0842, 0846, 0848, 0850, 0852")
    print("   Destino: 0942, 0944")
    print("\n💡 Python lê I/O DIRETAMENTE (0100-0107, 0180-0187)!")
