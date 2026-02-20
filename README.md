# 🛡️ NEUROAUDIT - Universal IT & Security Suite
**Desarrollado por:** Felipe Soluciones IT  
**Versión:** 4.4 Universal Edition (Stable)  
**Usuario GitHub:** [N1x-afl](https://github.com/N1x-afl)

---

## 🚀 Evolución Universal
**NEUROAUDIT** es una herramienta integral de terminal diseñada para técnicos de soporte y administradores de sistemas Linux. Cuenta con un **motor de detección de arquitectura** que adapta los comandos de mantenimiento y actualización según el gestor de paquetes nativo (APT, DNF o PACMAN).

## 🛠️ Capacidades de la Suite

### 🖥️ Auditoría de Hardware e Identidad
* **Hardware Report:** Obtiene Serial Number/Tag, modelo de CPU y arquitectura del Kernel.
* **Métricas de Rendimiento:** Monitoreo de RAM y **Uptime** detallado.

### 🔒 Seguridad y Red
* **Socket Audit:** Mapeo de puertos en estado `LISTEN` e identificación de protocolos (SSH, HTTP, RPC, etc.) en IPv4 e IPv6.

### 🔋 Salud de Componentes
* **Storage & Battery:** Diagnóstico veraz de discos físicos y nivel de desgaste de batería.

---

## 🛡️ Instalación Segura y Verificación (Protocolo N1x)
Para garantizar la integridad y siguiendo buenas prácticas de ciberseguridad, se recomienda verificar el archivo antes de su ejecución global.

1. **Descargar el script:**
   ```bash
   curl -O [https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py](https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py)

## Validar Integridad (SHA-256 Checksum):
echo "90ce1c46df53c6ef7a699e5762cc7614e1e8c2125eadeb49ee3d54a77b169064  neuroaudit.py" | sha256sum -c
   
