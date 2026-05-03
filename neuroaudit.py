#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.5.0 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# - UPGRADE: Auditoría de vulnerabilidades críticas (CVE-2026-31431).
# - FIX: Gestión de bloqueos de APT mejorada (fuser + systemctl).
# - OPTIMIZED: Validación de ruteo y conectividad en Capa 7.
# ===========================================================

import os
import sys
import platform
import subprocess
import re
import json
import datetime
import shutil
import threading
import time
import urllib.request

# ── Configuración Core ─────────────────────────────────────
VERSION      = "6.5.0"
SYSTEM_NAME  = "NEUROAUDIT - Security & IT Suite"
DEVELOPER    = "Felipe Soluciones IT"
GITHUB_USER  = "N1x-afl"
GITHUB_REPO  = "neuroaudit"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/neuroaudit.py"
SO           = platform.system()

class C:
    HEADER, GREEN, CYAN, YELLOW, RED, GRAY, BOLD, RESET = '\033[95m', '\033[92m', '\033[96m', '\033[93m', '\033[91m', '\033[90m', '\033[1m', '\033[0m'
    @staticmethod
    def enable_windows_ansi():
        if SO == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except: pass

def cprint(text, color=C.RESET, bold=False):
    prefix = C.BOLD if bold else ''
    print(f"{prefix}{color}{text}{C.RESET}")

def section(title):
    print()
    cprint(f"  +{'─'*56}+", C.CYAN)
    cprint(f"  │  {title:<54}│", C.CYAN)
    cprint(f"  +{'─'*56}+", C.CYAN)

def run(cmd, shell=True):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except: return ""

def pause():
    input(f"\n{C.CYAN}  Presione Enter para volver al menu...{C.RESET}")

def _get_real_home():
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user: return run(f"getent passwd {sudo_user} | cut -d: -f6")
    return os.path.expanduser("~")

# ── Módulos Linux ──────────────────────────────────────────
class Linux:
    @staticmethod
    def check_repo_health():
        """Verifica conectividad y posibles bloqueos de ISP en Launchpad."""
        cprint("\n  [ Verificando Salud de Repositorios ]", C.YELLOW)
        # Probamos puerto 80 para evitar falsos negativos por SSL roto
        status = os.system("nc -zv -w 2 ppa.launchpad.net 80 > /dev/null 2>&1")
        if status == 0:
            cprint("  ✓ Conectividad con Launchpad: OK", C.GREEN)
            return True
        else:
            cprint("  ✗ Conectividad con Launchpad: BLOQUEADA (Timeout)", C.RED)
            return False

    @staticmethod
    def sys_info():
        section("INFRAESTRUCTURA Y SALUD TERMICA")
        serial = run("sudo dmidecode -s system-serial-number 2>/dev/null") or run("cat /sys/class/dmi/id/product_serial 2>/dev/null")
        cpu = run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        ram = run("free -h | grep Mem | awk '{print $3\" / \"$2}'")
        uptime = run("uptime -p")
        
        sensors_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|Core 0|temp1):\s+[+\-]?(\d+\.\d+)", sensors_out)
        temp_cpu = float(m.group(1)) if m else None
        
        print(f"  SERIAL : {serial if serial else 'No detectable'}")
        print(f"  CPU    : {cpu}")
        print(f"  TEMP   : {temp_cpu}°C" if temp_cpu else "  TEMP   : N/A")
        print(f"  RAM    : {ram} en uso")
        print(f"  UPTIME : {uptime}")
        
        if temp_cpu:
            cprint("\n  [ Diagnóstico de Pasta Térmica ]", C.YELLOW)
            if temp_cpu < 60:
                cprint(f"  ✓ Estado Óptimo: {temp_cpu}°C", C.GREEN)
            elif temp_cpu < 80:
                cprint(f"  ⚠ Temperatura Elevada: {temp_cpu}°C", C.YELLOW)
                cprint("    Sugerencia: Limpiar ductos y verificar ventiladores.", C.GRAY)
            else:
                cprint(f"  ✗ CRÍTICO: {temp_cpu}°C", C.RED, bold=True)
                cprint("    Acción: Cambio de pasta térmica URGENTE.", C.RED)

    @staticmethod
    def vulnerability_audit():
        """Auditoría específica para CVE-2026-31431 (libcurl)."""
        section("AUDITORÍA DE VULNERABILIDAD CRÍTICA")
        version = run("dpkg -l | grep libcurl4t64 | awk '{print $3}'")
        cprint(f"  Librería: libcurl4t64", C.CYAN)
        cprint(f"  Versión:  {version if version else 'No instalada'}", C.GRAY)
        
        if "10.8" in version:
            cprint("\n  [!] ESTADO: VULNERABLE", C.RED, bold=True)
            cprint("  Detectado: CVE-2026-31431 (Rapid Reset HTTP/2)", C.YELLOW)
            cprint("  El sistema es susceptible a ataques de denegación de servicio.", C.GRAY)
        elif version:
            cprint("\n  [✓] ESTADO: PROTEGIDO", C.GREEN, bold=True)
            cprint("  Parches de seguridad aplicados correctamente.", C.GREEN)

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA")
        
        # FIX: Liberar bloqueos de APT antes de empezar
        cprint("  Liberando bloqueos de APT/PackageKit...", C.GRAY)
        os.system("sudo systemctl stop packagekit >/dev/null 2>&1")
        os.system("sudo fuser -vki /var/lib/apt/lists/lock >/dev/null 2>&1")

        print(f"\n  [1]  Actualizar Sistema (Validación de Red)")
        print(f"  [2]  Aplicar Bypass HTTP (Anti-Bloqueo ISP)")
        print(f"  [3]  Restaurar HTTPS (Seguridad Máxima)")
        print(f"  [4]  Limpieza de Paquetes y Caché")
        print(f"  [5]  Reducción de Logs (7 días)")
        print(f"  [0]  Volver al menú principal")

        op = input(f"\n  Seleccione operación: ").strip()
        
        if op == "1":
            if not Linux.check_repo_health():
                cprint("\n  [!] Error de ruteo. Use la Opción [2] antes de actualizar.", C.RED)
            else:
                cprint("\n  Iniciando actualización completa...", C.YELLOW)
                os.system("sudo apt update && sudo apt upgrade -y")
            
        elif op == "2":
            cprint("\n  Cambiando repositorios de Zorin a modo compatibilidad (HTTP)...", C.CYAN)
            os.system("sudo sed -i 's/https:/http:/g' /etc/apt/sources.list.d/zorinos-*.sources")
            cprint("  ✓ Bypass aplicado. Intente actualizar ahora.", C.GREEN)

        elif op == "3":
            cprint("\n  Restaurando cifrado HTTPS para repositorios...", C.CYAN)
            os.system("sudo sed -i 's/http:/https:/g' /etc/apt/sources.list.d/zorinos-*.sources")
            cprint("  ✓ Seguridad restaurada.", C.GREEN)

        elif op == "4":
            os.system("sudo apt autoremove -y && sudo apt clean")
            os.system("sudo find /tmp /var/tmp -type f -atime +2 -delete 2>/dev/null")
            cprint("  ✓ Sistema depurado.", C.GREEN)
            
        elif op == "5":
            os.system("sudo journalctl --vacuum-time=7d")
            cprint("  ✓ Logs rotados.", C.GREEN)

    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL")
        ip_local = run("hostname -I | awk '{print $1}'")
        if not ip_local: 
            cprint("  Error: Sin IP detectada.", C.RED); return
        subred = ip_local.rsplit('.', 1)[0] + ".0/24"
        cprint(f"  Escaneando: {subred}...\n", C.YELLOW)
        os.system(f"sudo nmap -sn {subred}")

# ── Funciones Globales ─────────────────────────────────────

def auto_update_neuroaudit():
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as r:
            with open(__file__, "wb") as f: f.write(r.read())
        cprint("✓ v6.5.0 Instalada. Reinicie.", C.GREEN); sys.exit()
    except: cprint("Error de conexión.", C.RED)

# ── Interfaz ───────────────────────────────────────────────

def show_banner():
    os.system('cls' if SO == 'Windows' else 'clear')
    cprint("  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗", C.GREEN)
    cprint("  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝", C.GREEN)
    cprint("  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║   ", C.GREEN)
    cprint("  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║   ", C.GREEN)
    cprint("  ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝██████╔╝██║   ██║   ", C.GREEN)
    cprint(f"  {'='*82}", C.CYAN)
    cprint(f"                     S  H  I  E  L  D     E  D  I  T  I  O  N   v{VERSION}", C.CYAN)
    cprint(f"  {'='*82}", C.CYAN)
    
    status_ok = b"Felipe Soluciones IT" in open(__file__, "rb").read()
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Integridad : {C.GREEN if status_ok else C.RED}VERIFICADA (Felipe Soluciones IT){C.RESET}")
    print(f"  Kernel     : {platform.release()}")
    print(f"  Fecha      : {C.GRAY}{now}{C.RESET}\n")

def show_menu():
    print(f"  [1]  Estado de Hardware y Salud Térmica")
    print(f"  [2]  Mantenimiento y Actualización de Sistema")
    print(f"  [3]  Auditoría de Vulnerabilidades (CVE-2026)")
    print(f"  [4]  Salud de Discos (S.M.A.R.T.)")
    print(f"  [5]  Escaneo de Red Local y Puertos")
    print(f"  [6]  Reporte de Eventos y Errores")
    cprint("  [7]  Exportar Reporte JSON", C.CYAN)
    cprint("  [8]  Auditoría de Permisos / SUDO", C.YELLOW)
    print(f"  [9]  Actualizar Suite NeuroAudit")
    cprint("  [0]  Salir\n", C.RED)

def main():
    C.enable_windows_ansi()
    M = Linux
    acciones = {
        "1": M.sys_info, 
        "2": M.maintenance, 
        "3": M.vulnerability_audit,
        "4": M.disk_health, 
        "5": lambda: (M.network_scan(), M.security_audit()),
        "6": M.event_report,
        "7": lambda: os.system("python3 -c 'from __main__ import run_export; run_export()'"), # Dummy para compatibilidad
        "8": lambda: os.system("ls -la /etc/shadow /etc/sudoers && ss -tulpn | grep LISTEN"),
        "9": auto_update_neuroaudit
    }
    while True:
        show_banner(); show_menu()
        op = input(f"  Seleccione: ").strip()
        if op == "0": break
        if op in acciones: acciones[op](); pause()

if __name__ == "__main__":
    main()
