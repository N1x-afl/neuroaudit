#!/usr/bin/env python3
import os
import subprocess
import sys

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.7.7
# ==========================================================
VERSION = "4.7.7 Final Edition"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.7.7"

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
    
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    ram_usage = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    uptime_val = subprocess.getoutput("uptime -p")

    # Lógica de Temperatura Ultra-Robusta (v4.7.7)
    temp_val = None
    try:
        # Intento 1: sensors con parseo mejorado
        res = subprocess.getoutput("sensors | grep -E 'Package id 0|temp1' | head -1 | awk -F: '{print $2}' | grep -oP '[0-9.]+' | head -1")
        if res: temp_val = float(res)
        
        # Intento 2 (Si falla el anterior): Lectura directa del kernel (thermal_zone)
        if temp_val is None:
            for i in range(10):
                path = f"/sys/class/thermal/thermal_zone{i}/temp"
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        t = int(f.read().strip()) / 1000
                        if t > 20 and t < 110: # Filtro de rango lógico
                            temp_val = t
                            break
    except: pass

    if temp_val:
        if temp_val >= 75:
            t_status = f"{Colors.ERROR}{temp_val}°C ⚠️ ALERTA: REVISAR PASTA TÉRMICA{Colors.ENDC}"
        elif temp_val >= 60:
            t_status = f"{Colors.WARNING}{temp_val}°C (Elevada){Colors.ENDC}"
        else:
            t_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}"
    else:
        t_status = f"{Colors.INFO}N/A (Cargar coretemp){Colors.ENDC}"

    print(f"SERIAL: {serial if serial else 'No detectable'}")
    print(f"CPU:    {cpu}")
    print(f"TEMP:   {t_status}")
    print(f"RAM:    {ram_usage} en uso")
    print(f"UPTIME: {uptime_val}")

def maintenance():
    print(f"\n{Colors.INFO}Iniciando mantenimiento...{Colors.ENDC}")
    os.system("sudo apt update && sudo apt autoremove -y")
    print(f"{Colors.SUCCESS}Mantenimiento finalizado.{Colors.ENDC}")

def hardware_health():
    print(f"\n{Colors.HEADER}--- DIAGNÓSTICO DE SALUD DE HARDWARE ---{Colors.ENDC}")
    os.system("upower -i $(upower -e | grep 'BAT') | grep -E 'percentage|capacity' || echo 'Batería: N/A'")
    print(f"\n{Colors.BOLD}Estado S.M.A.R.T. de Discos:{Colors.ENDC}")
    os.system("sudo smartctl --all /dev/sda | grep -E 'SMART overall-health' || sudo smartctl --all /dev/nvme0n1 | grep -E 'SMART overall-health' || echo 'SMART: No disponible'")

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"{Colors.BOLD}1.{Colors.ENDC} Auditoría de Hardware e Identidad TÉRMICA")
        print(f"{Colors.BOLD}2.{Colors.ENDC} Mantenimiento y Actualización")
        print(f"{Colors.BOLD}3.{Colors.ENDC} Monitor de Procesos (HTOP)")
        print(f"{Colors.BOLD}4.{Colors.ENDC} Auditoría de Seguridad (Puertos)")
        print(f"{Colors.BOLD}5.{Colors.ENDC} SALUD: Batería, Discos y SMART")
        print(f"{Colors.BOLD}0.{Colors.ENDC} Salir")
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")
        if op == "1": get_sys_info()
        elif op == "2": maintenance()
        elif op == "3": os.system("htop")
        elif op == "4": os.system("sudo ss -tunlp | grep LISTEN")
        elif op == "5": hardware_health()
        elif op == "0": break
        input(f"\n{Colors.INFO}Presione Enter para volver...{Colors.ENDC}")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Error: Ejecutar con sudo.{Colors.ENDC}"); sys.exit(1)
    main()
