# Configuración de Zona Horaria Toronto (America/Toronto)

- **Fecha:** 2026-10-09
- **Rama:** `fix/timezone-toronto`
- **Tipo:** `fix`

---

## 1. Inconveniente / Requerimiento
El sistema mostraba una hora incorrecta al estar configurado por defecto en tiempo universal coordinado (`UTC`), en lugar de la hora local correspondiente a Toronto, Canadá.

## 2. Causa Raíz
La zona horaria de systemd (`/etc/localtime`) apuntaba a UTC (`+0000`) en vez de la región `America/Toronto` (EDT, UTC-4).

## 3. Solución Aplicada
Se reconfiguró la zona horaria del sistema y se verificó la sincronización NTP:
```bash
timedatectl set-timezone America/Toronto
```

## 4. Archivos Modificados
- `/etc/localtime` (enlace simbólico a `/usr/share/zoneinfo/America/Toronto`)

## 5. Validación
Se verificó el estado con `timedatectl` y `date`:
- Zona horaria activa: `America/Toronto (EDT, -0400)`.
- Reloj y sincronización NTP activos y reflejados en el entorno de escritorio.
