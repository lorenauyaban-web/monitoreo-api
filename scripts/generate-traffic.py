"""
Script de tráfico sintético.
Envía requests aleatorios a los diferentes endpoints de la API
para generar métricas observables en Prometheus y Grafana.

Uso:
    python generate-traffic.py
    python generate-traffic.py --duracion 120 --rps 5
"""
import argparse
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor

try:
    import requests
except ImportError:
    print("Falta la dependencia 'requests'. Instala con: pip install requests")
    sys.exit(1)

BASE_URL = "http://localhost:3000"

# Endpoints con pesos (mayor peso = más llamadas)
ENDPOINTS = [
    ("/", 3),
    ("/api/datos", 5),
    ("/api/lento", 1),
    ("/api/error", 2),
    ("/api/usuarios/1", 2),
    ("/api/usuarios/42", 2),
    ("/api/usuarios/150", 1),  # genera 404
]


def hacer_request(endpoint: str):
    url = f"{BASE_URL}{endpoint}"
    try:
        r = requests.get(url, timeout=10)
        return endpoint, r.status_code
    except requests.RequestException as e:
        return endpoint, f"ERROR: {e}"


def main():
    global BASE_URL
    parser = argparse.ArgumentParser(description="Generador de tráfico sintético")
    parser.add_argument("--duracion", type=int, default=300, help="Duración en segundos (default 300)")
    parser.add_argument("--rps", type=float, default=3.0, help="Requests por segundo aprox (default 3)")
    parser.add_argument("--url", type=str, default=BASE_URL, help="URL base de la API")
    args = parser.parse_args()
    BASE_URL = args.url

    intervalo = 1.0 / args.rps if args.rps > 0 else 0.5

    print(f"=> Generando tráfico contra {BASE_URL}")
    print(f"=> Duración: {args.duracion}s | RPS objetivo: {args.rps}")
    print("Ctrl+C para detener\n")

    endpoints = [e for e, w in ENDPOINTS for _ in range(w)]
    inicio = time.time()
    total = 0
    contadores = {}

    with ThreadPoolExecutor(max_workers=10) as pool:
        try:
            while time.time() - inicio < args.duracion:
                ep = random.choice(endpoints)
                future = pool.submit(hacer_request, ep)
                future.add_done_callback(
                    lambda f: _callback(f, contadores)
                )
                total += 1
                if total % 20 == 0:
                    print(f"  enviados: {total} | tiempo: {int(time.time()-inicio)}s")
                time.sleep(intervalo * random.uniform(0.5, 1.5))
        except KeyboardInterrupt:
            print("\n[!] Detenido por el usuario")

    print(f"\n=> Total enviados: {total}")
    print("=> Detalle por endpoint:")
    for ep, codigos in sorted(contadores.items()):
        print(f"   {ep}: {codigos}")


def _callback(future, contadores):
    try:
        ep, status = future.result()
        contadores.setdefault(ep, {}).setdefault(status, 0)
        contadores[ep][status] += 1
    except Exception:
        pass


if __name__ == "__main__":
    main()
