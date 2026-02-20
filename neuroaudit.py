#!/usr/bin/env python3
import os
import subprocess
import datetime
import sys
import socket

# ==========================================================
# CONFIGURACIÓN TÉCNICA - NEUROAUDIT Universal
# ==========================================================
VERSION = "4.4 Universal"
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

# Diccionario de comandos por gestor de paquetes
PACKAGE_COMMANDS = {
    "APT": {
        "update": "sudo apt-get update && sudo apt-get upgrade -y",
        "clean": "sudo apt-get autoremove -y -qq && sudo apt-get autoclean -qq && sudo dpkg --purge $(dpkg -l | grep '^rc' | awk '{print $2}') 2>/dev/null"
    },
    "DNF": {
        "update": "sudo dnf upgrade -y",
        "clean": "sudo dnf autoremove -y && sudo dnf clean all"
    },
    "PACMAN": {
        "update": "sudo pacman -Syu --noconfirm",
        "clean": "sudo pacman -Sc --noconfirm && sudo pacman -Rns $(pacman -Qdtq) 2>/dev/null"
    }
}

def get_package_manager():
    if os.path.exists("/usr/bin/apt-get"): return "APT"
    if os.path.exists("/usr/bin/dnf"): return "DNF"
    if os.path.exists("/usr/bin/pacman"): return "PACMAN"
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
    {Colors.ENDC}{Colors.BOLD} {SYSTEM_NAME} | v{VERSION} 
     Powered by: {DEVELOPER} | Modo: {PKG_MANAGER}{Colors.ENDC}
    """
    print(banner)

def logger(message, type="INFO"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"{getattr(Colors, type)}[{timestamp}] {message}{Colors.ENDC}")

# --- FUNCIONES DE MANTENIMIENTO MULTIPLATAFORMA ---

def sys_update():
    if PKG_MANAGER == "UNKNOWN":
        logger("No se detectó un gestor de paquetes compatible para actualización automática.", "ERROR")
        return
    
    cmd = PACKAGE_COMMANDS[PKG_MANAGER]["update"]
    logger(f"Iniciando actualización del sistema usando {PKG_MANAGER}...", "INFO")
    subprocess.run(cmd, shell=True)
    logger("Proceso de actualización finalizado.", "SUCCESS")

def maintenance():
    if PKG_MANAGER == "UNKNOWN":
        logger("No se detectó un gestor de paquetes compatible para limpieza.", "ERROR")
        return

    cmd = PACKAGE_COMMANDS[PKG_MANAGER]["clean"]
    logger(f"Iniciando tareas de limpieza profunda ({PKG_MANAGER})...", "INFO")
    subprocess.run(cmd, shell=True)
    logger("Mantenimiento y purga de residuos completados.", "SUCCESS")

# --- FUNCIONES UNIVERSALES (HARDWARE / RED) ---

def get_sys_info():
    print(f"\n{Colors.BOLD}{'='*65}{Colors.ENDC}")
    print(f"{Colors.HEADER}       REPORTES DE INFRAESTRUCTURA TÉCNICA{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*65}{Colors.ENDC}")
    serial = subprocess.getoutput("sudo dmidecode -s system-serial-number").strip()
    cpu = subprocess.getoutput("lscpu | grep -i 'model name' | head -1 | cut -d: -f2 | sed 's/^[ \t]*//'").strip()
    if not cpu: cpu = subprocess.getoutput("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
    ram_t = subprocess.getoutput("free -h | grep Mem | awk '{print $2}'").strip()
    ram_u = subprocess.getoutput("free -h | grep Mem | awk '{print $3}'").strip()
    ram_l = subprocess.getoutput("free -h | grep Mem | awk '{print $4}'").strip()
    ip_loc = subprocess.getoutput("hostname -I | awk '{print $1}'").strip()
    uptime = subprocess.getoutput("uptime -p").replace("up ", "")
    
    print(f"{Colors.BOLD}ID DISPOSITIVO:{Colors.ENDC}  {serial if serial else 'N/A'}")
    print(f"{Colors.BOLD}PROCESADOR:{Colors.ENDC}      {cpu if cpu else 'Generic CPU'}")
    print(f"{Colors.BOLD}MEMORIA RAM:{Colors.ENDC}     {ram_t} (Uso: {ram_u} / Disponible: {ram_l})")
    print(f"{Colors.BOLD}DIRECCIÓN IP:{Colors.ENDC}    {ip_loc}")
    print(f"{Colors.BOLD}TIEMPO ACTIVO:{Colors.ENDC}   {uptime}")
    print(f"{Colors.BOLD}PLATAFORMA:{Colors.ENDC}      {os.uname().sysname} {os.uname().release}")
    print(f"{Colors.BOLD}{'='*65}{Colors.ENDC}")

def audit_ports():
    logger("Escaneando sockets locales activos...", "WARNING")
    print(f"\n{'PROTO':<10} {'PUERTO':<12} {'SERVICIO'}")
    print("-" * 35)
    output = subprocess.getoutput("sudo ss -tunlp | grep LISTEN | awk '{print $1, $5}'")
    for line in output.split('\n'):
        line = line.strip()
        if not line: continue
        parts = line.split()
        if len(parts) >= 2:
            proto = parts[0].upper()
            raw_port = parts[1].split(':')[-1]
            try:
                service = socket.getservbyport(int(raw_port), proto.lower())
            except: service = "N/A"
            print(f"{Colors.SUCCESS}{proto:<10} {raw_port:<12} [{service.upper()}]{Colors.ENDC}")

def monitor_storage_health():
    print(f"\n{Colors.WARNING}--- UNIDADES DE DISCO FÍSICAS ---{Colors.ENDC}")
    print(f"{'DISCO':<12} {'TAMAÑO':<10} {'USADO':<10} {'DISP':<10} {'MOUNT'}")
    output = subprocess.getoutput("df -h | grep -E '^/dev/sd|^/dev/nvme'")
    print(output)
    print(f"\n{Colors.WARNING}--- ESTADO DE BATERÍA ---{Colors.ENDC}")
    bat_path = subprocess.getoutput("upower -e | grep 'BAT'").strip()
    if bat_path:
        state = subprocess.getoutput(f"upower -i {bat_path} | grep 'state' | awk '{{print $2}}'")
        perc = subprocess.getoutput(f"upower -i {bat_path} | grep 'percentage' | awk '{{print $2}}'")
        cap = subprocess.getoutput(f"upower -i {bat_path} | grep 'capacity' | awk '{{print $2}}' | tr -d '%' | tr ',' '.'")
        print(f"Estado: {state.capitalize()} | Carga: {perc}")
        try:
            val = float(cap)
            color = Colors.SUCCESS if val > 75 else Colors.WARNING if val > 50 else Colors.ERROR
            status = "SALUDABLE" if val > 75 else "DESGASTADA" if val > 50 else "CRÍTICA"
            print(f"Salud (Capacidad Real): {color}{val}% [{status}]{Colors.ENDC}")
        except: print(f"Capacidad: {cap}%")
    else: print("Batería no detectada.")

def monitor_processes():
    print(f"\n{Colors.WARNING}--- CONSUMO DE RECURSOS CRÍTICOS (RAM) ---{Colors.ENDC}")
    print(subprocess.getoutput("ps aux --sort=-%mem | head -6 | tail -n +2 | awk '{print $2, $4, $11}'"))

# --- MENÚ PRINCIPAL ---

def main():
    while True:
        os.system('clear')
        show_banner()
        print(f"{Colors.BOLD}1.{Colors.ENDC} Auditoría de Hardware e Identidad")
        print(f"{Colors.BOLD}2.{Colors.ENDC} Actualizar Sistema (Auto-Detect)")
        print(f"{Colors.BOLD}3.{Colors.ENDC} Mantenimiento y Purga de Residuos")
        print(f"{Colors.BOLD}4.{Colors.ENDC} Monitor de Procesos en Tiempo Real")
        print(f"{Colors.BOLD}5.{Colors.ENDC} Auditoría de Seguridad (Puertos)")
        print(f"{Colors.BOLD}6.{Colors.ENDC} Salud de Batería y Almacenamiento")
        print(f"{Colors.BOLD}0.{Colors.ENDC} Salir")
        
        op = input(f"\n{Colors.INFO}Seleccione operación: {Colors.ENDC}")

        if op == "1": get_sys_info()
        elif op == "2": sys_update()
        elif op == "3": maintenance()
        elif op == "4": monitor_processes()
        elif op == "5": audit_ports()
        elif op == "6": monitor_storage_health()
        elif op == "0": break
        input(f"\nPresione {Colors.BOLD}ENTER{Colors.ENDC} para continuar...")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print(f"{Colors.ERROR}ERROR: Se requiere privilegios SUDO.{Colors.ENDC}")
        sys.exit(1)
    main()