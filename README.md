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
![Platform](https://img.shields.io/badge/Platform-Linux-green?style=flat-square&logo=linux)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Version](https://img.shields.io/badge/Version-6.7.0-red?style=flat-square)

*Suite de auditoría de seguridad y operaciones IT para sistemas Linux*

</div>

---

## ¿Qué es NeuroAudit?

NeuroAudit es una herramienta de línea de comandos desarrollada en Python puro para auditoría de seguridad, mantenimiento y diagnóstico de sistemas Linux. Diseñada para sysadmins y equipos de seguridad, agrupa en un solo binario los checks más críticos que normalmente requieren múltiples herramientas.

No requiere dependencias externas fuera de la librería estándar de Python y las herramientas nativas del sistema (`ss`, `find`, `dpkg`, `journalctl`, etc.).

---

## Módulos disponibles

| # | Módulo | Descripción |
|---|--------|-------------|
| 1 | **Hardware & Térmica** | CPU, RAM, temperatura, serial, uptime y diagnóstico de pasta térmica |
| 2 | **Mantenimiento** | `apt update/upgrade`, limpieza de caché, reducción de logs, bypass HTTP |
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
- Linux (Debian/Ubuntu recomendado)
- `sudo` / acceso root para módulos de auditoría

### Instalación rápida

```bash
git clone https://github.com/N1x-afl/neuroaudit.git
cd neuroaudit
chmod +x instalar_neuroaudit.sh
sudo ./instalar_neuroaudit.sh
```

El instalador crea un virtualenv, instala dependencias y genera el wrapper `/usr/local/bin/neuroaudit`.

### Ejecución

```bash
sudo neuroaudit
```

---

## Actualización

Desde el menú principal, opción **[9]** descarga la última versión desde `main` y reemplaza el binario automáticamente.

O manualmente:

```bash
cd ~/ruta/neuroaudit
git pull
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

## Changelog

| Versión | Cambios |
|---------|---------|
| **6.7.0** | Módulo 12 — Auditoría de Servidor (Firewall, SUID/SGID, Accesos, Procesos, Conexiones) |
| **6.6.0** | Módulo 11 — CVE Scan real via OSV.dev Batch API |
| **6.5.0** | Módulo 10 — Auditoría de Permisos y Usuarios |
| **6.x** | Versiones anteriores: Hardware, Mantenimiento, Red, Discos, Eventos, Inventario |

---

## Autor

**Felipe Soluciones IT**  
GitHub: [@N1x-afl](https://github.com/N1x-afl)

---

<div align="center">
<sub>NeuroAudit — Security & IT Suite · Shield Edition</sub>
</div>
