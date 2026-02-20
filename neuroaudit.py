#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys
import socket
import hashlib

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.5
# ==========================================================
VERSION = "4.5 Hardened"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
# Este es el Hash que vamos a validar al final
OFFICIAL_HASH = "b8ff94b4f93a3bb52afaeb3acac8b39873c83d28b95b378f980df27000afbd33"

class Colors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def verify_self_integrity():
    try:
        with open(__file__, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        return file_hash == OFFICIAL_HASH, file_hash
    except:
        return False, "Error"

def get_package_manager():
    if os.path.exists("/usr/bin/apt-get"): return "APT (Debian/Ubuntu/Zorin)"
    if os.path.exists("/usr/bin/dnf"): return "DNF (Fedora/RHEL)"
    if os.path.exists("/usr/bin/pacman"): return "PACMAN (Arch Linux)"
    return "UNKNOWN"

PKG_MANAGER = get_package_manager()

def show_banner():
    is_valid, _ = verify_self_integrity()
    status_msg = f"{Colors.SUCCESS}✅ INTEGRIDAD VERIFICADA" if is_valid else f"{Colors.ERROR}❌ INTEGRIDAD NO VERIFICADA"
    
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
     Powered by: {DEVELOPER} | Modo: {PKG_MANAGER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}{'='*65}{Colors.ENDC}")
    print(f"{Colors.HEADER}       REPORTES DE INFRAESTRUCTURA TÉCNICA{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*65}{Colors.ENDC}")
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("lscpu | grep -i 'model name' | head -1 | cut -d: -f2 | sed 's/^[ \t]*//'").strip()
    kernel = subprocess.getoutput("uname -sr")
    ram_t = subprocess.getoutput("free -h | grep Mem | awk '{print $2}'").strip()
    ram_u = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    uptime = subprocess.getoutput("uptime -p").replace("up ", "")
    print(f"{Colors.BOLD}SERIAL:{Colors.ENDC} {serial}")
    print(f"{Colors.BOLD}CPU:{Colors.ENDC} {cpu}")
    print(f"{Colors.BOLD}KERNEL:{Colors.ENDC} {kernel}")
    print(f"{Colors.BOLD}RAM:{Colors.ENDC} {ram_u} en uso / {ram_t} total")
    print(f"{Colors.BOLD}UPTIME:{Colors.ENDC} {uptime}")

def audit_security():
    print(f"\n{Colors.WARNING}--- AUDITORÍA DE PUERTOS (TCP/UDP LISTEN) ---{Colors.ENDC}")
    os.system("sudo ss -tunlp | grep LISTEN")

def maintenance():
    print(f"\n{Colors.INFO}Iniciando mantenimiento optimizado...{Colors.ENDC}")
    if "APT" in PKG_MANAGER:
        os.system("sudo apt update && sudo apt autoremove -y && sudo apt autoclean")
    print(f"{Colors.SUCCESS}Mantenimiento finalizado.{Colors.ENDC}")

def battery_storage():
    print(f"\n{Colors.INFO}--- SALUD DE BATERÍA Y DISCOS ---{Colors.ENDC}")
    os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'state|to\ full|percentage|capacity'")
    print(f"\n{Colors.BOLD}Espacio en Disco:{Colors.ENDC}")
    os.system("df -h | grep '^/dev/'")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"{Colors.BOLD}1.{Colors.ENDC} Auditoría de Hardware e Identidad")
        print(f"{Colors.BOLD}2.{Colors.ENDC} Actualizar Sistema (Auto-Detect)")
        print(f"{Colors.BOLD}3.{Colors.ENDC} Mantenimiento y Purga de Residuos")
        print(f"{Colors.BOLD}4.{Colors.ENDC} Monitor de Procesos (HTOP)")
        print(f"{Colors.BOLD}5.{Colors.ENDC} Auditoría de Seguridad (Puertos)")
        print(f"{Colors.BOLD}6.{Colors.ENDC} Salud de Batería y Almacenamiento")
        print(f"{Colors.BOLD}0.{Colors.ENDC} Salir")
        
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")
        if op == "1": get_sys_info()
        elif op == "2" or op == "3": maintenance()
        elif op == "4": os.system("htop")
        elif op == "5": audit_security()
        elif op == "6": battery_storage()
        elif op == "0": break
        input(f"\n{Colors.INFO}Presione Enter para continuar...{Colors.ENDC}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Error: Ejecutar con sudo.{Colors.ENDC}")
        sys.exit(1)
    main()
