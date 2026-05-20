# Guión del video demostrativo (≤ 5 minutos)

> Lee este guión mientras grabas. Los tiempos son aproximados; practica una vez antes para encajar dentro de los 5 minutos.

---

## (0:00 - 0:30) Introducción

> "Hola, soy **[tu nombre]**, código **[tu código]**, y voy a presentar la actividad de monitoreo y observabilidad de la asignatura Herramientas y visualización de datos.
>
> Construí una API REST en Python con FastAPI que expone 5 endpoints más uno de métricas. La API está instrumentada con la librería oficial de Prometheus, y todo el stack —API, Prometheus y Grafana— corre sobre Docker Compose en una sola red. El objetivo es observar el comportamiento de la API en tiempo real."

---

## (0:30 - 3:30) Demostración técnica

### Paso 1 - Levantar el stack (~20s)

> "Primero levanto los servicios con `docker-compose up -d`."

```bash
docker-compose up -d
docker-compose ps
```

> "Aquí confirmo que los tres contenedores están UP: la API en el puerto 3000, Prometheus en el 9090 y Grafana en el 3001."

### Paso 2 - La API (~30s)

> "Abro la API en `localhost:3000`. Devuelve un JSON con la lista de endpoints disponibles. Llamo a `/api/datos` que es rápido, y luego a `/api/lento`, que demora intencionalmente entre 2 y 3 segundos para simular un endpoint pesado. También tengo `/api/error` que falla con 500 el 30% de las veces, y `/api/usuarios/{id}` que devuelve 404 cuando el id es mayor a 100."

### Paso 3 - Endpoint /metrics (~20s)

> "El endpoint `/metrics` expone todo en formato Prometheus: contadores por endpoint y status, el histograma de duración con sus buckets, el gauge de requests activos, y métricas de CPU y memoria del sistema."

```bash
curl http://localhost:3000/metrics | head -40
```

### Paso 4 - Generar tráfico (~15s)

> "Ahora lanzo el script de tráfico sintético en una terminal aparte. Hace requests aleatorios a todos los endpoints con pesos diferentes."

```bash
python scripts/generate-traffic.py --duracion 300 --rps 5
```

### Paso 5 - Prometheus (~40s)

> "Voy a `localhost:9090`. En **Status > Targets** se ve que `mi-api` está siendo scrapeado correctamente cada 15 segundos. Ejecuto la primera query PromQL:"

```promql
sum by (endpoint) (rate(http_requests_total[1m]))
```

> "Aquí veo los requests por segundo desglosados por endpoint. La segunda query:"

```promql
histogram_quantile(0.95, sum by (le, endpoint) (rate(http_request_duration_seconds_bucket[1m])))
```

> "Esta calcula la latencia p95 y se ve claramente cómo `/api/lento` está cerca de 3 segundos mientras los demás están por debajo de 100 milisegundos."

### Paso 6 - Grafana (~40s)

> "Entro a Grafana en `localhost:3001` con admin / admin. El dashboard llamado **API REST - Monitoreo y Observabilidad** ya está provisionado automáticamente. Tiene seis paneles:
>
> 1. Throughput por endpoint
> 2. Latencia p95 con umbral en 2 segundos
> 3. Requests activos
> 4. Tasa de errores 4xx y 5xx
> 5. CPU y memoria del sistema
> 6. Total acumulado de requests
>
> El dashboard se refresca cada 5 segundos."

---

## (3:30 - 4:30) Análisis

> "Las métricas que estoy monitoreando siguen el método **RED**: Rate, Errors, Duration.
>
> - **Rate:** el panel de throughput muestra que `/api/datos` recibe la mayor parte del tráfico, alrededor de X requests por segundo.
> - **Errors:** la tasa de errores muestra picos de HTTP 500 provenientes de `/api/error` y 404 de `/api/usuarios/150`. Esto es esperado por diseño.
> - **Duration:** el p95 de `/api/lento` se mantiene cerca de 3 segundos, lo que es muy alto.
>
> **Una optimización clara basada en estas métricas:** el endpoint `/api/lento` está saturando workers porque bloquea durante 2 a 3 segundos. Tres acciones podrían reducir esta latencia: (1) convertirlo a `async def` para no bloquear el event loop, (2) cachear el resultado en Redis si los datos lo permiten, o (3) escalar uvicorn con varios workers usando `--workers 4`. Sin estas métricas no podríamos justificar la inversión."

---

## (4:30 - 5:00) Cierre

> "El monitoreo y la observabilidad no son opcionales en producción. Sin métricas operamos a ciegas: no sabemos cuándo un servicio se degrada, ni qué endpoint debemos optimizar. Con el stack Prometheus + Grafana puedo detectar problemas en minutos, dimensionar capacidad con datos reales y demostrar el cumplimiento de SLOs. Gracias."

---

## Lista de verificación antes de grabar

- [ ] `docker-compose down -v` y luego `docker-compose up -d` (start limpio)
- [ ] Esperar 30 segundos antes de empezar a grabar (Grafana tarda en provisionar)
- [ ] Ejecutar el script de tráfico al menos 1 minuto antes de mostrar Grafana
- [ ] Activar la cámara para que aparezcas en el video (lo pide la rúbrica)
- [ ] Audio claro - prueba el micrófono
- [ ] Resolución mínima 1080p
- [ ] No exceder 5 minutos (es estricto)
