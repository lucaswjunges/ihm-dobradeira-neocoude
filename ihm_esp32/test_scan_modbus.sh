#!/bin/bash
echo "Escaneando Slave IDs de 1 a 10..."
for id in {1..10}; do
    echo -n "Testando Slave ID $id: "
    timeout 2 mbpoll -a $id -b 57600 -P none -s 1 -t 3 -r 1238 -c 1 /dev/ttyUSB0 2>&1 | grep -q "0x" && echo "RESPOSTA!" || echo "timeout/erro"
done
