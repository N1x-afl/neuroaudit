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
---

## 🛠️ Instalación Rápida (One-Liner)

Para instalar NeuroAudit de manera global en tu sistema, ejecutá el siguiente comando en tu terminal:

```bash
curl -L -o neuroaudit "[https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py?$(date](https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py?$(date) +%s)" && chmod +x neuroaudit && sudo mv neuroaudit /usr/local/bin/neuroaudit

🖥️ Uso
Simplemente ejecuta el comando con privilegios de superusuario:

Gemini dijo
¡Excelente idea, Felipe! Para que tu proyecto en GitHub se vea como el de un SRE o Soporte Ssr, el README tiene que ser impecable.

Respecto a tu consulta sobre proteger el archivo, en Linux el comando clave es chattr (change attribute). Podés marcar el archivo como inmutable, lo que significa que nadie (ni siquiera vos con sudo o un proceso malicioso) podrá borrarlo, renombrarlo o modificarlo hasta que le quites ese atributo.

🛡️ Cómo Proteger tu Script contra Corrupción
Una vez que hayas instalado el script en su ruta definitiva, ejecutá esto:

Bash
# Para protegerlo (Inmutable)
sudo chattr +i /usr/local/bin/neuroaudit
Nota: Si después necesitás actualizarlo o borrarlo, primero tenés que quitarle la protección con: sudo chattr -i /usr/local/bin/neuroaudit.

📄 Texto para tu README.md de GitHub
Copiá y pegá este bloque en tu archivo README.md. Está diseñado para resaltar tu marca Felipe Soluciones IT.

Markdown
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
Para instalar NeuroAudit en tu sistema como un comando global:

Bash
curl -L -o neuroaudit "[https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py?$(date](https://raw.githubusercontent.com/N1x-afl/neuroaudit/main/neuroaudit.py?$(date) +%s)" && chmod +x neuroaudit && sudo mv neuroaudit /usr/local/bin/neuroaudit
🖥️ Uso
Simplemente ejecuta el comando con privilegios de superusuario:

Bash
sudo neuroaudit

