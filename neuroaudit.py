#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys
import socket

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT
# ==========================================================
VERSION = "4.5 Stable"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"

class Colors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def get_package_manager():
    if os.path.exists("/usr/bin/apt-get"): return "APT (Debian/Ubuntu/Zorin)"
    if os.path.exists("/usr/bin/dnf"): return "DNF (Fedora/RHEL)"
    if os.path.exists("/usr/bin/pacman"): return "PACMAN (Arch Linux)"
    return "UNKNOWN"

PKG_MANAGER = get_package_manager()

def show_banner():
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
     ✅ SISTEMA DE INTEGRIDAD ACTIVO
     Powered by: {DEVELOPER} | Modo: {PKG_MANAGER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}{'='*65}{Colors.ENDC}")
    print(f"{Colors.HEADER}       REPORTES DE INFRAESTRUCTURA TÉCNICA{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*65}{Colors.ENDC}")
    
    # Datos de Hardware
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("lscpu | grep -i 'model name' | head -1 | cut -d: -f2 | sed 's/^[ \t]*//'").strip()
    ram_t = subprocess.getoutput("free -h | grep Mem | awk '{print $2}'").strip()
    ram_u = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    uptime = subprocess.getoutput("uptime -p").replace("up ", "")
    
    print(f"{Colors.BOLD}SERIAL:  {Colors.ENDC}{serial}")
    print(f"{Colors.BOLD}CPU:     {Colors.ENDC}{cpu}")
    print(f"{Colors.BOLD}RAM:     {Colors.ENDC}{ram_u} en uso / {ram_t} total")
    print(f"{Colors.BOLD}UPTIME:  {Colors.ENDC}{uptime}")

def audit_security():
    print(f"\n{Colors.WARNING}--- AUDITORÍA DE PUERTOS (LISTEN) ---{Colors.ENDC}")
    print(subprocess.getoutput("sudo ss -tunlp | grep LISTEN | awk '{print $1, $5}'"))

def clean_system():
    print(f"\n{Colors.INFO}Iniciando limpieza de residuos...{Colors.ENDC}")
    if "APT" in PKG_MANAGER:
        os.system("sudo apt autoremove -y && sudo apt autoclean")
    print(f"{Colors.SUCCESS}Limpieza completada.{Colors.ENDC}")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"{Colors.BOLD}1.{Colors.ENDC} Auditoría de Hardware")
        print(f"{Colors.BOLD}2.{Colors.ENDC} Auditoría de Seguridad (Puertos)")
        print(f"{Colors.BOLD}3.{Colors.ENDC} Mantenimiento y Limpieza")
        print(f"{Colors.BOLD}0.{Colors.ENDC} Salir")
        
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")

        if op == "1":
            get_sys_info()
            input("\nPresione Enter para volver...")
        elif op == "2":
            audit_security()
            input("\nPresione Enter para volver...")
        elif op == "3":
            clean_system()
            input("\nPresione Enter para volver...")
        elif op == "0":
            print(f"{Colors.INFO}Saliendo de NeuroAudit...{Colors.ENDC}")
            break

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Error: Debes ejecutar NeuroAudit con privilegios de SUDO.{Colors.ENDC}")
        sys.exit(1)
    main()
