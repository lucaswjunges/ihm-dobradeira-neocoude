# 🔍 COMO ENCONTRAR O TERMINAL COM (COMUM)

## 📍 Onde procurar:

### 1. No módulo da CPU do CLP:
Procure por terminais marcados como:
- **COM** ou **C**
- **COMUM**
- **+24V** ou **24V**
- **0V** ou **GND**
- Pode estar entre os terminais E0-E7

### 2. Aparência típica no borne:
```
┌─────────────────────────────┐
│  COM  E0  E1  E2  E3  E4 ...│  ← Tipo 1: COM antes das entradas
└─────────────────────────────┘

ou

┌─────────────────────────────┐
│  E0  E1  E2  E3  COM  E4 ...│  ← Tipo 2: COM no meio
└─────────────────────────────┘

ou

┌─────────────────────────────┐
│  E0  E1  E2  E3  E4  E5  E6 │
│                              │
│  COM      +24V      0V       │  ← Tipo 3: Embaixo
└─────────────────────────────┘
```

## 🎯 MÉTODO ALTERNATIVO - Usar botão físico existente

Se não achar o COM, podemos usar um **botão que já funciona** na máquina:

### Passo 1: Identificar um botão que funciona
Exemplo: botão **AVANÇAR** ou **RECUAR** da máquina

### Passo 2: Ver onde o botão está conectado
- Um fio vai para alguma entrada (Ex: E4)
- Outro fio vai para o COMUM (esse é o que queremos!)

### Passo 3: Usar o mesmo COMUM
Pegue um fio e conecte:
```
[Fio do COMUM do botão] ──┬─> [Mantém no botão]
                          │
                          └─> [Novo fio para E0]
```

## 🔬 MÉTODO 3 - Verificar LEDs do CLP

Alguns CLPs Atos têm LEDs na frente mostrando status das entradas:

1. Olhe na frente do módulo CPU
2. Procure por LEDs pequenos marcados E0, E1, E2...
3. Aperte um botão físico da máquina (AVANÇAR, RECUAR, etc)
4. Veja qual LED acende → isso confirma que entradas funcionam

## 📸 MÉTODO 4 - Foto

Se tiver dificuldade, tire uma foto clara do borne do CLP e me descreva o que vê escrito nos terminais.

## 🔧 TESTE RÁPIDO - Esquema da instalação

Como a máquina já está funcionando (encoder funciona, botões K1 funcionam), o COM **já está conectado** em algum lugar da instalação elétrica.

Você pode:
1. Pegar um fio jumper
2. Conectar E0 ao terminal de um **botão que já funciona**
3. Ver se E0 ativa quando apertar o botão

Isso confirma se é TIPO N ou TIPO P.

## ❓ Responda:

1. **Você vê LEDs acesos no CLP?** (quando liga a máquina)
2. **Consegue ver os bornes/terminais onde os botões físicos estão conectados?**
3. **Há alguma numeração ou marcação visível nos terminais?**
