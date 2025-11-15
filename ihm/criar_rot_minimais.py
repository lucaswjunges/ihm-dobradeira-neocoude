#!/usr/bin/env python3
"""
Cria arquivos ROT5-9 MINIMAIS mas com estrutura válida
Cada um terá apenas linhas vazias (ret) para completar o número declarado
"""

# Template para linha vazia (apenas RET - return)
LINE_TEMPLATE = """[Line{num:05d}]
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

# Configuração: rotina -> (número de linhas, descrição)
ROUTINES = {
    'ROT5': (6, 'Comunicação básica'),
    'ROT6': (18, 'Integração Modbus'),
    'ROT7': (12, 'Comunicação inversor'),
    'ROT8': (15, 'Estatísticas'),
    'ROT9': (20, 'Emulação teclas')
}

for rot_name, (line_count, desc) in ROUTINES.items():
    # Criar arquivo
    content = f"Lines:{line_count:05d}\n"

    for i in range(1, line_count + 1):
        content += LINE_TEMPLATE.format(num=i)

    # Escrever arquivo
    filename = f"v18_build/{rot_name}.lad"
    with open(filename, 'w', newline='\r\n') as f:
        f.write(content)

    # Criar .txt vazio
    with open(f"v18_build/{rot_name}.txt", 'w', newline='\r\n') as f:
        pass

    print(f"✅ {rot_name}.lad criado com {line_count} linhas ({desc})")

print("\n✅ Todas as rotinas criadas com estrutura válida!")
print("   Cada linha é um RET (return vazio)")
print("   Números de linhas batem com cabeçalhos!")
