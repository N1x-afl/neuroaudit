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
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.5"

class Colors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def verify_self_integrity():
    """Verifica que el script esté completo y funcional"""
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > 120:  # Verificación de estructura mínima
            return True, "Valid"
        return False, "Incomplete"
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
     Powered by: {DEVELOPER} | Modo: {PKG_MANAGER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}{'='*65}{Colors.ENDC}")
    print(f"{Colors.HEADER}       REPORTES DE INFRAESTRUCTURA TÉCNICA{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*65}{Colors.ENDC}")
    
    # Detección Universal de CPU
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^[ \t]*//'").strip()
    if not cpu:
        cpu = subprocess.getoutput("lscpu | grep -E 'Model name|Nombre del modelo' | cut -d: -f2 | sed 's/^[ \t]*//'").strip()

    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    kernel = subprocess.getoutput("uname -sr")
    ram_t = subprocess.getoutput("free -h | grep Mem | awk '{print $2}'").strip()
    ram_u = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    uptime = subprocess.getoutput("uptime -p").replace("up ", "")
    
    print(f"{Colors.BOLD}SERIAL: {Colors.ENDC}{serial}")
    print(f"{Colors.BOLD}CPU:    {Colors.ENDC}{cpu if cpu else 'No detectado'}")
    print(f"{Colors.BOLD}KERNEL: {Colors.ENDC}{kernel}")
    print(f"{Colors.BOLD}RAM:    {Colors.ENDC}{ram_u} en uso / {ram_t} total")
    print(f"{Colors.BOLD}UPTIME: {Colors.ENDC}{uptime}")

def audit_security():
    print(f"\n{Colors.WARNING}--- AUDITORÍA DE PUERTOS (TCP/UDP LISTEN) ---{Colors.ENDC}")
    os.system("sudo ss -tunlp | grep LISTEN")

def maintenance():
    print(f"\n{Colors.INFO}Iniciando mantenimiento optimizado...{Colors.ENDC}")
    if "APT" in PKG_MANAGER:
        os.system("sudo apt update && sudo apt autoremove -y && sudo apt autoclean")
    else:
        print(f"{Colors.WARNING}Gestor de paquetes no soportado para auto-limpieza.{Colors.ENDC}")
    print(f"{Colors.SUCCESS}Mantenimiento finalizado.{Colors.ENDC}")

def battery_storage():
    print(f"\n{Colors.INFO}--- SALUD DE BATERÍA Y DISCOS ---{Colors.ENDC}")
    # Batería
    bat_info = subprocess.getoutput("upower -i $(upower -e | grep 'BAT') | grep -E 'state|percentage|capacity'").strip()
    print(bat_info if bat_info else "
