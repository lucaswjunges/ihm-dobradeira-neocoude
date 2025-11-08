#!/bin/bash
# Script para abrir a IHM no navegador

echo "Abrindo IHM NEOCOUDE-HD-15..."

# Tenta abrir no navegador disponível
if command -v firefox &> /dev/null; then
    firefox index.html &
elif command -v google-chrome &> /dev/null; then
    google-chrome index.html &
elif command -v chromium-browser &> /dev/null; then
    chromium-browser index.html &
else
    echo "Abra manualmente: index.html"
    xdg-open index.html &
fi

echo "IHM iniciada!"
echo "Servidor rodando em: ws://localhost:8080"
