#!/bin/bash
# Script de tráfico sintético usando curl.
# Uso: ./generate-traffic.sh [duracion_segundos]
# Ejemplo: ./generate-traffic.sh 300

DURACION=${1:-300}
BASE_URL="http://localhost:3000"
ENDPOINTS=(
  "/"
  "/api/datos"
  "/api/datos"
  "/api/datos"
  "/api/lento"
  "/api/error"
  "/api/error"
  "/api/usuarios/1"
  "/api/usuarios/42"
  "/api/usuarios/150"
)

echo "=> Generando tráfico contra $BASE_URL por $DURACION segundos"
echo "Ctrl+C para detener"

INICIO=$(date +%s)
COUNT=0

while [ $(( $(date +%s) - INICIO )) -lt $DURACION ]; do
  EP=${ENDPOINTS[$RANDOM % ${#ENDPOINTS[@]}]}
  curl -s -o /dev/null -w "%{http_code} $EP\n" "$BASE_URL$EP" &
  COUNT=$((COUNT + 1))
  SLEEP_TIME=$(awk -v min=0.2 -v max=0.6 'BEGIN{srand(); print min+rand()*(max-min)}')
  sleep $SLEEP_TIME
done

wait
echo "=> Total enviados: $COUNT"
