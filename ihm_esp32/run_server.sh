#!/bin/bash
# Script para iniciar/parar servidor IHM
# Uso:
#   ./run_server.sh start   - Inicia em background
#   ./run_server.sh stop    - Para o servidor
#   ./run_server.sh status  - Mostra status
#   ./run_server.sh restart - Reinicia servidor
#   ./run_server.sh         - Inicia em foreground (Ctrl+C para parar)

cd "$(dirname "$0")"

case "$1" in
  start)
    echo "=============================================="
    echo "  INICIANDO SERVIDOR IHM EM BACKGROUND"
    echo "=============================================="
    echo ""

    # Mata processos antigos
    pkill -9 -f "python.*main_server" 2>/dev/null
    sleep 2

    # Inicia servidor (versão threaded - não bloqueia event loop)
    python3 -u main_server_threaded.py > ihm.log 2>&1 &
    echo $! > ihm.pid

    sleep 3

    if ps -p $(cat ihm.pid) > /dev/null 2>&1; then
        echo "✅ Servidor iniciado com sucesso!"
        echo ""
        echo "PID: $(cat ihm.pid)"
        echo "IP: $(hostname -I | awk '{print $1}')"
        echo ""
        echo "Acesse: http://$(hostname -I | awk '{print $1}'):8080"
        echo ""
        echo "Para ver logs: tail -f ihm.log"
        echo "Para parar: ./run_server.sh stop"
    else
        echo "✗ Falha ao iniciar servidor"
        echo "Veja os logs: tail ihm.log"
    fi
    ;;

  stop)
    echo "Parando servidor..."
    if [ -f ihm.pid ]; then
        kill $(cat ihm.pid) 2>/dev/null && echo "✅ Servidor parado" || echo "✗ Servidor não estava rodando"
        rm ihm.pid
    else
        pkill -9 -f "python.*main_server" 2>/dev/null && echo "✅ Servidor parado" || echo "✗ Nenhum servidor rodando"
    fi
    ;;

  status)
    ./check_server.sh
    ;;

  restart)
    $0 stop
    sleep 2
    $0 start
    ;;

  *)
    # Modo foreground (padrão)
    echo "=============================================="
    echo "  SERVIDOR IHM - DOBRADEIRA NEOCOUDE"
    echo "=============================================="
    echo ""

    echo "Matando processos antigos..."
    pkill -9 -f "python.*main_server" 2>/dev/null
    sleep 2

    echo "Iniciando servidor..."
    echo ""
    echo "IP do Raspberry Pi: $(hostname -I | awk '{print $1}')"
    echo "Acesse no navegador: http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
    echo "Pressione Ctrl+C para parar"
    echo "=============================================="
    echo ""

    python3 -u main_server_threaded.py
    ;;
esac
