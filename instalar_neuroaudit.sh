#!/bin/bash
# ===========================================================
# NEUROAUDIT — Instalador para Linux
# Desarrollado por: Felipe Soluciones IT
# ===========================================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;91m'
CYAN='\033[0;96m'
RESET='\033[0m'

echo -e "${CYAN}"
echo "  ┌─────────────────────────────────────────────────┐"
echo "  │   NEUROAUDIT — Instalador Linux                 │"
echo "  │   Felipe Soluciones IT                          │"
echo "  └─────────────────────────────────────────────────┘"
echo -e "${RESET}"

# Verificar root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}  ERROR: Ejecutar como root: sudo ./instalar_neuroaudit.sh${RESET}"
    exit 1
fi

# Verificar Python3
echo -e "${YELLOW}  [1/4] Verificando Python3...${RESET}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}  Python3 no encontrado. Instalando...${RESET}"
    apt install -y python3 python3-pip 2>/dev/null || \
    dnf install -y python3 python3-pip 2>/dev/null || \
    pacman -S --noconfirm python python-pip 2>/dev/null
fi
PYTHON_VER=$(python3 --version)
echo -e "${GREEN}  ✓ ${PYTHON_VER}${RESET}"

# Verificar que neuroaudit.py existe en la carpeta actual
echo -e "${YELLOW}  [2/4] Verificando archivo neuroaudit.py...${RESET}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ ! -f "$SCRIPT_DIR/neuroaudit.py" ]; then
    echo -e "${RED}  ERROR: No se encontró neuroaudit.py en $SCRIPT_DIR${RESET}"
    echo -e "${YELLOW}  Asegurate de ejecutar este script desde la carpeta del repo.${RESET}"
    exit 1
fi
echo -e "${GREEN}  ✓ neuroaudit.py encontrado en $SCRIPT_DIR${RESET}"

# Instalar en el sistema
echo -e "${YELLOW}  [3/4] Instalando en /usr/local/bin/neuroaudit...${RESET}"
cp "$SCRIPT_DIR/neuroaudit.py" /usr/local/bin/neuroaudit
chmod +x /usr/local/bin/neuroaudit

# Verificar shebang
SHEBANG=$(head -1 /usr/local/bin/neuroaudit)
if [[ "$SHEBANG" != "#!/usr/bin/env python3" ]]; then
    echo -e "${RED}  ADVERTENCIA: El archivo no tiene shebang correcto.${RESET}"
    echo -e "${YELLOW}  Agregando shebang...${RESET}"
    sed -i '1s|^|#!/usr/bin/env python3\n|' /usr/local/bin/neuroaudit
fi
echo -e "${GREEN}  ✓ Instalado correctamente${RESET}"

# Instalar dependencias opcionales
echo -e "${YELLOW}  [4/4] Verificando dependencias del sistema...${RESET}"

FALTANTES=()
command -v sensors   &>/dev/null || FALTANTES+=("lm-sensors")
command -v smartctl  &>/dev/null || FALTANTES+=("smartmontools")
command -v nmap      &>/dev/null || FALTANTES+=("nmap")
command -v ufw       &>/dev/null || FALTANTES+=("ufw")

if [ ${#FALTANTES[@]} -gt 0 ]; then
    echo -e "${YELLOW}  Dependencias opcionales no instaladas: ${FALTANTES[*]}${RESET}"
    read -p "  ¿Instalar ahora? (S/N): " RESP
    if [[ "$RESP" =~ ^[Ss]$ ]]; then
        if command -v apt &>/dev/null; then
            apt update -qq && apt install -y "${FALTANTES[@]}"
        elif command -v dnf &>/dev/null; then
            dnf install -y "${FALTANTES[@]}"
        elif command -v pacman &>/dev/null; then
            pacman -S --noconfirm "${FALTANTES[@]}"
        fi
        echo -e "${GREEN}  ✓ Dependencias instaladas${RESET}"
    else
        echo -e "${YELLOW}  Omitido. Algunos módulos pueden mostrar N/A.${RESET}"
    fi
else
    echo -e "${GREEN}  ✓ Todas las dependencias presentes${RESET}"
fi

# Resumen
echo ""
echo -e "${CYAN}  ┌─────────────────────────────────────────────────┐${RESET}"
echo -e "${CYAN}  │  ✓  Instalación completada                      │${RESET}"
echo -e "${CYAN}  │                                                 │${RESET}"
echo -e "${CYAN}  │  Ejecutar con:  sudo neuroaudit                 │${RESET}"
echo -e "${CYAN}  └─────────────────────────────────────────────────┘${RESET}"
echo ""
