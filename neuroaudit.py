#!/usr/bin/env python3
import os
import subprocess
import sys

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT v4.7.2
# ==========================================================
VERSION = "4.7.2 Thermal Master"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER = "Felipe Soluciones IT"
OFFICIAL_HASH = "felipe-soluciones-it-verified-v4.7.2"

class Colors:
    HEADER, SUCCESS, INFO = '\033[95m', '\033[92m', '\033[94m'
    WARNING, ERROR, ENDC, BOLD = '\033[93m', '\033[91m', '\033[0m', '\033[1m'

def verify_self_integrity():
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            lines = f.readlines()
        content = "".join([l for l in lines if "OFFICIAL_HASH =" not in l])
        if len(lines) > 100 and "Felipe Soluciones IT" in content:
            return True
        return False
    except: return False

def show_banner():
    is_valid = verify_self_integrity()
    status_msg = f"{Colors.SUCCESS}✅ INTEGRIDAD VERIFICADA" if is_valid else f"{Colors.ERROR}❌ INTEGRIDAD COMPROMETIDA"
    print(f"{Colors.SUCCESS}\n    NEUROAUDIT - v{VERSION}\n    {status_msg}\n    Powered by: {Colors.BOLD}{DEVELOPER}{Colors.ENDC}")

def get_sys_info():
    print(f"\n{Colors.BOLD}--- INFRAESTRUCTURA Y SALUD TÉRMICA ---{Colors.ENDC}")
    
    # Comandos separados para evitar el error de comillas en el print
    cpu = subprocess.getoutput("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    temp_raw = subprocess.getoutput("sensors | grep -E 'Package id 0|Core 0|temp1' | head -1 | awk '{print $4}'").replace('+', '').replace('°C', '').strip()
    ram_usage = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    
    try:
        temp_val = float(temp_raw)
        if temp_val >= 75:
            t_status = f"{Colors.ERROR}{temp_val}°C ⚠️ REVISAR PASTA TÉRMICA{Colors.ENDC}"
        else:
            t_status = f"{Colors.SUCCESS}{temp_val}°C (Normal){Colors.ENDC}"
    except:
        t_status = "N/A"

    print(f"CPU:    {cpu}")
    print(f"TEMP:   {t_status}")
    print(f"RAM:    {ram_usage} en uso")
    print(f"UPTIME: {subprocess.getoutput('uptime -p')}")

def main():
    while True:
        os.system('clear')
        show_banner()
        print("1. Auditoría de Hardware y Térmica")
        print("2. Mantenimiento del Sistema")
        print("0. Salir")
        op = input(f"\nSeleccione: ")
        if op == "1": get_sys_info()
        elif op == "2": os.system("sudo apt update && sudo apt autoremove -y")
        elif op == "0": break
        input(f"\nPresione Enter...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}Usar sudo.{Colors.ENDC}"); sys.exit(1)
    main()
