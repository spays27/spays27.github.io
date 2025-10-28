# run_server.ps1
# Detecta Node o Python y arranca el servidor de ejemplo (server.js / server.py)
# Uso: Ejecutar en PowerShell desde la carpeta del proyecto

Param(
    [int]$Port = 3000
)

function Info($msg){ Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Err($msg){ Write-Host "[ERROR] $msg" -ForegroundColor Red }

Push-Location $PSScriptRoot

$node = Get-Command node -ErrorAction SilentlyContinue
$python = Get-Command python -ErrorAction SilentlyContinue

if($node){
    Info "Node detectado: ejecutando server.js con Node."
    if(Test-Path "server.js"){
        Info "Arrancando: node server.js"
        node server.js
    } else {
        Err "No se encontró server.js en el directorio. Asegúrate de que el archivo existe."
    }
    Pop-Location
    exit
}

if($python){
    Info "Python detectado: ejecutando server.py con Flask (si existe)."
    if(Test-Path "server.py"){
        Info "Arrancando: python server.py"
        python server.py
    } else {
        Err "No se encontró server.py en el directorio. Asegúrate de que el archivo existe."
    }
    Pop-Location
    exit
}

# Si llegamos aquí, ninguno está instalado
Err "Ni Node ni Python detectados en el sistema."
Write-Host "Instrucciones rápidas para Windows:" -ForegroundColor Yellow
Write-Host "1) Instalar Node.js desde https://nodejs.org/ (LTS)." -ForegroundColor White
Write-Host "   Después de instalar, abre PowerShell en esta carpeta y ejecuta: node server.js" -ForegroundColor White
Write-Host "2) O instalar Python desde https://www.python.org/ y luego: python server.py" -ForegroundColor White
Write-Host "Si quieres que genere comandos exactos para tu sistema, dime y te los preparo." -ForegroundColor Green

Pop-Location
