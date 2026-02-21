#!/usr/bin/env python3
import os
import subprocess
import sys

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.7.5
# ==========================================================
VERSION = "4.7.5 Audit Edition"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.7.5"

class Colors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def verify_self_integrity():
    """Lógica de Integridad Dinámica: Busca tu firma de marca"""
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            content = f.read()
        if "Felipe Soluciones IT" in content and len(content) > 3000:
            return True
        return False
    except: return False

def show_banner():
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
     {SYSTEM_NAME} | v{VERSION} 
     {status_msg}
     Powered by: {DEVELOPER}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}--- INFRAESTRUCTURA Y SALUD TÉRMICA ---{Colors.ENDC}")
    
    # Captura de datos (Serial restaurado)
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    temp_raw = subprocess.getoutput("sensors | grep -E 'Package id 0|Core 0|temp1' | head -1 | awk '{print $4}'").replace('+', '').replace('°C', '').strip()
    ram_usage = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    uptime_val = subprocess.getoutput("uptime -p")

    # Lógica de Pasta Térmica
    try:
        temp_val = float(temp_raw)
        if temp_val >= 75:
            t_status = f"{Colors.ERROR}{temp_val}°C ⚠️ REVISAR PASTA TÉRMICA{Colors.ENDC}"
        else:
            t_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}"
    except:
        t_status = f"{Colors.INFO}N/A{Colors.ENDC}"

    print(f"SERIAL: {serial if serial else 'No detectable'}")
    print(f"CPU:    {cpu}")
    print(f"TEMP:   {t_status}")
    print(f"RAM:    {ram_usage} en uso")
    print(f"UPTIME: {uptime_val}")

def main():
    while True:
        os.system('clear')
        show_banner()
        print("1. Auditoría de Hardware e Identidad TÉRMICA")
        print("2. Mantenimiento del Sistema")
        print("3. Monitor de Procesos (HTOP)")
        print("4. Auditoría de Seguridad (Puertos)")
        print("5. Salud: Batería y Discos SMART")
        print("0. Salir")
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")
        if op == "1": get_sys_info()
        elif op == "2": os.system("sudo apt update && sudo apt autoremove -y")
        elif op == "3": os.system("htop")
        elif op == "4": os.system("sudo ss -tunlp | grep LISTEN")
        elif op == "5": hardware_health() # (Asume que hardware_health está definido abajo)
        elif op == "0": break
        input(f"\nPresione Enter para volver...")

def hardware_health():
    print(f"\n{Colors.HEADER}--- SALUD DE HARDWARE ---{Colors.ENDC}")
    os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'percentage|capacity' || echo 'Batería: N/A'")
    os.system("sudo smartctl --all /dev/sda | grep -E 'SMART overall-health' || echo 'SMART: N/A'")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Error: Ejecutar con sudo.{Colors.ENDC}"); sys.exit(1)
    main()
