# GNOME Keyring SDDM PAM and login sync

- **Date:** 2026-10-16
- **Branch:** `fix/gnome-keyring-sddm-sync`
- **Type:** `fix`

---

## 1. Issue / Requirement
Aparecía una ventana emergente del sistema pidiendo contraseña para crear un "Default Keyring" al abrir aplicaciones como navegadores o editores. Se solicitó investigar el origen, evaluar la seguridad y configurar la opción más segura: cifrado del llavero sincronizado automáticamente con la contraseña de usuario.

## 2. Root Cause
Omarchy viene por defecto con un llavero sin contraseña (`Default_keyring.keyring`), pero SDDM y las aplicaciones modernas solicitan el llavero estándar `login` o `Default Keyring`. Al no estar sincronizado el puntero por defecto ni alineada la contraseña del llavero con la de inicio de sesión de Linux, GNOME Keyring solicitaba contraseña manual.

## 3. Applied Solution
1. Se configuró `~/.local/share/keyrings/default` para apuntar a la colección segura `login`.
2. Se instaló `seahorse` para la gestión gráfica de claves y certificados.
3. Se alineó la contraseña del llavero `login.keyring` con la contraseña de usuario de Linux.
4. Se verificó la integración de `pam_gnome_keyring.so` en `/etc/pam.d/sddm` para el desbloqueo transparente y cifrado al iniciar sesión.

## 4. Modified Files
- `~/.local/share/keyrings/default` (apunta a `login`)
- `~/.local/share/keyrings/login.keyring` (contraseña sincronizada con el usuario)
- `/home/dagudelo/Code/omarchy-setup/docs/resolutions/2026-10-16-gnome-keyring-sddm-sync.md`

## 5. Validation
- Verificación de `~/.local/share/keyrings/default` con contenido `login`.
- Confirmación de actualización del archivo `login.keyring` tras sincronizar la contraseña.
- Comprobación de que el servicio `gnome-keyring-daemon` y socket están activos en la sesión de usuario.
