#!/usr/bin/env python3
import os
import subprocess
import sys
import re

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.8.1
# ==========================================================
VERSION = "4.8.1 Thermal Hardened"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"

class Colors:
    HEADER, SUCCESS, INFO = '\033[95m', '\033[92m', '\033[94m'
    WARNING, ERROR, ENDC, BOLD = '\033[93m', '\033[91m', '\033[0m', '\033[1m'

def verify_self_integrity():
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            content = f.read()
        return "Felipe Soluciones IT" in content and len(content) > 3500
    except: return False

def show_banner():
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
     Powered by: {DEVELOPER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}--- INFRAESTRUCTURA Y SALUD TÉRMICA ---{Colors.ENDC}")
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    
    # NUEVA CAPTURA DE FUERZA BRUTA (v4.8.1)
    # Filtramos la salida de sensors buscando el Package o temp1 y extraemos el número con Regex puro de Python
    try:
        sensors_output = subprocess.getoutput("sensors")
        # Buscamos una línea que tenga Package o temp1 y luego un número decimal
        match = re.search(r"(?:Package id 0|temp1|Core 0):\s+[\+\-]?(\d+\.\d+)", sensors_output)
        if match:
            temp_val = float(match.group(1))
            if temp_val >= 75:
                t_status = f"{Colors.ERROR}{temp_val}°C ⚠️ REVISAR PASTA TÉRMICA{Colors.ENDC}"
            elif temp_val >= 60:
                t_status = f"{Colors.WARNING}{temp_val}°C (Elevada){Colors.ENDC}"
            else:
                t_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}"
        else:
            t_status = f"{Colors.INFO}N/A (No detectado){Colors.ENDC}"
    except:
        t_status = f"{Colors.INFO}N/A (Error){Colors.ENDC}"

    ram = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    print(f"SERIAL: {serial if serial else 'No detectable'}")
    print(f"CPU:    {cpu}")
    print(f"TEMP:   {t_status}")
    print(f"RAM:    {ram} en uso")
    print(f"UPTIME: {subprocess.getoutput('uptime -p')}")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"{Colors.BOLD}1.{Colors.ENDC} Auditoría de Hardware e Identidad TÉRMICA")
        print(f"{Colors.BOLD}2.{Colors.ENDC} Mantenimiento y Actualización")
        print(f"{Colors.BOLD}3.{Colors.ENDC} Monitor de Procesos (HTOP)")
        print(f"{Colors.BOLD}4.{Colors.ENDC} Auditoría de Seguridad (Puertos)")
        print(f"{Colors.BOLD}5.{Colors.ENDC} SALUD: Batería, Discos y SMART")
        print(f"0. Salir")
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")
        if op == "1": get_sys_info()
        elif op == "2": os.system("sudo apt update && sudo apt autoremove -y")
        elif op == "3": os.system("htop")
        elif op == "4": os.system("sudo ss -tunlp | grep LISTEN")
        elif op == "5": 
            print(f"\n{Colors.HEADER}--- SALUD ---{Colors.ENDC}")
            os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'percentage|capacity'")
            os.system("sudo smartctl --all /dev/nvme0n1 | grep -E 'overall-health' || sudo smartctl --all /dev/sda | grep -E 'overall-health'")
        elif op == "0": break
        input(f"\nPresione Enter para volver...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Ejecutar con sudo.{Colors.ENDC}"); sys.exit(1)
    main()
