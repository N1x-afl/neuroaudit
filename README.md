<p align="center">
  <img src="menu.png" width="600" title="NeuroAudit Preview">
</p>

# 🛡️ NeuroAudit - Security & IT Suite v4.8.6

**NeuroAudit** es una herramienta de auditoría de sistemas y diagnóstico de hardware desarrollada por **Felipe Soluciones IT**. Diseñada para profesionales de soporte técnico y administración de sistemas Linux, esta suite permite obtener reportes precisos en segundos.



## 🚀 Características Principales

* ✅ **Integridad Dinámica:** Sistema de autoverificación para asegurar que el script no ha sido alterado.
* 🌡️ **Diagnóstico Térmico:** Monitorización de temperatura con alertas inteligentes para cambio de pasta térmica.
* 🆔 **Identificación de Hardware:** Extracción de Serial Number (Service Tag) mediante `dmidecode`.
* 📊 **Auditoría de Almacenamiento:** Reporte detallado de particiones, modelos de disco (SATA/NVMe) y salud S.M.A.R.T.
* 🐧 **Multi-Distro:** Autodetección de Sistema Operativo (Zorin, Ubuntu, Debian, etc.) y gestión de mantenimiento según el gestor de paquetes (APT/DNF).
* 🛡️ **Seguridad:** Escaneo rápido de puertos en escucha y monitoreo de procesos.

## 🛠️ Requisitos

Para el correcto funcionamiento de los sensores y discos, asegúrate de tener instalados:
```bash
sudo apt update && sudo apt install lm-sensors smartmontools dmidecode -y
sudo sensors-detect --auto  

📦 Instalación Rápida
curl -L -o neuroaudit "[https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py?$(date](https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py?$(date) +%s)" && chmod +x neuroaudit && sudo mv neuroaudit /usr/local/bin/neuroaudit

🖥️ Uso
Simplemente ejecuta el comando con privilegios de superusuario:
sudo neuroaudit








