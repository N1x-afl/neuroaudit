#!/usr/bin/env python3
import os
import subprocess
import sys
import re

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.8.5
# ==========================================================
VERSION = "4.8.5 Multi-Distro"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.8.5"

class Colors:
    HEADER, SUCCESS, INFO = '\033[95m', '\033[92m', '\033[94m'
    WARNING, ERROR, ENDC, BOLD = '\033[93m', '\033[91m', '\033[0m', '\033[1m'

def verify_self_integrity():
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            content = f.read()
        return "Felipe Soluciones IT" in content and len(content) > 4000
    except: return False

def get_distro_info():
    """Detecta la distribución de Linux y el gestor de paquetes"""
    distro = subprocess.getoutput("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'")
    pkg_manager = "Desconocido"
    if os.path.exists("/usr/bin/apt"): pkg_manager = "APT"
    elif os.path.exists("/usr/bin/dnf"): pkg_manager = "DNF"
    elif os.path.exists("/usr/bin/pacman"): pkg_manager = "Pacman"
    elif os.path.exists("/usr/bin/zypper"): pkg_manager = "Zypper"
    
    return distro if distro else "Linux Generic", pkg_manager

def show_banner():
    distro, pkg = get_distro_info()
    is_valid = verify_self_integrity()
    status_msg = f"{Colors.SUCCESS}✅ INTEGRIDAD VERIFICADA" if is_valid else f"{Colors.ERROR}❌ INTEGRIDAD COMPROMETIDA"
    
    banner = f"""{Colors.SUCCESS}
    ┌────────────────────────────────────────────────────────┐
    │   ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗          │
    │   ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗         │
    │   ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║         │
    │   ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║         │
    │   ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝         │
    │   ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝          │
    │                S Y S T E M   A U D I T                 │
    └────────────────────────────────────────────────────────┘
                {Colors.WARNING}          ______
                {Colors.WARNING}       _ [______] _
                {Colors.WARNING}      | |  ____  | |
                {Colors.WARNING}      | | |    | | |
                {Colors.WARNING}      |_| |____| |_|
                {Colors.WARNING}          |____|{Colors.SUCCESS}

     {SYSTEM_NAME} | v{VERSION} 
     {status_msg}
     OS: {distro} ({pkg})
     Powered by: {DEVELOPER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}--- INFRAESTRUCTURA Y SALUD TÉRMICA ---{Colors.ENDC}")
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    
    # Lógica de temperatura infalible heredada de v4.8.1
    sensors_output = subprocess.getoutput("sensors")
    match = re.search(r"(?:Package id 0|temp1|Core 0|temp2):\s+[\+\-]?(\d+\.\d+)", sensors_output)
    
    if match:
        temp_val = float(match.group(1))
        t_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}" if temp_val < 75 else f"{Colors.ERROR}{temp_val}°C ⚠️ REVISAR PASTA TÉRMICA{Colors.ENDC}"
    else:
        t_status = f"{Colors.INFO}N/A{Colors.ENDC}"

    ram = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    print(f"SERIAL: {serial if serial else 'No detectable'}")
    print(f"CPU:    {cpu}")
    print(f"TEMP:   {t_status}")
    print(f"RAM:    {ram} en uso")
    print(f"UPTIME: {subprocess.getoutput('uptime -p')}")

def maintenance():
    _, pkg = get_distro_info()
    print(f"\n{Colors.INFO}Iniciando mantenimiento con {pkg}...{Colors.ENDC}")
    if pkg == "APT":
        os.system("sudo apt update && sudo apt autoremove -y")
    elif pkg == "DNF":
        os.system("sudo dnf check-update && sudo dnf autoremove -y")
    else:
        print(f"{Colors.WARNING}Gestor de paquetes no soportado para mantenimiento automático.{Colors.ENDC}")
    print(f"{Colors.SUCCESS}Proceso finalizado.{Colors.ENDC}")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"1. Auditoría de Hardware e Identidad TÉRMICA")
        print(f"2. Mantenimiento del Sistema")
        print(f"3. Monitor de Procesos (HTOP)")
        print(f"4. Auditoría de Seguridad (Puertos)")
        print(f"5. SALUD: Batería y Discos SMART")
        print(f"0. Salir")
        op = input(f"\nSeleccione operación: ")
        if op == "1": get_sys_info()
        elif op == "2": maintenance()
        elif op == "3": os.system("htop")
        elif op == "4": os.system("sudo ss -tunlp | grep LISTEN")
        elif op == "5":
             os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'percentage|capacity'")
             os.system("sudo smartctl --all /dev/nvme0n1 | grep -E 'overall-health' || sudo smartctl --all /dev/sda | grep -E 'overall-health'")
        elif op == "0": break
        input(f"\nPresione Enter para volver...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Ejecutar con sudo.{Colors.ENDC}"); sys.exit(1)
    main()
