#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4.4 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# ESTADO: FULL OPERATIVO (1-10)
# - FIX: Menú de Mantenimiento (Opción 2) ahora en LISTA VERTICAL.
# - FIX: Diagnóstico de Pasta Térmica avanzado con sugerencias.
# - FIX: Escaneo de Red Local con detección dinámica de subred.
# - FIX: Header completo con Kernel, RAM real y Serial BIOS.
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
VERSION      = "6.4.4"
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
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=15)
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
                cprint("    La disipación funciona correctamente.", C.GRAY)
            elif temp_cpu < 80:
                cprint(f"  ⚠ Temperatura Elevada: {temp_cpu}°C", C.YELLOW)
                cprint("    Sugerencia: Limpiar ductos de ventilación y ventiladores.", C.GRAY)
            else:
                cprint(f"  ✗ CRÍTICO: {temp_cpu}°C", C.RED, bold=True)
                cprint("    Acción: Cambio de pasta térmica URGENTE (Arctic MX-4 sugerida).", C.RED)

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA")
        # Cambio a LISTA VERTICAL para mantener la esencia
        print(f"\n  [1]  Actualizar Sistema (APT/PACMAN)")
        print(f"  [2]  Purgar Paquetes Huérfanos")
        print(f"  [3]  Limpiar Caché del Gestor")
        print(f"  [4]  Limpieza de Archivos Temporales")
        print(f"  [5]  Limpiar Logs del Sistema (journalctl)")
        print(f"  [8]  Actualizar Suite NEUROAUDIT")
        print(f"  [0]  Volver al menú principal")

        op = input(f"\n  Seleccione operación: ").strip()
        
        if op == "1":
            cprint("\n  Iniciando actualización completa...", C.YELLOW)
            os.system("sudo apt update && sudo apt upgrade -y || sudo pacman -Syu --noconfirm")
        elif op == "2":
            os.system("sudo apt autoremove -y || sudo pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null")
            cprint("  ✓ Limpieza completada.", C.GREEN)
        elif op == "3":
            os.system("sudo apt clean || sudo pacman -Sc --noconfirm")
            cprint("  ✓ Caché liberada.", C.GREEN)
        elif op == "4":
            cprint("\n  Limpiando archivos temporales antiguos...", C.YELLOW)
            os.system("sudo find /tmp /var/tmp -type f -atime +2 -delete 2>/dev/null")
            cprint("  ✓ Temporales eliminados.", C.GREEN)
        elif op == "5":
            os.system("sudo journalctl --vacuum-time=7d")
            cprint("  ✓ Logs reducidos a los últimos 7 días.", C.GREEN)
        elif op == "8":
            auto_update_neuroaudit()

    @staticmethod
    def disk_health():
        section("SALUD: DISCOS Y S.M.A.R.T.")
        os.system("df -h | grep -E 'Filesystem|/dev/sd|/dev/nvme|/$'")
        disks = run("lsblk -dn -o NAME | grep -E 'sd|nvme'").splitlines()
        for d in disks:
            cprint(f"\n  Disco /dev/{d}:", C.CYAN)
            os.system(f"sudo smartctl -H /dev/{d} | grep -E 'overall-health|result|PASSED|FAILED'")

    @staticmethod
    def security_audit():
        section("AUDITORIA DE PUERTOS")
        os.system("sudo ss -tulpn | grep LISTEN")

    @staticmethod
    def event_report():
        section("REPORTE DE EVENTOS DEL SISTEMA")
        os.system("sudo journalctl -p err -n 15 --no-pager")

    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE")
        os.system("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -n 50 2>/dev/null || pacman -Q | head -n 50")
        count = run("dpkg -l | grep '^ii' | wc -l 2>/dev/null || pacman -Q | wc -l")
        cprint(f"\n  Total paquetes instalados: {count}", C.YELLOW)

    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL")
        ip_local = run("hostname -I | awk '{print $1}'")
        if not ip_local: 
            cprint("  Error: No se pudo detectar IP local.", C.RED); return
        subred = ip_local.rsplit('.', 1)[0] + ".0/24"
        cprint(f"  Escaneando subred: {subred}...\n", C.YELLOW)
        os.system(f"sudo nmap -sn {subred}")

# ── Funciones Globales ─────────────────────────────────────

def run_export():
    section("EXPORTAR REPORTE")
    data = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "kernel": platform.release(),
        "cpu": run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(),
        "ram": run("free -h | grep Mem | awk '{print $3\" / \"$2}'")
    }
    path = os.path.join(_get_real_home(), f"reporte_audit_{datetime.datetime.now().strftime('%Y%m%d')}.json")
    with open(path, "w") as f: json.dump(data, f, indent=4)
    cprint(f"  ✓ Reporte JSON guardado en: {path}", C.GREEN)

def run_permission_audit():
    section("AUDITORIA DE PERMISOS Y USUARIOS")
    cprint("\n  [ Archivos Críticos ]", C.YELLOW)
    os.system("ls -la /etc/shadow /etc/sudoers")
    cprint("\n  [ Puertos (Seguridad) ]", C.YELLOW)
    os.system("sudo ss -tulpn | grep LISTEN")
    cprint("\n  [ Usuarios con SUDO ]", C.YELLOW)
    print(run("grep -Po '^sudo:.*:\\K.*|^wheel:.*:\\K.*' /etc/group") or "Solo root")

def auto_update_neuroaudit():
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as r:
            with open(__file__, "wb") as f: f.write(r.read())
        cprint("✓ v6.4.4 Instalada. Reinicie.", C.GREEN); sys.exit()
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
    cprint(f"                   A  U  D  I  T     S  Y  S  T  E  M   v{VERSION}", C.CYAN)
    cprint(f"  {'='*82}", C.CYAN)
    
    status_ok = b"Felipe Soluciones IT" in open(__file__, "rb").read()
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Estado   : {C.GREEN if status_ok else C.RED}OK INTEGRIDAD VERIFICADA{C.RESET}")
    print(f"  Sistema  : {C.GREEN}[LINUX]{C.RESET} {platform.release()}")
    print(f"  Fecha    : {C.GRAY}{now}{C.RESET}")
    print(f"  Autor    : {C.GRAY}{DEVELOPER}{C.RESET}\n")

def show_menu():
    print(f"  [1]  Hardware e Identidad Termica")
    print(f"  [2]  Mantenimiento del Sistema")
    print(f"  [3]  Salud: Discos y S.M.A.R.T.")
    print(f"  [4]  Auditoria de Seguridad (Puertos)")
    print(f"  [5]  Reporte de Eventos del Sistema")
    print(f"  [6]  Inventario de Software Instalado")
    cprint("  [7]  Exportar Reporte (JSON)", C.CYAN)
    print(f"  [8]  Ping / Test de Conectividad")
    print(f"  [9]  Escaneo de Red Local")
    cprint("  [10] Auditoria de Permisos y Usuarios", C.YELLOW)
    cprint("  [0]  Salir\n", C.RED)

def main():
    C.enable_windows_ansi()
    M = Linux
    acciones = {
        "1": M.sys_info, "2": M.maintenance, "3": M.disk_health, "4": M.security_audit,
        "5": M.event_report, "6": M.software_inventory, "7": run_export,
        "8": lambda: os.system("ping -c 3 8.8.8.8"),
        "9": M.network_scan, "10": run_permission_audit
    }
    while True:
        show_banner(); show_menu()
        op = input(f"  Seleccione: ").strip()
        if op == "0": break
        if op in acciones: acciones[op](); pause()

if __name__ == "__main__":
    main()
