# Monitoreo y Observabilidad - API REST con Prometheus y Grafana

**Asignatura:** Herramientas y visualización de datos
**Actividad:** Monitoreo y observabilidad
**Nombre:** Loreana Uyaban Sanchez 
**Código:** 202210022601

## Descripción

Stack completo de monitoreo sobre una API REST construida con FastAPI. La API expone métricas en formato Prometheus, Prometheus las recolecta cada 15s y Grafana las visualiza en un dashboard provisionado automáticamente.

## Stack

| Servicio   | Puerto host | URL                      |
|------------|-------------|--------------------------|
| API        | 3000        | http://localhost:3000    |
| Prometheus | 9090        | http://localhost:9090    |
| Grafana    | 3001        | http://localhost:3001    |

Usuario Grafana: `admin` / `admin`

## Estructura del proyecto

```
monitoreo-api/
├── docker-compose.yml
├── README.md
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/datasource.yml
│   │   └── dashboards/dashboards.yml
│   └── dashboards/api-dashboard.json
└── scripts/
    ├── generate-traffic.py
    ├── generate-traffic.sh
    └── generate-traffic.ps1
```

## Endpoints de la API

| Método | Ruta                  | Descripción                                 |
|--------|-----------------------|---------------------------------------------|
| GET    | `/`                   | Info de la API                              |
| GET    | `/api/datos`          | Devuelve datos rápidamente                  |
| GET    | `/api/lento`          | Simula procesamiento lento (2-3 s)          |
| GET    | `/api/error`          | Falla aleatoriamente (~30% HTTP 500)        |
| GET    | `/api/usuarios/{id}`  | Devuelve usuario; id > 100 retorna 404      |
| GET    | `/metrics`            | Métricas en formato Prometheus              |

## Métricas expuestas

- `http_requests_total{method, endpoint, status_code}` - Counter
- `http_request_duration_seconds{method, endpoint}` - Histogram (con buckets y `_bucket`, `_sum`, `_count`)
- `http_requests_active` - Gauge
- `http_errors_total{endpoint, status_code}` - Counter
- `system_cpu_usage_percent` - Gauge
- `system_memory_usage_percent` - Gauge

## Cómo ejecutar

Requisitos: Docker y Docker Compose instalados.

```bash
# 1. Levantar el stack
docker-compose up -d

# 2. Verificar que los 3 servicios están UP
docker-compose ps

# 3. Probar la API
curl http://localhost:3000/
curl http://localhost:3000/api/datos
curl http://localhost:3000/metrics
```

Acceder en el navegador:

- API: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin / admin)

El dashboard se llama **"API REST - Monitoreo y Observabilidad"** y aparece provisionado automáticamente.

## Generar tráfico

Elige una opción según tu sistema:

```bash
# Python (multiplataforma)
pip install requests
python scripts/generate-traffic.py --duracion 300 --rps 5

# Bash (Linux/Mac/WSL)
chmod +x scripts/generate-traffic.sh
./scripts/generate-traffic.sh 300

# PowerShell (Windows)
.\scripts\generate-traffic.ps1 -Duracion 300
```

## Queries PromQL útiles para el video

```promql
# 1. Throughput por endpoint (requests por segundo)
sum by (endpoint) (rate(http_requests_total[1m]))

# 2. Latencia p95 por endpoint
histogram_quantile(0.95, sum by (le, endpoint) (rate(http_request_duration_seconds_bucket[1m])))

# 3. Tasa de errores
sum by (status_code) (rate(http_errors_total[1m]))

# 4. Requests activos en este momento
http_requests_active

# 5. Distribución del status code
sum by (status_code) (rate(http_requests_total[5m]))
```

## Paneles del dashboard

1. **Throughput - Requests por segundo (por endpoint)** - timeseries
2. **Latencia p95 (por endpoint)** - timeseries con umbral en 2s
3. **Requests Activos** - stat panel
4. **Tasa de errores (4xx / 5xx)** - timeseries apilado
5. **Sistema - CPU y Memoria** - gauges
6. **Total acumulado de requests por endpoint** - stat horizontal

## Detener y limpiar

```bash
# Detener
docker-compose down

# Detener y borrar volúmenes (datos de Prometheus y Grafana)
docker-compose down -v
```

## Análisis de las métricas (para el video)

Las métricas implementadas siguen el método **RED** (Rate, Errors, Duration):

- **Rate:** `http_requests_total` muestra el volumen de tráfico.
- **Errors:** `http_errors_total` permite calcular SLO de disponibilidad.
- **Duration:** el histograma de latencia permite calcular p95/p99, mejor indicador de experiencia de usuario que el promedio.


