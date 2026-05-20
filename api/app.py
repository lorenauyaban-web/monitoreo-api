"""
API REST instrumentada con métricas Prometheus.
Actividad: Monitoreo y observabilidad
"""
import os
import time
import random
import psutil
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

app = FastAPI(
    title="API de Monitoreo",
    description="API REST con métricas expuestas en formato Prometheus",
    version="1.0.0",
)

# ---------- Métricas Prometheus ----------
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Número total de requests HTTP",
    ["method", "endpoint", "status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Latencia de los requests HTTP en segundos",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Número de requests actualmente en proceso",
)

ERRORS_TOTAL = Counter(
    "http_errors_total",
    "Número total de respuestas con error (>=400)",
    ["endpoint", "status_code"],
)

CPU_USAGE = Gauge("system_cpu_usage_percent", "Uso de CPU del sistema en porcentaje")
MEMORY_USAGE = Gauge("system_memory_usage_percent", "Uso de memoria del sistema en porcentaje")


# ---------- Middleware: instrumenta todas las rutas excepto /metrics ----------
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    endpoint = request.url.path

    # No instrumentar el propio endpoint de métricas
    if endpoint == "/metrics":
        return await call_next(request)

    ACTIVE_REQUESTS.inc()
    start_time = time.time()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration = time.time() - start_time
        REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(duration)
        REQUEST_COUNT.labels(
            method=request.method, endpoint=endpoint, status_code=str(status_code)
        ).inc()
        if status_code >= 400:
            ERRORS_TOTAL.labels(endpoint=endpoint, status_code=str(status_code)).inc()
        ACTIVE_REQUESTS.dec()


# ---------- Endpoints ----------
@app.get("/")
def root():
    """Endpoint principal: información de la API."""
    return {
        "servicio": "API de Monitoreo",
        "version": "1.0.0",
        "endpoints": [
            "GET /",
            "GET /api/datos",
            "GET /api/lento",
            "GET /api/error",
            "GET /api/usuarios/{id}",
            "GET /metrics",
        ],
    }


@app.get("/api/datos")
def datos():
    """Retorna datos rápidamente (simulación de query ligera)."""
    return {
        "total": 3,
        "items": [
            {"id": 1, "nombre": "Producto A", "precio": 100},
            {"id": 2, "nombre": "Producto B", "precio": 250},
            {"id": 3, "nombre": "Producto C", "precio": 75},
        ],
    }


@app.get("/api/lento")
def lento():
    """Simula un procesamiento lento (2-3 segundos)."""
    delay = random.uniform(2.0, 3.0)
    time.sleep(delay)
    return {"mensaje": "Operación lenta completada", "duracion_segundos": round(delay, 2)}


@app.get("/api/error")
def error_aleatorio():
    """Simula errores aleatorios (30% de probabilidad de 500)."""
    if random.random() < 0.3:
        raise HTTPException(status_code=500, detail="Error simulado del servidor")
    return {"mensaje": "ok"}


@app.get("/api/usuarios/{user_id}")
def usuario(user_id: int):
    """Retorna información de un usuario. 404 si id > 100."""
    if user_id > 100:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    time.sleep(random.uniform(0.05, 0.3))
    return {"id": user_id, "nombre": f"Usuario {user_id}", "activo": True}


@app.get("/metrics")
def metrics():
    """Expone métricas en formato Prometheus."""
    # Actualizar métricas del sistema antes de exponerlas
    CPU_USAGE.set(psutil.cpu_percent(interval=None))
    MEMORY_USAGE.set(psutil.virtual_memory().percent)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "3000"))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
