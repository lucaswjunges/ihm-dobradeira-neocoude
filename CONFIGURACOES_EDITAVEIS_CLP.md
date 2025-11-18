# Configurações Editáveis do CLP ATOS (Bloqueadas no WinSup 2)

Este documento lista todas as configurações que podem ser modificadas manualmente nos arquivos do projeto `.sup`, mas que estão bloqueadas (grayed out) na interface do WinSup 2.

## ⚠️ ATENÇÃO

Modificações incorretas podem causar mal funcionamento do CLP. Sempre faça backup antes de modificar!

---

## 📋 Configurações Disponíveis

### 1. FRONTREMOTO (IHM Remota) ⭐ RECOMENDADO

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita o modo de IHM remota, permitindo que um terminal remoto se conecte ao CLP via RS232/RS485 e opere como interface homem-máquina.

**Por que modificar**:
- Permite conectar tablets/computadores como IHM
- Exatamente o que você precisa para o projeto da dobradeira
- **ESTA É A CONFIGURAÇÃO PRINCIPAL QUE RESOLVE SEU PROBLEMA!**

**Riscos**: Baixo. Se não funcionar, basta desabilitar novamente.

---

### 2. FRONTAL

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita comunicação com painel frontal (HMI física ATOS).

**Por que modificar**:
- Útil se você tiver um painel frontal ATOS conectado
- Pode ser necessário em conjunto com FRONTREMOTO

**Riscos**: Baixo, mas só habilite se tiver hardware compatível.

---

### 3. HMAMI (HMI Master Interface)

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita o modo Master para comunicação com IHM (telas).

**Por que modificar**:
- Pode ser necessário para comunicação avançada com IHM
- Relacionado ao FRONTREMOTO

**Riscos**: Médio. Pode causar conflitos se mal configurado.

---

### 4. FORCE (Modo Force)

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita o modo FORCE, que permite forçar manualmente o estado de entradas e saídas durante debug.

**Por que modificar**:
- **MUITO ÚTIL para testes e comissionamento**
- Permite forçar saídas e entradas para testar lógica
- Essencial durante desenvolvimento

**Riscos**: ⚠️ ALTO! Forçar I/Os em máquina real pode causar acidentes. Use apenas em bancada de testes.

---

### 5. ESCUTA (Modo Monitor/Escuta)

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita modo de monitoramento/escuta, permitindo que o WinSup conecte ao CLP sem interromper a execução.

**Por que modificar**:
- Permite monitorar o CLP em tempo real sem parar a máquina
- Útil para debug online

**Riscos**: Baixo. Apenas monitora, não interfere.

---

### 6. RECFRONTAL (Receitas no Frontal)

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita armazenamento e gerenciamento de receitas (parâmetros pré-configurados) no painel frontal.

**Por que modificar**:
- Útil se você quiser armazenar configurações de dobra como "receitas"
- Pode simplificar operação para usuário final

**Riscos**: Baixo, mas requer estrutura de dados adequada.

---

### 7. HAB_SENHA (Habilitar Senha)

**Arquivo**: `Conf.smt`
**Valor atual**: `0` (desabilitado)
**Valor sugerido**: `1` (habilitado)

**Descrição**: Habilita proteção por senha para acesso ao CLP via WinSup.

**Por que modificar**:
- Segurança: impede modificações não autorizadas
- Proteção contra alterações acidentais

**Nota**: Após habilitar, defina a senha no parâmetro `SENHA=` (linha 194).

**Riscos**: ⚠️ Médio. Se esquecer a senha, você pode ficar bloqueado do CLP!

---

### 8. WATCHDOGTIMER (Timer Watchdog)

**Arquivo**: `Conf.smt`
**Valor atual**: `1` (habilitado)
**Valor sugerido**: `0` (desabilitado) - **NÃO RECOMENDADO**

**Descrição**: Watchdog monitora se o programa está executando corretamente. Se travado por mais de X segundos, reseta o CLP.

**Por que DESABILITAR**:
- Para debug de programas muito lentos
- Durante testes de bancada

**Riscos**: ⚠️⚠️ ALTO! Desabilitar o watchdog remove proteção contra travamento. **NÃO DESABILITE EM PRODUÇÃO!**

---

## 🛠️ Como Modificar

### Opção 1: Script Automático (Recomendado)

```bash
cd /home/lucas-junges/Documents/clientes/w\&co
python3 modificar_config_clp.py
```

O script irá:
1. Fazer backup automático do `.sup`
2. Mostrar todas as opções
3. Pedir confirmação
4. Modificar e reempacotar o arquivo

### Opção 2: Manual

1. Extrair o `.sup`:
   ```bash
   unzip apr03_v2_alterado.sup -d temp_edit/
   ```

2. Editar `temp_edit/Conf.smt` (é um arquivo semi-binário):
   ```bash
   # Use um editor hexadecimal ou sed:
   sed -i 's/FRONTREMOTO=0/FRONTREMOTO=1/g' temp_edit/Conf.smt
   ```

3. Reempacotar:
   ```bash
   cd temp_edit/
   zip ../apr03_v2_alterado_modificado.sup *
   ```

---

## 🎯 Recomendação para Projeto da Dobradeira

Para o seu projeto de IHM web, recomendo habilitar:

1. ✅ **FRONTREMOTO=1** (ESSENCIAL - habilita IHM remota)
2. ✅ **FRONTAL=1** (útil para comunicação)
3. ✅ **ESCUTA=1** (permite monitorar sem parar máquina)
4. ⚠️ **FORCE=1** (apenas para testes de bancada, DESABILITE em produção)

**NÃO habilite**:
- ❌ WATCHDOGTIMER=0 (mantenha segurança)
- ❌ HAB_SENHA=1 (só se você realmente quiser senha)

---

## 📝 Outras Configurações Interessantes no Conf.smt

Além dos parâmetros acima, você pode modificar:

### Comunicação Serial - Canal A (RS232)
```
A_BAUD_APR=6     (Baudrate: 0=1200, 6=57600, 7=115200)
A_PARID_APR=0    (Paridade: 0=None, 1=Even, 2=Odd)
A_BSIZE_APR=1    (Bits de dados: 0=7bits, 1=8bits)
A_STOPB_APR=1    (Stop bits: 0=1bit, 1=2bits)
```

### Comunicação Serial - Canal B (RS485)
```
B_BAUD_MOD=6     (Baudrate para Modbus)
B_PARID_MOD=0    (Paridade para Modbus)
B_BSIZE_MOD=1    (Bits de dados)
B_STOPB_MOD=1    (Stop bits)
```

### Outros
```
BASTIDOR_0=0097  (Endereço do bastidor/rack)
SIMULAANG=1      (Simula ângulos - útil para debug)
INT1=0           (Interrupção 1)
INT2=0           (Interrupção 2)
```

---

## 🔧 Troubleshooting

### O WinSup não reconhece o arquivo modificado
- Verifique se todos os arquivos foram reempacotados corretamente
- Confira se manteve a estrutura ZIP (use `zip`, não `tar`)
- Verifique terminação de linha (CRLF)

### CLP não aceita o programa após modificação
- Restaure o backup
- Habilite apenas 1 parâmetro por vez
- Verifique compatibilidade do firmware do CLP

### Senha esquecida (se habilitar HAB_SENHA)
- Edite Conf.smt e mude `HAB_SENHA=1` de volta para `HAB_SENHA=0`
- Ou limpe a senha: `SENHA=`

---

## 📚 Referências

- Manual ATOS MPC4004, páginas 85-86 (configuração de comunicação)
- Manual ATOS Expert Series, seção "Configuração de Sistema"
- Documentação WinSup 2.0 (limitada quanto a estes parâmetros)

---

**Última atualização**: 2025-11-10
**Autor**: Análise de projeto dobradeira ATOS
