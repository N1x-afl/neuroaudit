# 🛡️ NEUROAUDIT - Security & IT Suite
**Desarrollado por:** Felipe Soluciones IT  
**Versión:** 4.1 Stable  

**NEUROAUDIT** es una herramienta integral de terminal diseñada para la gestión profesional de infraestructura Linux. Centraliza tareas de soporte técnico, auditoría de hardware y seguridad perimetral local en una interfaz intuitiva y potente.

## 🚀 Funcionalidades Principales

1. **Auditoría Técnica:** Identificación de Serial Number (Tag), CPU, RAM detallada y Kernel.
2. **Gestión de Actualizaciones:** Actualización segura de repositorios y paquetes (Upgrade).
3. **Mantenimiento Proactivo:** Purga de archivos residuales y limpieza de caché del sistema.
4. **Monitor de Recursos:** Identificación de procesos que más consumen memoria RAM.
5. **Auditoría de Seguridad:** Escaneo de puertos en escucha (`LISTEN`) con identificación de servicios.
6. **Diagnóstico de Hardware:** Reporte de salud de batería (capacidad real) y estado de unidades físicas.

## 🔧 Instalación Rápida (One-Liner)
Puedes instalar NEUROAUDIT ejecutando este comando en tu terminal:



```bash
curl -O https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py && chmod +x neuroaudit.py && sudo mv neuroaudit.py /usr/local/bin/neuroaudit
