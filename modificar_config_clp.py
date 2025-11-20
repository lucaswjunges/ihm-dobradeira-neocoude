#!/usr/bin/env python3
"""
Script para modificar configurações do CLP ATOS que o WinSup 2 bloqueia na interface.
Modifica o arquivo Conf.smt dentro do projeto .sup
"""

import zipfile
import os
import sys
import shutil
from datetime import datetime

# Configurações modificáveis (valor atual → valor sugerido)
CONFIGURACOES_INTERESSANTES = {
    'FRONTREMOTO': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita IHM remota (bloqueado no WinSup 2)',
        'recomendado': True
    },
    'FRONTAL': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita comunicação com frontal',
        'recomendado': False
    },
    'HMAMI': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita HMI Master Interface',
        'recomendado': False
    },
    'FORCE': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita modo FORCE (forçar I/O)',
        'recomendado': False
    },
    'ESCUTA': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita modo ESCUTA (monitor)',
        'recomendado': False
    },
    'RECFRONTAL': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita receitas no frontal',
        'recomendado': False
    },
    'HAB_SENHA': {
        'atual': '0',
        'novo': '1',
        'descricao': 'Habilita proteção por senha',
        'recomendado': False
    },
    'WATCHDOGTIMER': {
        'atual': '1',
        'novo': '0',
        'descricao': 'Desabilita Watchdog Timer (cuidado!)',
        'recomendado': False
    }
}

def listar_configuracoes():
    """Lista todas as configurações disponíveis"""
    print("\n" + "="*80)
    print("CONFIGURAÇÕES DISPONÍVEIS PARA MODIFICAÇÃO")
    print("="*80 + "\n")

    for i, (param, config) in enumerate(CONFIGURACOES_INTERESSANTES.items(), 1):
        recomendado = " [RECOMENDADO]" if config['recomendado'] else ""
        print(f"{i}. {param}{recomendado}")
        print(f"   Valor atual: {config['atual']}")
        print(f"   Valor novo:  {config['novo']}")
        print(f"   Descrição:   {config['descricao']}")
        print()

def modificar_conf_smt(arquivo_smt, modificacoes):
    """Modifica o arquivo Conf.smt"""
    with open(arquivo_smt, 'rb') as f:
        conteudo = f.read()

    conteudo_original = conteudo
    modificacoes_aplicadas = []

    for param, config in modificacoes.items():
        busca = f"{param}={config['atual']}".encode('ascii')
        substitui = f"{param}={config['novo']}".encode('ascii')

        if busca in conteudo:
            conteudo = conteudo.replace(busca, substitui)
            modificacoes_aplicadas.append(param)
            print(f"✓ {param}: {config['atual']} → {config['novo']}")
        else:
            print(f"✗ {param}: não encontrado ou já modificado")

    with open(arquivo_smt, 'wb') as f:
        f.write(conteudo)

    return modificacoes_aplicadas

def modificar_projeto_sup(arquivo_sup, modificacoes_selecionadas):
    """Modifica o arquivo .sup extraindo, modificando e recompactando"""

    # Criar backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = f"{arquivo_sup}.backup_{timestamp}"
    shutil.copy2(arquivo_sup, backup)
    print(f"\n✓ Backup criado: {backup}")

    # Criar diretório temporário
    temp_dir = f"{arquivo_sup}_temp_{timestamp}"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Extrair .sup
        print(f"\n✓ Extraindo {arquivo_sup}...")
        with zipfile.ZipFile(arquivo_sup, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Modificar Conf.smt
        conf_smt = os.path.join(temp_dir, 'Conf.smt')
        if not os.path.exists(conf_smt):
            print(f"✗ Erro: Conf.smt não encontrado em {temp_dir}")
            return False

        print(f"\n✓ Modificando Conf.smt...")
        modificacoes_aplicadas = modificar_conf_smt(conf_smt, modificacoes_selecionadas)

        if not modificacoes_aplicadas:
            print("\n✗ Nenhuma modificação foi aplicada!")
            return False

        # Recompilar .sup
        print(f"\n✓ Recompilando {arquivo_sup}...")
        os.remove(arquivo_sup)

        with zipfile.ZipFile(arquivo_sup, 'w', zipfile.ZIP_DEFLATED) as zip_ref:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zip_ref.write(file_path, arcname)

        print(f"\n✓ Arquivo modificado com sucesso!")
        print(f"\n✓ Modificações aplicadas: {', '.join(modificacoes_aplicadas)}")

        return True

    finally:
        # Limpar diretório temporário
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def main():
    # Arquivo .sup padrão
    arquivo_sup = "/home/lucas-junges/Documents/clientes/w&co/apr03_alterado/apr03_v2_alterado.sup"

    if len(sys.argv) > 1:
        arquivo_sup = sys.argv[1]

    if not os.path.exists(arquivo_sup):
        print(f"✗ Erro: Arquivo {arquivo_sup} não encontrado!")
        sys.exit(1)

    # Listar configurações
    listar_configuracoes()

    # Perguntar quais modificar
    print("="*80)
    print("Digite os números das configurações que deseja modificar (separados por vírgula)")
    print("Exemplo: 1,2,5  ou  1  ou  all (para todas recomendadas)")
    print("="*80)

    escolha = input("\nSua escolha: ").strip().lower()

    modificacoes_selecionadas = {}

    if escolha == 'all':
        modificacoes_selecionadas = {k: v for k, v in CONFIGURACOES_INTERESSANTES.items() if v['recomendado']}
    else:
        try:
            indices = [int(x.strip()) for x in escolha.split(',')]
            params = list(CONFIGURACOES_INTERESSANTES.keys())
            for idx in indices:
                if 1 <= idx <= len(params):
                    param = params[idx - 1]
                    modificacoes_selecionadas[param] = CONFIGURACOES_INTERESSANTES[param]
        except ValueError:
            print("✗ Entrada inválida!")
            sys.exit(1)

    if not modificacoes_selecionadas:
        print("\n✗ Nenhuma configuração selecionada!")
        sys.exit(1)

    print(f"\n{'='*80}")
    print(f"Arquivo: {arquivo_sup}")
    print(f"Modificações a aplicar:")
    for param, config in modificacoes_selecionadas.items():
        print(f"  - {param}: {config['atual']} → {config['novo']}")
    print(f"{'='*80}")

    confirma = input("\nConfirmar modificações? (s/n): ").strip().lower()
    if confirma != 's':
        print("\n✗ Operação cancelada.")
        sys.exit(0)

    # Aplicar modificações
    sucesso = modificar_projeto_sup(arquivo_sup, modificacoes_selecionadas)

    if sucesso:
        print("\n" + "="*80)
        print("✓ SUCESSO! Arquivo modificado com sucesso!")
        print("="*80)
        print("\nPróximos passos:")
        print("1. Abra o arquivo .sup no WinSup 2")
        print("2. Compile o projeto")
        print("3. Transfira para o CLP")
        print("4. Verifique se as novas configurações foram aplicadas")
        print("\nNOTA: Se algo der errado, use o arquivo de backup criado.")
    else:
        print("\n✗ Falha ao modificar o arquivo!")
        sys.exit(1)

if __name__ == "__main__":
    main()
