# 🛡️ NEUROAUDIT - Professional IT & Security Suite
**Desarrollado por:** Felipe Soluciones IT  
**Versión:** 4.3 Multi-Distro (Stable)  
**Usuario GitHub:** [N1x-afl](https://github.com/N1x-afl)

---

## 🚀 ¿Qué es NEUROAUDIT?
**NEUROAUDIT** es una herramienta integral de terminal diseñada para técnicos de soporte y administradores de sistemas Linux. Automatiza el diagnóstico de hardware, la auditoría de seguridad perimetral y el mantenimiento proactivo del sistema.

Esta versión **Multi-Distro** incluye un motor de detección inteligente que identifica el gestor de paquetes del sistema para asegurar una ejecución segura en diferentes arquitecturas.

## 🛠️ Funcionalidades Principales

### 🖥️ Auditoría de Hardware e Identidad
* **Identificación Total:** Service Tag/Serial real, modelo de CPU y arquitectura de Kernel.
* **Gestión de Memoria:** Reporte en tiempo real de RAM total, usada y disponible.
* **Uptime:** Monitoreo del tiempo de actividad para diagnóstico de estabilidad.

### 🔒 Seguridad de Red
* **Socket Audit:** Mapeo de puertos en estado `LISTEN`.
* **Service Mapping:** Resolución inversa para identificar qué servicios (SSH, HTTP, RPC, etc.) están activos en IPv4 e IPv6.

### 🔋 Diagnóstico de Hardware Crítico
* **Storage Audit:** Filtrado de unidades físicas (SSD/NVMe) eliminando ruido de unidades virtuales.
* **Battery Health:** Cálculo del nivel de desgaste químico (Capacity) con alertas visuales de estado saludable, desgastado o crítico.

### 🧹 Mantenimiento (Optimizado para Sistemas APT)
* **Smart Clean:** Purga de archivos residuales y configuraciones huérfanas (`rc`).
* **Auto-Upgrade:** Sincronización y actualización de repositorios con un solo comando.

---

## ⚙️ Instalación Rápida (One-Liner)

Para instalar **NEUROAUDIT** en cualquier equipo Linux, simplemente pega el siguiente comando en tu terminal:

```bash
curl -O [https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py](https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py) && chmod +x neuroaudit.py && sudo mv neuroaudit.py /usr/local/bin/neuroaudit
