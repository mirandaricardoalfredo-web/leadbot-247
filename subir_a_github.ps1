param (
    [string]$RepoUrl = ""
)

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "     DESPLEGANDO ROBOT A LA NUBE DE GITHUB ACTIONS 24/7   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green

# Inicializar Git si no existe
if (!(Test-Path ".git")) {
    Write-Host "[*] Inicializando repositorio Git local..." -ForegroundColor Cyan
    git init
}

# Configurar identidad basica si no existe
$gitUser = git config user.name
if (-not $gitUser) {
    git config user.name "Ricardo Miranda"
    git config user.email "mirandaricardoalfredo@gmail.com"
}

git add .
git commit -m "Despliegue inicial de Supercomputadora LeadBot 24/7"

if ($RepoUrl -eq "") {
    Write-Host ""
    Write-Host "[!] Por favor pega la URL de tu repositorio nuevo de GitHub:" -ForegroundColor Yellow
    Write-Host "    (Ejemplo: https://github.com/TU_USUARIO/supercloud-leadbot.git)" -ForegroundColor DarkGray
    $RepoUrl = Read-Host "URL del Repositorio"
}

if ($RepoUrl -ne "") {
    git branch -M main
    git remote remove origin 2>$null
    git remote add origin $RepoUrl
    Write-Host "[*] Subiendo robot a los servidores de GitHub..." -ForegroundColor Cyan
    git push -u origin main -f
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host " [!] ROBOT DESPLEGADO CON ÉXITO EN LA NUBE DE MICROSOFT    " -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Green
    Write-Host "Ahora el robot se ejecutara automaticamente todas las noches" -ForegroundColor Yellow
    Write-Host "incluso si tu computadora esta 100% apagada." -ForegroundColor Yellow
}
