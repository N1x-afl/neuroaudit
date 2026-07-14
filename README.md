<div align="center">

```
███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗
████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║   
██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║   
██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝██████╔╝██║   ██║   
```

**SHIELD EDITION v6.7.0**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux%20Only-green?style=flat-square&logo=linux)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Version](https://img.shields.io/badge/Version-6.7.0-red?style=flat-square)

*Suite de auditoría de seguridad y operaciones IT para sistemas Linux*

</div>

---

## ¿Qué es NeuroAudit?

NeuroAudit es una herramienta de línea de comandos desarrollada en Python puro para auditoría de seguridad, mantenimiento y diagnóstico de sistemas Linux. Diseñada para sysadmins y equipos de seguridad, agrupa en un solo binario los checks más críticos que normalmente requieren múltiples herramientas.

No requiere dependencias externas fuera de la librería estándar de Python y las herramientas nativas del sistema (`ss`, `find`, `dpkg`, `journalctl`, etc.).

> ⚠️ **Esta versión (Shield Edition) es exclusiva para Linux.**
> El soporte para Windows fue discontinuado a partir de la v6.5.
> Esta edición utiliza herramientas nativas de Linux (`journalctl`, `dpkg`, `ss`, `/proc`, `/etc/shadow`) que no están disponibles en Windows.

---

## Módulos disponibles

| # | Módulo | Descripción |
|---|--------|-------------|
| 1 | **Hardware & Térmica** | CPU, RAM, temperatura, serial, uptime y diagnóstico de pasta térmica |
| 2 | **Mantenimiento** | `apt update/upgrade`, limpieza de caché, reducción de logs |
| 3 | **Vulnerabilidad CVE (libcurl)** | Verificación puntual de libcurl4 contra CVE conocidos |
| 4 | **Salud de Discos** | S.M.A.R.T. por dispositivo + uso de particiones con `df` |
| 5 | **Red y Puertos** | Escaneo LAN con nmap + puertos en escucha con `ss` |
| 6 | **Eventos del Sistema** | Últimos 15 errores del journal (`journalctl -p err`) |
| 7 | **Exportar Reporte JSON** | Snapshot del sistema exportado a JSON en el home del usuario |
| 8 | **Inventario de Software** | Lista de paquetes instalados vía `dpkg` + conteo total |
| 9 | **Auto-actualización** | Descarga la última versión desde GitHub y se reemplaza |
| 10 | **Permisos y Usuarios** | Archivos críticos (`/etc/shadow`, `sudoers`) y usuarios con sudo |
| 11 | **CVE Scan — Todos los Paquetes** | Escaneo real contra OSV.dev Batch API (sin API key) |
| 12 | **Auditoría de Servidor** | Suite completa de seguridad para servidores (ver detalle abajo) |

---

## Módulo 12 — Auditoría de Servidor

Submenú especializado con 5 checks independientes y opción de ejecución completa:

### `[1]` Firewall — Estado y Reglas
- Detecta automáticamente **UFW** o **iptables**
- Muestra estado ACTIVO/INACTIVO con código de color
- Lista reglas activas y marca puertos expuestos en `0.0.0.0` / `::`

### `[2]` Archivos SUID / SGID Sospechosos
- Escanea todo el filesystem con `find -perm -4000 / -perm -2000`
- Compara contra whitelist de ~25 binarios legítimos de Debian/Ubuntu
- Reporta en rojo cualquier binario fuera de la whitelist con sus permisos

### `[3]` Accesos Fallidos y Últimos Logins
- Parsea `/var/log/auth.log` (fallback a `journald`)
- Top IPs atacantes con umbral de color (>10 intentos = rojo)
- `faillog` del sistema, últimos logins exitosos y cuentas sin password

### `[4]` Procesos Anómalos
- Top 10 por CPU y RAM con colores por umbral
- Detecta procesos corriendo desde `/tmp`, `/dev/shm` o `/var/tmp`
- Detecta procesos zombie

### `[5]` Conexiones Activas Sospechosas
- Conexiones establecidas al exterior (excluye loopback y LAN)
- Marca puertos asociados a C2/backdoors (`:4444`, `:31337`, `:9999`, etc.)
- Resumen de estados TCP y top IPs remotas por volumen de conexiones

### `[6]` Auditoría Completa
Ejecuta los 5 checks en secuencia y ofrece exportar todo a JSON.

---

## Módulo 11 — CVE Scan (OSV.dev)

- Obtiene todos los paquetes instalados con `dpkg-query`
- Consulta la [OSV.dev Batch API](https://osv.dev) en chunks de 100 paquetes
- Clasifica por severidad: `CRITICAL` / `HIGH` / `MEDIUM` / `LOW`
- Muestra detalle por CVE: ID, aliases, resumen
- Exporta resultados a `neuroaudit_cve_YYYYMMDD_HHMM.json`
- **Sin API key requerida**

---

## Instalación

### Requisitos
- Python 3.8+
- Linux (Debian / Ubuntu / Kali / Zorin / Arch / Fedora)
- `sudo` / acceso root para módulos de auditoría

### Opción A — Instalador automático (recomendado)

```bash
git clone https://github.com/N1x-afl/neuroaudit.git
cd neuroaudit
chmod +x instalar_neuroaudit.sh
sudo ./instalar_neuroaudit.sh
```

El instalador verifica Python3, copia el script a `/usr/local/bin/neuroaudit`, da permisos y ofrece instalar dependencias opcionales.

### Opción B — Instalación manual

Usá este método si el instalador no funciona o preferís hacerlo paso a paso:

```bash
# 1. Clonar el repositorio
git clone https://github.com/N1x-afl/neuroaudit.git
cd neuroaudit

# 2. Copiar al sistema
sudo cp neuroaudit.py /usr/local/bin/neuroaudit

# 3. Dar permisos de ejecución
sudo chmod +x /usr/local/bin/neuroaudit

# 4. Verificar instalación
head -1 /usr/local/bin/neuroaudit
# Debe mostrar: #!/usr/bin/env python3

# 5. Ejecutar
sudo neuroaudit
```

### Opción C — Sin instalar (ejecución directa)

```bash
git clone https://github.com/N1x-afl/neuroaudit.git
cd neuroaudit
sudo python3 neuroaudit.py
```

---

## Ejecución

```bash
sudo neuroaudit
```

---

## Actualización

Desde el menú principal, opción **[9]** descarga la última versión desde `main` y reemplaza el binario automáticamente.

O manualmente:

```bash
cd ~/neuroaudit
git pull
sudo cp neuroaudit.py /usr/local/bin/neuroaudit
```

---

## Exportación de reportes

| Módulo | Archivo generado |
|--------|-----------------|
| 7 — Reporte general | `reporte_audit_YYYYMMDD.json` |
| 11 — CVE scan | `neuroaudit_cve_YYYYMMDD_HHMM.json` |
| 12 — Auditoría servidor | `neuroaudit_servidor_YYYYMMDD_HHMM.json` |

Todos se guardan en el home del usuario que invocó `sudo`.

---

## Solución de problemas frecuentes

### `bash: neuroaudit: orden no encontrada`
El script no está en el PATH. Usá la instalación manual (Opción B) o ejecutalo directamente:
```bash
sudo python3 ~/neuroaudit/neuroaudit.py
```

### `./instalar_neuroaudit.sh: No existe el fichero o el directorio`
```bash
# Asegurate de estar dentro de la carpeta del repo
cd ~/neuroaudit
chmod +x instalar_neuroaudit.sh
sudo ./instalar_neuroaudit.sh
```

### `Permission denied`
```bash
sudo chmod +x /usr/local/bin/neuroaudit
```

### Módulos que muestran `N/A`
Algunos módulos requieren herramientas adicionales:
```bash
sudo apt install lm-sensors smartmontools nmap
sudo sensors-detect   # para temperatura de CPU
```

---

## Changelog

| Versión | Cambios |
|---------|---------|
| **6.7.0** | Módulo 12 — Auditoría de Servidor (Firewall, SUID/SGID, Accesos, Procesos, Conexiones) |
| **6.6.0** | Módulo 11 — CVE Scan real via OSV.dev Batch API |
| **6.5.0** | Módulo 10 — Auditoría de Permisos y Usuarios · Discontinuado soporte Windows |
| **6.x** | Versiones anteriores: Hardware, Mantenimiento, Red, Discos, Eventos, Inventario |

---

## Autor

**Felipe Soluciones IT**  
GitHub: [@N1x-afl](https://github.com/N1x-afl)

---

<div align="center">
<sub>NeuroAudit — Security & IT Suite · Shield Edition · Linux Only</sub>
</div>
