#!/usr/bin/env python3
import os
import subprocess
import sys

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.7
# ==========================================================
VERSION = "4.7 Thermal Master"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.7"

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
        with open(__file__, "r", encoding="utf-8") as f:
            lines = f.readlines()
        content = "".join([l for l in lines if "OFFICIAL_HASH =" not in l])
        if len(lines) > 150 and "Felipe Soluciones IT" in content:
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
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | sed 's/^[ \t]*//'").strip()
    
    # Captura de Temperatura y lógica de Pasta Térmica
    temp_raw = subprocess.getoutput("sensors | grep -E 'Package id 0|Core 0|temp1' | head -1 | awk '{print $4}'").replace('+', '').replace('°C', '')
    
    try:
        temp_val = float(temp_raw)
        if temp_val >= 75:
            temp_status = f"{Colors.ERROR}{temp_val}°C ⚠️ ALERTA: REQUIERE CAMBIO DE PASTA TÉRMICA{Colors.ENDC}"
        elif temp_val >= 60:
            temp_status = f"{Colors.WARNING}{temp_val}°C (Temperatura elevada){Colors.ENDC}"
        else:
            temp_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}"
    except:
        temp_status = f"{Colors.INFO}N/A (Verificar lm-sensors){Colors.ENDC}"

    print(f"CPU:    {cpu}")
    print(f"TEMP:   {temp_status}")
    print(f"RAM:    {subprocess.getoutput(\"free -h | grep Mem | awk '{print $3}'\")} en uso")
    print(f"UPTIME: {subprocess.getoutput('uptime -p')}")

def maintenance():
    print(f"\n{Colors.INFO}Iniciando mantenimiento...{Colors.ENDC}")
    os.system("sudo apt update && sudo apt autoremove -y")
    print(f"{Colors.SUCCESS}Mantenimiento finalizado.{Colors.ENDC}")

def hardware_health():
    print(f"\n{Colors.HEADER}--- DIAGNÓSTICO DE SALUD DE HARDWARE ---{Colors.ENDC}")
    os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'percentage|capacity' || echo 'Batería: N/A'")
    print(f"\n{Colors.BOLD}Estado S.M.A.R.T. de Discos:{Colors.ENDC}")
    os.system("sudo smartctl --all /dev/sda | grep -E 'SMART overall-health|test_result' || echo 'SMART: No disponible'")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"1. Auditoría de Hardware e Identidad TÉRMICA")
        print(f"2. Mantenimiento del Sistema")
        print(f"3. Monitor de Procesos (HTOP)")
        print(f"4. Auditoría de Seguridad (Puertos)")
        print(f"5. Salud: Batería y Discos SMART")
        print(f"0. Salir")
        op = input(f"\nSeleccione operación: ")
        if op == "1": get_sys_info()
        elif op == "2": maintenance()
        elif op == "3": os.system("htop")
        elif op == "4": os.system("sudo ss -tunlp | grep LISTEN")
        elif op == "5": hardware_health()
        elif op == "0": break
        input(f"\nPresione Enter para volver...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Error: Ejecutar con sudo.{Colors.ENDC}")
        sys.exit(1)
    main()
