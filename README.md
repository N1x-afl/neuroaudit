# NEUROAUDIT v6.1
### Security & IT Suite — Multiplataforma (Linux + Windows)

> Herramienta de auditoría y diagnóstico del sistema desarrollada por **Felipe Soluciones IT**

---

## Capturas de pantalla

### Linux
```
███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗
████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝
██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║   
██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║   
██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝██████╔╝██║   ██║   
╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   
══════════════════════════════════════════════════════════════════════════════════════
                   A  U  D  I  T     S  Y  S  T  E  M   v6.1
══════════════════════════════════════════════════════════════════════════════════════
```

### Windows Terminal
```
  +-----------------------------------------------------------------+
  |    N E U R O A U D I T   v6.1                                  |
  |    S Y S T E M   A U D I T   -   Security & IT Suite           |
  +-----------------------------------------------------------------+
```

---

## Descripción

**NEUROAUDIT** es una herramienta de línea de comandos multiplataforma para auditoría, diagnóstico y mantenimiento de sistemas. Diseñada para administradores de sistemas, técnicos IT y usuarios avanzados que necesitan información detallada de su equipo en un solo lugar.

Funciona en **Linux** (Debian/Ubuntu/Mint, Fedora/RHEL, Arch/Manjaro) y **Windows 10/11**.

---

## Requisitos del sistema

### Linux
| Requisito | Detalle |
|---|---|
| Python | 3.8 o superior |
| Privilegios | sudo |
| Dependencias opcionales | `lm-sensors`, `smartmontools`, `nmap`, `ufw` |
| Dependencias Python | `reportlab`, `pyyaml` (instaladas automáticamente) |

### Windows
| Requisito | Detalle |
|---|---|
| Python | 3.8 o superior ([python.org](https://www.python.org/downloads/)) |
| Privilegios | Administrador |
| Terminal recomendada | Windows Terminal (para logo completo) |
| Dependencias Python | `reportlab`, `pyyaml`, `Pillow` (instaladas automáticamente) |

---

## Instalación

### Linux

**1. Clonar el repositorio:**
```bash
git clone https://github.com/N1x-afl/neuroaudit.git
cd neuroaudit
```

**2. Ejecutar el instalador (una sola vez):**
```bash
bash instalar_neuroaudit.sh
```

El instalador:
- Crea un entorno virtual `.venv`
- Instala `reportlab` y `pyyaml`
- Crea el lanzador `./neuroaudit`
- Ofrece crear el comando global `neuroaudit` en `/usr/local/bin`

**3. Ejecutar:**
```bash
neuroaudit
# o desde la carpeta del proyecto:
./neuroaudit
```

---

### Windows

**1. Clonar o descargar el repositorio:**
```
neuroaudit\
    neuroaudit.py
    instalar_neuroaudit.bat
```

**2. Ejecutar el instalador como Administrador:**
- Clic derecho en `instalar_neuroaudit.bat` → **Ejecutar como administrador**

El instalador:
- Verifica Python instalado
- Crea el entorno virtual `.venv`
- Instala `reportlab`, `pyyaml` y `Pillow`
- Genera el lanzador `neuroaudit_win.bat`

**3. Ejecutar:**
- Doble clic en `neuroaudit_win.bat` (pide elevación automáticamente)

> **Recomendado:** Usar **Windows Terminal** para ver el logo completo con caracteres Unicode.

---

## Módulos disponibles

| # | Módulo | Linux | Windows |
|---|---|---|---|
| 1 | Hardware e Identidad Térmica | ✅ | ✅ |
| 2 | Mantenimiento del Sistema | ✅ | ✅ |
| 3 | Salud de Discos y S.M.A.R.T. | ✅ | ✅ |
| 4 | Auditoría de Seguridad (Puertos) | ✅ | ✅ |
| 5 | Reporte de Eventos del Sistema | ✅ | ✅ |
| 6 | Inventario de Software Instalado | ✅ | ✅ |
| 7 | Exportar Reporte Completo | ✅ | ✅ |
| 8 | Ping / Test de Conectividad | ✅ | ✅ |
| 9 | Escaneo de Red Local | ✅ | ✅ |
| 10 | Auditoría de Permisos y Usuarios | ✅ | ✅ |

### Módulo 7 — Formatos de exportación
- JSON
- YAML
- XML
- CSV
- **PDF** (requiere `reportlab`)
- HTML

### Módulo 1 — Diagnóstico de pasta térmica
- Detección automática Notebook / Desktop
- Temperatura CPU y GPU en tiempo real
- Historial de 3 lecturas con análisis de variación
- Recomendación según temperatura y tipo de equipo

---

## Estructura del proyecto

```
neuroaudit/
├── neuroaudit.py              # Script principal
├── instalar_neuroaudit.sh     # Instalador Linux
├── instalar_neuroaudit.bat    # Instalador Windows
├── README.md
├── .gitignore
└── LICENSE
```

---

## Uso del modo --setup (Linux)

```bash
sudo neuroaudit --setup
```

Verifica e instala dependencias del sistema: `lm-sensors`, `smartmontools`, `nmap`, `ufw`.

---

## Licencia

MIT License — libre para uso personal y comercial.

---

## Autor

**Felipe Soluciones IT**  
Desarrollado con Python 3 — multiplataforma Linux/Windows
