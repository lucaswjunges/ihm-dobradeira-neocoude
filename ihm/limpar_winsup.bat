@echo off
chcp 65001 >nul 2>&1
echo ╔═══════════════════════════════════════════════════════════════╗
echo ║        LIMPEZA DE CACHE DO WINSUP 2 - v1.0                   ║
echo ║        Data: 12/11/2025                                       ║
echo ╚═══════════════════════════════════════════════════════════════╝
echo.

REM ═══════════════════════════════════════════════════════════════
REM Verificar se está rodando como Administrador
REM ═══════════════════════════════════════════════════════════════
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo.
    echo ┌───────────────────────────────────────────────────────────┐
    echo │ ❌ ERRO: Este script precisa de privilégios de Admin     │
    echo └───────────────────────────────────────────────────────────┘
    echo.
    echo Como executar corretamente:
    echo 1. Clique com botão direito neste arquivo
    echo 2. Selecione "Executar como Administrador"
    echo 3. Confirme no UAC ^(controle de conta de usuário^)
    echo.
    pause
    exit /b 1
)

echo.
echo ✓ Privilégios de Administrador confirmados
echo.
echo ═══════════════════════════════════════════════════════════════
echo   INICIANDO LIMPEZA...
echo ═══════════════════════════════════════════════════════════════
echo.

REM ═══════════════════════════════════════════════════════════════
REM Passo 1: Fechar WinSUP completamente
REM ═══════════════════════════════════════════════════════════════
echo [Passo 1/6] Fechando processos do WinSUP...
taskkill /F /IM WinSUP.exe /T >nul 2>&1
if %errorLevel% equ 0 (
    echo   → WinSUP.exe fechado
) else (
    echo   → WinSUP.exe não estava rodando
)

taskkill /F /IM winsup2.exe /T >nul 2>&1
if %errorLevel% equ 0 (
    echo   → winsup2.exe fechado
) else (
    echo   → winsup2.exe não estava rodando
)

taskkill /F /IM winsup3.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul
echo   ✓ Processos verificados
echo.

REM ═══════════════════════════════════════════════════════════════
REM Passo 2: Deletar cache do usuário
REM ═══════════════════════════════════════════════════════════════
echo [Passo 2/6] Deletando cache do usuário...
set deleted_count=0

if exist "%LOCALAPPDATA%\WinSUP\" (
    del /F /S /Q "%LOCALAPPDATA%\WinSUP\*" >nul 2>&1
    echo   → %LOCALAPPDATA%\WinSUP\
    set /a deleted_count+=1
)

if exist "%APPDATA%\WinSUP\" (
    del /F /S /Q "%APPDATA%\WinSUP\*" >nul 2>&1
    echo   → %APPDATA%\WinSUP\
    set /a deleted_count+=1
)

if %deleted_count% equ 0 (
    echo   → Nenhum cache de usuário encontrado
) else (
    echo   ✓ Cache de usuário limpo
)
echo.

REM ═══════════════════════════════════════════════════════════════
REM Passo 3: Deletar arquivos temporários
REM ═══════════════════════════════════════════════════════════════
echo [Passo 3/6] Deletando arquivos temporários...
set temp_count=0

del /F /S /Q "%TEMP%\WinSUP*" >nul 2>&1
if %errorLevel% equ 0 (
    echo   → %TEMP%\WinSUP*
    set /a temp_count+=1
)

if exist "C:\Temp\" (
    del /F /S /Q "C:\Temp\WinSUP*" >nul 2>&1
    if %errorLevel% equ 0 (
        echo   → C:\Temp\WinSUP*
        set /a temp_count+=1
    )
)

if %temp_count% equ 0 (
    echo   → Nenhum arquivo temporário encontrado
) else (
    echo   ✓ Arquivos temporários limpos
)
echo.

REM ═══════════════════════════════════════════════════════════════
REM Passo 4: Deletar cache do programa
REM ═══════════════════════════════════════════════════════════════
echo [Passo 4/6] Deletando cache do programa...
if exist "C:\ProgramData\WinSUP\cache\" (
    del /F /S /Q "C:\ProgramData\WinSUP\cache\*" >nul 2>&1
    echo   → C:\ProgramData\WinSUP\cache\
    echo   ✓ Cache do programa limpo
) else (
    echo   → Nenhum cache de programa encontrado
)
echo.

REM ═══════════════════════════════════════════════════════════════
REM Passo 5: Limpar registro do Windows
REM ═══════════════════════════════════════════════════════════════
echo [Passo 5/6] Limpando registro do Windows...
set reg_count=0

reg delete "HKCU\Software\WinSUP\RecentFiles" /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   → HKCU\Software\WinSUP\RecentFiles
    set /a reg_count+=1
)

reg delete "HKCU\Software\WinSUP\Cache" /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   → HKCU\Software\WinSUP\Cache
    set /a reg_count+=1
)

reg delete "HKCU\Software\WinSUP\RecentProjects" /f >nul 2>&1
if %errorLevel% equ 0 (
    echo   → HKCU\Software\WinSUP\RecentProjects
    set /a reg_count+=1
)

if %reg_count% equ 0 (
    echo   → Nenhuma entrada de registro encontrada
) else (
    echo   ✓ Registro limpo ^(%reg_count% entradas^)
)
echo.

REM ═══════════════════════════════════════════════════════════════
REM Passo 6: Criar diretório limpo para testes
REM ═══════════════════════════════════════════════════════════════
echo [Passo 6/6] Criando diretório limpo...
if not exist "C:\Projetos_CLP\" (
    mkdir "C:\Projetos_CLP\" >nul 2>&1
    echo   → C:\Projetos_CLP\ criado
) else (
    echo   → C:\Projetos_CLP\ já existe
)
echo   ✓ Diretório pronto
echo.

REM ═══════════════════════════════════════════════════════════════
REM Resumo Final
REM ═══════════════════════════════════════════════════════════════
echo.
echo ═══════════════════════════════════════════════════════════════
echo   ✓ LIMPEZA CONCLUÍDA COM SUCESSO!
echo ═══════════════════════════════════════════════════════════════
echo.
echo PRÓXIMOS PASSOS:
echo.
echo 1. REINICIE O COMPUTADOR (importante!)
echo    - Pressione Windows + R
echo    - Digite: shutdown /r /t 0
echo    - Ou: Iniciar ^> Reiniciar
echo.
echo 2. Após reiniciar, copie o arquivo .sup para:
echo    C:\Projetos_CLP\
echo.
echo 3. Abra o WinSUP como Administrador:
echo    - Botão direito no ícone do WinSUP
echo    - "Executar como Administrador"
echo.
echo 4. Tente abrir o arquivo:
echo    - Arquivo ^> Abrir Projeto
echo    - Navegue até C:\Projetos_CLP\
echo    - Selecione o arquivo .sup
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
echo IMPORTANTE: Se o problema persistir após reiniciar:
echo - Leia o arquivo: SOLUCAO_DEFINITIVA_WINSUP.md
echo - Considere reinstalar o WinSUP 2
echo.
echo ═══════════════════════════════════════════════════════════════
echo.
pause
