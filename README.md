# 🛡️ NEUROAUDIT - Universal IT & Security Suite
**Desarrollado por:** Felipe Soluciones IT  
**Versión:** 4.4 Universal Edition (Stable)  
**Usuario GitHub:** [N1x-afl](https://github.com/N1x-afl)

---

## 🚀 Evolución Universal
**NEUROAUDIT** ha evolucionado. En su versión 4.4, la suite ya no está limitada a una sola familia de Linux. Ahora cuenta con un **motor de detección de arquitectura** que adapta los comandos de mantenimiento y actualización según el gestor de paquetes nativo del sistema.

Es la herramienta definitiva para técnicos que saltan entre servidores Debian, estaciones de trabajo Fedora o laboratorios en Arch Linux.

## 🛠️ Capacidades de la Suite

### 🖥️ Auditoría de Hardware e Identidad (Universal)
* **Hardware Report:** Obtiene Serial Number/Tag, modelo de CPU y arquitectura.
* **Métricas de Rendimiento:** Monitoreo de RAM (Total/Uso/Libre) y procesos críticos.
* **Control de Estabilidad:** Reporte de **Uptime** detallado para verificar ciclos de reinicio.

### 🔒 Seguridad y Red (Universal)
* **Socket Audit:** Mapeo proactivo de puertos en estado `LISTEN`.
* **Service Mapping:** Identificación de protocolos (SSH, HTTP, RPC, etc.) en IPv4 e IPv6 mediante resolución inversa.

### 🔋 Salud de Componentes (Universal)
* **Storage Health:** Filtrado inteligente de unidades físicas (SSD/NVMe) para un diagnóstico veraz de capacidad.
* **Battery Analytics:** Monitoreo de nivel de desgaste químico con alertas visuales de estado.

### 🧹 Mantenimiento Inteligente (Multi-Distro)
El script detecta y utiliza comandos nativos para:
* **Sistemas APT:** Debian, Ubuntu, Zorin OS, Mint.
* **Sistemas DNF:** Fedora, RHEL, CentOS.
* **Sistemas PACMAN:** Arch Linux, Manjaro.

---

## 🛡️ Instalación Segura y Verificación
Como parte de nuestro compromiso con la ciberseguridad, recomendamos verificar la integridad del archivo antes de otorgar permisos de superusuario.

1. **Descargar el script:**
   ```bash
   curl -O [https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py](https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py)
