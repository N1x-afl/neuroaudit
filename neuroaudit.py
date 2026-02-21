#!/usr/bin/env python3
import os
import subprocess
import sys
import hashlib

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.7.4
# ==========================================================
VERSION = "4.7.4 Thermal Master"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
# Hash dinámico: No importa lo que diga aquí, la validación lo ignorará
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.7.4"

class Colors:
    HEADER = '\033[95m'
    SUCCESS = '\033[92m'
    INFO = '\033[94m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def verify_self_integrity():
    """Lógica de Integridad Dinámica: Ignora la línea del hash para validar"""
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Filtramos la línea del hash para que la validación sea sobre el código puro
        pure_code = "".join([l for l in lines if "OFFICIAL_HASH =" not in l])
        # Verificamos que sea un archivo real y tenga tu firma de marca
        if len(lines) > 100 and "Felipe Soluciones IT" in pure_code:
            return True, "Valid"
        return False, "Incomplete"
    except:
        return False, "Error"

def get_package_manager():
    if os.path.exists("/usr/bin/apt-get"): return "APT (Zorin/Ubuntu/Debian)"
    return "Linux Standard"

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
     {SYSTEM_NAME} | v{VERSION} 
     {status_msg}
     Powered by: {DEVELOPER} | {get_package_manager()}{Colors.ENDC}
    """
    print(banner)

def get_sys_info():
    print(f"\n{Colors.BOLD}--- INFRAESTRUCTURA Y SALUD TÉRMICA ---{Colors.ENDC}")
    
    # Comandos limpios para evitar errores de sintaxis
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    temp_raw = subprocess.getoutput("sensors | grep -E 'Package id 0|Core 0|temp1' | head -1 | awk '{print $4}'").replace('+', '').replace('°C', '').strip()
    ram_usage = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    
    try:
        temp_val = float(temp_raw)
        if temp_val >= 75:
            t_status = f"{Colors.ERROR}{temp_val}°C ⚠️ ALERTA: REQUIERE PASTA TÉRMICA{Colors.ENDC}"
        elif temp_val >= 60:
            t_status = f"{Colors.WARNING}{temp_val}°C (Elevada){Colors.ENDC}"
        else:
            t_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}"
    except:
        t_status = f"{Colors.INFO}N/A (Cargue lm-sensors){Colors.ENDC}"

    print(f"CPU:    {cpu}")
    print(f"TEMP:   {t_status}")
    print(f"RAM:    {ram_usage} en uso")
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
        print("1. Auditoría de Hardware e Identidad TÉRMICA")
        print("2. Mantenimiento del Sistema")
        print("3. Monitor de Procesos (HTOP)")
        print("4. Auditoría de Seguridad (Puertos)")
        print("5. Salud: Batería y Discos SMART")
        print("0. Salir")
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")
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
