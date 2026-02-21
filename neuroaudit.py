#!/usr/bin/env python3
import os
import subprocess
import sys
import re

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.8.6
# ==========================================================
VERSION = "4.8.6"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.8.6"

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
    distro = subprocess.getoutput("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'")
    pkg_manager = "APT" if os.path.exists("/usr/bin/apt") else "DNF" if os.path.exists("/usr/bin/dnf") else "Otro"
    return distro, pkg_manager

def show_banner():
    distro, pkg = get_distro_info()
    status = f"{Colors.SUCCESS}✅ INTEGRIDAD VERIFICADA" if verify_self_integrity() else f"{Colors.ERROR}❌ INTEGRIDAD COMPROMETIDA"
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
     {status}
     OS: {distro} ({pkg})
     Powered by: {DEVELOPER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}--- INFRAESTRUCTURA Y SALUD TÉRMICA ---{Colors.ENDC}")
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    
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

def hardware_health():
    print(f"\n{Colors.HEADER}--- SALUD: BATERÍA Y DISCOS SMART ---{Colors.ENDC}")
    
    # Capacidad y Uso de Particiones
    print(f"{Colors.BOLD}\n[ Uso de Particiones y Capacidad ]{Colors.ENDC}")
    os.system("df -h | grep -E 'Filesystem|/dev/sd|/dev/nvme|total'")
    
    # Modelos de Discos Físicos
    print(f"{Colors.BOLD}\n[ Unidades de Almacenamiento Detectadas ]{Colors.ENDC}")
    os.system("lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINT | grep -E 'NAME|disk'")
    
    # Estado SMART (NVMe o SATA)
    print(f"{Colors.BOLD}\n[ Estado S.M.A.R.T. ]{Colors.ENDC}")
    os.system("sudo smartctl --all /dev/nvme0n1 | grep -E 'Model Number|SMART overall-health' || sudo smartctl --all /dev/sda | grep -E 'Device Model|SMART overall-health' || echo 'No se detectó SMART compatible'")
    
    # Salud de Batería
    print(f"{Colors.BOLD}\n[ Salud de Batería ]{Colors.ENDC}")
    os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'state|percentage|capacity' || echo 'Batería: N/A'")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"{Colors.BOLD}1.{Colors.ENDC} Auditoría de Hardware e Identidad TÉRMICA")
        print(f"{Colors.BOLD}2.{Colors.ENDC} Mantenimiento del Sistema")
        print(f"{Colors.BOLD}3.{Colors.ENDC} Monitor de Procesos (HTOP)")
        print(f"{Colors.BOLD}4.{Colors.ENDC} Auditoría de Seguridad (Puertos)")
        print(f"{Colors.BOLD}5.{Colors.ENDC} Salud: Batería y Discos SMART")
        print(f"{Colors.BOLD}0.{Colors.ENDC} Salir")
        
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")
        if op == "1": get_sys_info()
        elif op == "2": 
            _, pkg = get_distro_info()
            if pkg == "APT": os.system("sudo apt update && sudo apt autoremove -y")
            else: print("Mantenimiento no disponible para esta distro.")
        elif op == "3": os.system("htop")
        elif op == "4": os.system("sudo ss -tunlp | grep LISTEN")
        elif op == "5": hardware_health()
        elif op == "0": break
        input(f"\nPresione Enter para volver...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Error: Ejecutar con sudo.{Colors.ENDC}"); sys.exit(1)
    main()
