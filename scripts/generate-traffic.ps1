# Script de tráfico sintético para Windows PowerShell.
# Uso: .\generate-traffic.ps1 -Duracion 300

param(
    [int]$Duracion = 300,
    [string]$BaseUrl = "http://localhost:3000"
)

$endpoints = @(
    "/",
    "/api/datos", "/api/datos", "/api/datos",
    "/api/lento",
    "/api/error", "/api/error",
    "/api/usuarios/1",
    "/api/usuarios/42",
    "/api/usuarios/150"
)

Write-Host "=> Generando trafico contra $BaseUrl por $Duracion segundos" -ForegroundColor Cyan
Write-Host "Ctrl+C para detener" -ForegroundColor Yellow

$inicio = Get-Date
$count = 0

while (((Get-Date) - $inicio).TotalSeconds -lt $Duracion) {
    $ep = $endpoints | Get-Random
    $url = "$BaseUrl$ep"
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10 -ErrorAction SilentlyContinue
        $status = $r.StatusCode
    } catch {
        $status = $_.Exception.Response.StatusCode.value__
    }
    $count++
    if ($count % 10 -eq 0) {
        Write-Host "  enviados: $count - $ep -> $status"
    }
    Start-Sleep -Milliseconds (Get-Random -Minimum 200 -Maximum 600)
}

Write-Host "=> Total enviados: $count" -ForegroundColor Green
