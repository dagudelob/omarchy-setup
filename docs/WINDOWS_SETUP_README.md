# Guía de Configuración, Respaldo y Flujo Git en Windows (`windows-setup`)

Esta guía documenta la arquitectura, el flujo de trabajo y las instrucciones paso a paso para replicar exactamente el entorno de automatización, versionado de dotfiles/configuraciones y registro de soluciones por ramas en **Windows** (usando PowerShell y Git), tal y como lo hemos venido trabajando en Omarchy / Arch Linux.

---

## 1. Visión General del Flujo de Trabajo

El sistema se basa en 3 pilares clave:
1. **Repositorio privado en GitHub** (ej. `github.com/dagudelob/windows-setup`):
   - Almacena scripts de respaldo (`Backup-Windows.ps1`), scripts de restauración (`Restore-Windows.ps1`), listados de paquetes (`winget-packages.json`, etc.) y dotfiles de herramientas modernas en Windows.
2. **Flujo por Ramas y "Tema Cerrado" / "Tema Solucionado"**:
   - Cada ajuste, corrección de bug (`fix/*`) o nueva característica/personalización (`feature/*`) se trabaja o documenta en su propia rama dedicada.
   - Cuando le indicas al asistente frases como:
     - *"este tema quedó solucionado"*, *"tema cerrado"*, *"tema solucionado"*, *"quedó solucionado"*, *"issue resolved"*, *"guardar solución"*
   - El asistente (o los scripts auxiliares) compila un reporte técnico conciso en Markdown dentro de `docs/resolutions/`, ejecuta un escaneo de seguridad anti-secretos, sube la rama a GitHub (`git push -u origin <rama>`), regresa a `main`, actualiza un catálogo maestro (`RESOLUTIONS.md`) con el enlace directo en Markdown y sube `main` a GitHub.
3. **Respaldo Rápido de Configuraciones (`Backup-Windows.ps1 -Push`)**:
   - Cuando pides *"guarda los cambios"*, *"haz un backup"* o *"sube a github"*, se respalda todo el estado actual y se sube directamente a `main`.

---

## 2. Estructura Recomendada del Repositorio (`windows-setup`)

```text
windows-setup/
├── .agents/
│   └── skills/
│       ├── windows-branch-logger/
│       │   └── SKILL.md          <-- Habilidad para el agente al decir "tema cerrado"
│       └── windows-backup/
│           └── SKILL.md          <-- Habilidad para el respaldo automático
├── config/
│   ├── WindowsTerminal/          <-- settings.json de Windows Terminal
│   ├── PowerShell/               <-- $PROFILE (Microsoft.PowerShell_profile.ps1)
│   ├── GlazeWM/ / komorebi/      <-- Si usas Tiling Window Manager en Windows
│   ├── starship.toml             <-- Prompt Starship (si aplica)
│   ├── fastfetch/ / btop/        <-- Herramientas CLI equivalentes
│   └── AutoHotkey/               <-- Remapeos y atajos de teclado (.ahk)
├── docs/
│   └── resolutions/              <-- Documentación de cada fix/feature por fecha
│       └── YYYY-MM-DD-<slug>.md
├── scripts/
│   ├── Log-Solution.ps1          <-- Script para inicializar rama y plantilla
│   └── Publish-Solution.ps1      <-- Script para escanear secretos, commitear y pushear
├── Backup-Windows.ps1            <-- Script de respaldo general de configs y paquetes
├── Restore-Windows.ps1           <-- Script para restaurar todo en una máquina nueva
├── winget-packages.json          <-- Export de paquetes instalados vía WinGet
├── RESOLUTIONS.md                <-- Catálogo maestro de temas resueltos
├── README.md                     <-- Documentación principal
└── .gitignore                    <-- Exclusión estricta de credenciales y temporales
```

---

## 3. Preparación Inicial en Windows

### Paso 1: Crear el repositorio privado en GitHub
1. Abre tu terminal de PowerShell o la web de GitHub y crea un repositorio **privado** llamado `windows-setup`:
   ```powershell
   gh repo create dagudelob/windows-setup --private --clone
   cd windows-setup
   ```
   *(O créalo en github.com y haz `git clone https://github.com/dagudelob/windows-setup.git`)*

### Paso 2: Crear el `.gitignore` de seguridad
Crea el archivo `.gitignore` para garantizar que nunca se suban credenciales:
```gitignore
# Credenciales y claves
*.key
*.pem
*.pfx
*.token
*.secret
.env*
id_rsa*
id_ed25519*

# Caches y logs de Windows
*.log
*.tmp
*.bak
AppData/Local/Temp/

# Historiales y tokens
*history*
```

---

## 4. Scripts de Automatización (PowerShell)

### A. Script para inicializar rama: `scripts/Log-Solution.ps1`
Este script replica a `log-solution.sh`. Crea o se cambia a la rama adecuada y genera la plantilla del reporte.

```powershell
<#
.SYNOPSIS
    Inicializa una rama de solución o feature en Windows.
.EXAMPLE
    .\scripts\Log-Solution.ps1 -Type fix -Slug "terminal-nerd-fonts" -Title "Configuración de fuentes Nerd Font en Windows Terminal"
#>
param (
    [ValidateSet("fix", "feature", "chore")]
    [string]$Type = "fix",
    
    [Parameter(Mandatory=$true)]
    [string]$Slug,
    
    [string]$Title = ""
)

$ErrorActionPreference = "Stop"
$RepoDir = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $RepoDir

$BranchName = "$Type/$Slug"
$DateStr = Get-Date -Format "yyyy-MM-dd"
$DocDir = Join-Path $RepoDir "docs\resolutions"
$DocFile = Join-Path $DocDir "$DateStr-$Slug.md"

if (-not (Test-Path $DocDir)) {
    New-Item -ItemType Directory -Path $DocDir -Force | Out-Null
}

Write-Host "==> 1. Asegurando que main esté al día..." -ForegroundColor Cyan
git checkout main
git pull origin main 2>$null

Write-Host "==> 2. Creando o cambiando a la rama $BranchName..." -ForegroundColor Cyan
$existingBranch = git branch --list $BranchName
if ($existingBranch) {
    git checkout $BranchName
} else {
    git checkout -b $BranchName
}

if (-not (Test-Path $DocFile)) {
    Write-Host "==> 3. Creando plantilla Markdown en $DocFile..." -ForegroundColor Cyan
    $DocContent = @"
# $($Title ? $Title : $Slug)

- **Fecha:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
- **Rama:** `$BranchName`
- **Tipo:** `$Type`

---

## 1. Problema / Requerimiento
<!-- Resumen ejecutivo de 2-3 líneas sobre el problema o la necesidad -->

## 2. Causa Raíz
<!-- Explicación técnica breve de por qué ocurría -->

## 3. Solución Aplicada
<!-- Pasos concretos, comandos de PowerShell ejecutados y configuraciones modificadas -->

## 4. Archivos Modificados
<!-- Rutas de archivos creados o editados -->

## 5. Validación
<!-- Cómo se comprobó que todo funciona correctamente -->
"@
    Set-Content -Path $DocFile -Value $DocContent -Encoding UTF8
    Write-Host "✔ Plantilla creada: $DocFile" -ForegroundColor Green
}

Write-Host "✔ Rama activa: $BranchName" -ForegroundColor Green
Write-Host "Puedes proceder a editar el archivo: $DocFile"
```

---

### B. Script para publicar la solución: `scripts/Publish-Solution.ps1`
Este script se ejecuta cuando dices **"tema cerrado"** o **"tema solucionado"**. Realiza el escaneo de seguridad, sube la rama a GitHub, actualiza el índice general `RESOLUTIONS.md` en `main` y sube `main`.

```powershell
<#
.SYNOPSIS
    Escanea secretos, commitea, pushea la rama y cataloga en RESOLUTIONS.md sobre main.
.EXAMPLE
    .\scripts\Publish-Solution.ps1 -CommitMessage "docs: registrar solución de fuentes en terminal"
#>
param (
    [string]$CommitMessage = ""
)

$ErrorActionPreference = "Stop"
$RepoDir = (Get-Item $PSScriptRoot).Parent.FullName
Set-Location $RepoDir

$CurrentBranch = (git rev-parse --abbrev-ref HEAD).Trim()

if ($CurrentBranch -eq "main") {
    Write-Error "❌ Error: Te encuentras en la rama 'main'. Debes estar en la rama de la solución/feature para publicarla."
}

if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    $CommitMessage = "docs: registrar solución para $CurrentBranch"
}

Write-Host "==> 1. Escaneo de seguridad anti-secretos..." -ForegroundColor Cyan
git add .

# Escaneo regex de tokens y llaves privadas
$diff = git diff --cached -- . ':!scripts/*' 2>$null
$secretPattern = "(ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|BEGIN.*PRIVATE KEY)"

if ($diff -match $secretPattern) {
    Write-Host "❌ ERROR DE SEGURIDAD: Posibles credenciales/tokens detectados en staged files." -ForegroundColor Red
    Write-Error "Operación abortada para proteger tu seguridad."
}

Write-Host "==> 2. Creando commit en rama $CurrentBranch..." -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    git commit -m "$CommitMessage"
} else {
    Write-Host "ℹ No hay cambios pendientes por commitear." -ForegroundColor Yellow
}

Write-Host "==> 3. Subiendo rama $CurrentBranch a GitHub..." -ForegroundColor Cyan
git push -u origin $CurrentBranch

Write-Host ""
Write-Host "==> 4. Actualizando catálogo de soluciones en rama main..." -ForegroundColor Cyan

# Obtener slug y título del documento Markdown
$Slug = $CurrentBranch -replace "^[^/]+/", ""
$DocFiles = Get-ChildItem -Path "$RepoDir\docs\resolutions" -Filter "*$Slug*.md" -ErrorAction SilentlyContinue
$DocTitle = $CurrentBranch

if ($DocFiles.Count -gt 0) {
    $FirstLine = (Get-Content $DocFiles[0].FullName -TotalCount 1)
    if ($FirstLine -match "^#\s*(.+)$") {
        $DocTitle = $matches[1].Trim()
    }
}

git checkout main
git pull origin main 2>$null

$IndexFile = Join-Path $RepoDir "RESOLUTIONS.md"
if (-not (Test-Path $IndexFile)) {
    $Header = @"
# Catálogo de Soluciones y Configuraciones (Windows)

Registro organizado de incidencias resueltas, optimizaciones y herramientas configuradas con sus ramas dedicadas en GitHub.

| Fecha | Tipo | Título / Asunto | Rama en GitHub |
|---|---|---|---|
"@
    Set-Content -Path $IndexFile -Value $Header -Encoding UTF8
}

$DateNow = Get-Date -Format "yyyy-MM-dd"
$TypePrefix = ($CurrentBranch -split "/")[0]
$RemoteUrl = (git config --get remote.origin.url) -replace "\.git$", ""
$BranchLink = "[$CurrentBranch]($RemoteUrl/tree/$CurrentBranch)"

$CatalogContent = Get-Content -Path $IndexFile -Raw
if (-not ($CatalogContent -match [regex]::Escape($CurrentBranch))) {
    $NewRow = "| $DateNow | ``$TypePrefix`` | $DocTitle | $BranchLink |"
    Add-Content -Path $IndexFile -Value $NewRow -Encoding UTF8
    
    git add $IndexFile
    git commit -m "docs: registrar $CurrentBranch en catálogo de resoluciones"
    git push origin main
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " ✔ Solución registrada y publicada con éxito!" -ForegroundColor Green
Write-Host " Rama en GitHub: $RemoteUrl/tree/$CurrentBranch" -ForegroundColor Cyan
Write-Host " Catálogo en main: $RemoteUrl/blob/main/RESOLUTIONS.md" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Green
```

---

### C. Script de Respaldo General: `Backup-Windows.ps1`
Exporta los paquetes de `winget`, copia los archivos de configuración desde `$env:USERPROFILE` / `$env:APPDATA` / `$env:LOCALAPPDATA`, audita secretos y sube directamente a `main`.

```powershell
<#
.SYNOPSIS
    Respalda las configuraciones de Windows y lista de paquetes instalados.
.EXAMPLE
    .\Backup-Windows.ps1 -Push
#>
param (
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$RepoDir = $PSScriptRoot
Set-Location $RepoDir

$ConfigDir = Join-Path $RepoDir "config"
New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null

Write-Host "==> 1. Exportando lista de paquetes WinGet..." -ForegroundColor Cyan
if (Get-Command winget -ErrorAction SilentlyContinue) {
    winget export -o (Join-Path $RepoDir "winget-packages.json") --accept-source-agreements --include-versions 2>$null
}

Write-Host "==> 2. Respaldando configuraciones de usuario..." -ForegroundColor Cyan

# 2.1 Perfil de PowerShell
$PSProfilePath = $PROFILE
if (Test-Path $PSProfilePath) {
    $DestPS = Join-Path $ConfigDir "PowerShell"
    New-Item -ItemType Directory -Path $DestPS -Force | Out-Null
    Copy-Item $PSProfilePath (Join-Path $DestPS "Microsoft.PowerShell_profile.ps1") -Force
    Write-Host "   -> Perfil PowerShell respaldado"
}

# 2.2 Windows Terminal
$WTerminalPath = "$env:LOCALAPPDATA\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json"
if (Test-Path $WTerminalPath) {
    $DestWT = Join-Path $ConfigDir "WindowsTerminal"
    New-Item -ItemType Directory -Path $DestWT -Force | Out-Null
    Copy-Item $WTerminalPath (Join-Path $DestWT "settings.json") -Force
    Write-Host "   -> Windows Terminal respaldado"
}

# 2.3 Starship Prompt
$StarshipPath = "$env:USERPROFILE\.config\starship.toml"
if (Test-Path $StarshipPath) {
    Copy-Item $StarshipPath (Join-Path $ConfigDir "starship.toml") -Force
    Write-Host "   -> starship.toml respaldado"
}

# 2.4 GlazeWM / Komorebi (si aplica)
$GlazeWMPath = "$env:USERPROFILE\.glzr"
if (Test-Path $GlazeWMPath) {
    $DestGWM = Join-Path $ConfigDir "glzr"
    Copy-Item $GlazeWMPath $DestGWM -Recurse -Force
    Write-Host "   -> GlazeWM respaldado"
}

# 2.5 Gitconfig global (sanitizado)
$GitConfigPath = "$env:USERPROFILE\.gitconfig"
if (Test-Path $GitConfigPath) {
    Copy-Item $GitConfigPath (Join-Path $ConfigDir ".gitconfig") -Force
    Write-Host "   -> .gitconfig respaldado"
}

Write-Host "==> 3. Verificación de seguridad..." -ForegroundColor Cyan
git add .
$diff = git diff --cached -- . ':!Backup-Windows.ps1' 2>$null
$secretPattern = "(ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|BEGIN.*PRIVATE KEY)"

if ($diff -match $secretPattern) {
    Write-Host "❌ ERROR DE SEGURIDAD: Secretos detectados. Abortando respaldo." -ForegroundColor Red
    exit 1
}

Write-Host "==> 4. Commiteando cambios locales..." -ForegroundColor Cyan
$status = git status --porcelain
if ($status) {
    git commit -m "Backup Windows: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "✔ Cambios guardados localmente." -ForegroundColor Green
} else {
    Write-Host "ℹ No hay cambios nuevos." -ForegroundColor Yellow
}

if ($Push) {
    Write-Host "==> 5. Subiendo a GitHub..." -ForegroundColor Cyan
    git push origin main
    Write-Host "✔ Subida completada exitosamente a GitHub." -ForegroundColor Green
}
```

---

## 5. Instrucciones para el Asistente AI (Skill Prompt / Custom Instructions)

Para que el asistente de IA (Antigravity, Claude, ChatGPT, etc.) en Windows se comporte **exactamente igual** a como lo hace en Linux:

Crea un archivo de regla o Skill en `.agents/skills/windows-branch-logger/SKILL.md`:

```markdown
---
name: windows-branch-logger
description: >-
  Crea una rama dedicada en Git y un registro Markdown en GitHub para cada problema resuelto o nueva configuración en Windows.
  DISPARADOR PRINCIPAL: Se activa inmediatamente cuando el usuario dice "este tema quedó solucionado", "tema cerrado", "tema solucionado", "quedó solucionado", "issue resolved", o solicita registrar la solución en una rama.
---

# Windows Branch Logger Skill

## Disparadores Principales
Activa este flujo inmediatamente cuando el usuario diga:
- "este tema quedó solucionado" / "tema cerrado" / "tema solucionado" / "quedó solucionado"
- "guardar solución" / "crear rama para esta solución" / "issue resolved"

## Procedimiento Automatizado del Agente:

1. **Identificar el tema y slug:**
   - Define si es `fix/` (error, bug, ajuste) o `feature/` (nueva herramienta, script, personalización).
   - Crea un slug descriptivo en kebab-case (ej. `fix/powershell-utf8-encoding`, `feature/glazewm-keybindings`).

2. **Crear y cambiar a la rama:**
   - Ejecuta:
     ```powershell
     .\scripts\Log-Solution.ps1 -Type <fix|feature> -Slug "<slug>" -Title "<Título descriptivo>"
     ```

3. **Escribir el Resumen Ejecutivo en Markdown:**
   - Completa el archivo generado en `docs/resolutions/YYYY-MM-DD-<slug>.md` con:
     1. Problema / Requerimiento (2-3 líneas).
     2. Causa Raíz (1-2 líneas técnicas).
     3. Solución Aplicada (comandos PowerShell exactos y archivos tocados).
     4. Archivos Modificados.
     5. Validación (cómo se comprobó).

4. **Publicación y Catalogación:**
   - Ejecuta:
     ```powershell
     .\scripts\Publish-Solution.ps1 -CommitMessage "docs: registrar solucion para <slug>"
     ```

5. **Respuesta al Usuario:**
   - Enlace directo a la rama en GitHub (`https://github.com/dagudelob/windows-setup/tree/<rama>`).
   - Breve resumen de 3 líneas del tema resuelto.
   - Enlace al catálogo maestro `RESOLUTIONS.md`.
```

---

## 6. Equivalencias Clave entre Omarchy (Linux) y Windows

| Componente en Omarchy (Linux) | Equivalente / Opción en Windows |
|---|---|
| **Gestor de Paquetes** | `pacman` / `yay` $\rightarrow$ `winget` (Windows Package Manager) / `scoop` |
| **Shell Principal** | `bash` / `zsh` $\rightarrow$ `PowerShell 7 (pwsh)` |
| **Prompt** | Starship / Oh My Posh $\rightarrow$ Starship o `oh-my-posh` en PowerShell |
| **Terminal** | Kitty / Foot / Ghostty $\rightarrow$ **Windows Terminal** o Ghostty / WezTerm |
| **Ventanas / Tiling WM** | Hyprland $\rightarrow$ **GlazeWM** o **Komorebi** |
| **Atajos de Teclado del Sistema** | `hyprland.conf` $\rightarrow$ **AutoHotkey (v2)** o GlazeWM config |
| **Scripts de Automatización** | Bash (`.sh`) $\rightarrow$ **PowerShell (`.ps1`)** |
| **Ubicación de Dotfiles** | `~/.config/<app>` $\rightarrow$ `$env:USERPROFILE\.config\` o `$env:LOCALAPPDATA\` |
| **Editor Predeterminado** | Antigravity IDE / VS Code $\rightarrow$ Antigravity IDE / VS Code en Windows |

---

## 7. Resumen de Comandos del Día a Día

- **Guardar todo el entorno actual en GitHub (`main`):**
  - Solo dile al asistente: *"haz un respaldo y súbelo a github"*
  - O ejecuta manualmente: `.\Backup-Windows.ps1 -Push`
- **Cerrar un tema resuelto y generar su rama:**
  - Solo dile al asistente: *"este tema quedó solucionado"* o *"tema cerrado"*
  - El asistente creará la rama, redactará el archivo `docs/resolutions/*.md`, la subirá a GitHub y actualizará la tabla `RESOLUTIONS.md` en `main`.
