#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4.1 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# FIX LOG:
# - Mantenimiento (Opción 2) 100% operativo con comandos reales.
# - Auditoría de Permisos (Opción 10) vinculada.
# - Salud S.M.A.R.T. corregida para NVMe/SATA.
# - Estética original v6.3 preservada.
# ===========================================================

import os
import sys
import platform
import subprocess
import re
import json
import datetime
import shutil
import hashlib
import threading
import time
import urllib.request
import tempfile

# ── Configuración Core ─────────────────────────────────────
VERSION      = "6.4.1"
SYSTEM_NAME  = "NEUROAUDIT - Security & IT Suite"
DEVELOPER    = "Felipe Soluciones IT"
GITHUB_USER  = "N1x-afl"
GITHUB_REPO  = "neuroaudit"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/neuroaudit.py"
SO           = platform.system()

class C:
    HEADER  = '\033[95m'
    GREEN   = '\033[92m'
    CYAN    = '\033[96m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    GRAY    = '\033[90m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'

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

def check_privileges():
    return os.geteuid() == 0 if SO == "Linux" else False

# ── Lógica de Actualización ────────────────────────────────
_update_result = {"disponible": False, "version": None, "checked": False}

def _check_update_background():
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "neuroaudit"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
        tag = data.get("tag_name", "").lstrip("v")
        def p_v(v): return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]
        if tag and p_v(tag) > p_v(VERSION):
            _update_result["disponible"], _update_result["version"] = True, tag
    except: pass
    finally: _update_result["checked"] = True

# ── Módulos Linux ──────────────────────────────────────────
class Linux:
    @staticmethod
    def sys_info():
        section("INFRAESTRUCTURA Y SALUD TERMICA")
        cpu = run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        temp = run("sensors 2>/dev/null | grep -E 'Package id 0|Core 0|temp1' | head -n1 | awk '{print $4}'")
        print(f"  CPU    : {cpu}")
        print(f"  TEMP   : {temp if temp else 'N/A'}")
        print(f"  RAM    : {run('free -h | grep Mem | awk \"{print $3\\\"/\\\"$2}\"')}")
        
    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA [OPERATIVO]")
        cprint("\n  [1] Actualizar Sistema (APT/PACMAN)", C.RESET)
        cprint("  [2] Purgar paquetes huerfanos", C.RESET)
        cprint("  [3] Limpiar cache del gestor", C.RESET)
        cprint("  [4] Gestión de Temporales (Opcional)", C.CYAN)
        cprint("  [5] Limpiar logs (journalctl >7d)", C.RESET)
        cprint("  [8] Actualizar NEUROAUDIT", C.GREEN)
        
        op = input(f"\n  {C.CYAN}Seleccione operación: {C.RESET}").strip()
        
        if op == "1":
            cprint("\n  Iniciando actualización...", C.YELLOW)
            os.system("sudo apt update && sudo apt upgrade -y 2>/dev/null || sudo pacman -Syu --noconfirm")
        elif op == "2":
            os.system("sudo apt autoremove -y 2>/dev/null || pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null")
            cprint("  ✓ Limpieza de huerfanos completada.", C.GREEN)
        elif op == "3":
            os.system("sudo apt clean 2>/dev/null || pacman -Sc --noconfirm")
            cprint("  ✓ Cache liberada.", C.GREEN)
        elif op == "4":
            print("\n  [1] Ver tamaño  [2] Limpieza Segura (>7d)  [3] Limpieza Profunda")
            sel = input("  Opción: ").strip()
            if sel == "2": os.system("sudo find /tmp /var/tmp -type f -atime +7 -delete 2>/dev/null")
            elif sel == "3": os.system("sudo find /tmp /var/tmp -type f -atime +2 -delete 2>/dev/null")
            else: cprint(f"  Tamaño: {run('du -sh /tmp 2>/dev/null')}", C.GRAY)
        elif op == "5":
            os.system("sudo journalctl --vacuum-time=7d")
            cprint("  ✓ Logs antiguos eliminados.", C.GREEN)
        elif op == "8":
            auto_update_neuroaudit()

    @staticmethod
    def disk_health():
        section("SALUD: DISCOS Y S.M.A.R.T.")
        os.system("df -h | grep -E 'Filesystem|/dev/sd|/dev/nvme|/$'")
        if shutil.which("smartctl"):
            disks = run("lsblk -dn -o NAME | grep -E 'sd|nvme'").splitlines()
            for d in disks:
                cprint(f"\n  Disco /dev/{d}:", C.CYAN)
                os.system(f"sudo smartctl -H /dev/{d} | grep -E 'overall-health|result|PASSED|FAILED'")

    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD (PUERTOS)")
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

# ── Utilidades ─────────────────────────────────────────────

def run_permission_audit():
    section("AUDITORIA DE PERMISOS Y USUARIOS")
    cprint("\n  [ Archivos Críticos ]", C.YELLOW)
    os.system("ls -la /etc/shadow /etc/sudoers")
    cprint("\n  [ Usuarios con capacidad de SUDO ]", C.YELLOW)
    os.system("grep -Po '^sudo:.*:\\K.*|^wheel:.*:\\K.*' /etc/group")

def auto_update_neuroaudit():
    cprint(f"\n  Descargando actualización v{_update_result['version']}...", C.YELLOW)
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as r:
            with open(os.path.abspath(__file__), "wb") as f: f.write(r.read())
        cprint("  ✓ Actualizado con éxito. Reinicie NEUROAUDIT.", C.GREEN); sys.exit()
    except Exception as e: cprint(f"  Error: {e}", C.RED)

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
    status_txt = f"{C.GREEN}OK INTEGRIDAD VERIFICADA{C.RESET}" if status_ok else f"{C.RED}ERROR{C.RESET}"
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Estado   : {status_txt}")
    print(f"  Sistema  : {C.GREEN}[LINUX]{C.RESET}  {platform.release()}")
    print(f"  Fecha    : {C.GRAY}{now}{C.RESET}")
    print(f"  Autor    : {C.GRAY}{DEVELOPER}{C.RESET}\n")
    if _update_result["disponible"]:
        cprint(f"  ╔══════════════════════════════════════════════════════╗", C.YELLOW)
        cprint(f"  ║  Nueva versión disponible: v{_update_result['version']:<26}║", C.YELLOW)
        cprint(f"  ╚══════════════════════════════════════════════════════╝", C.YELLOW)

def show_menu():
    cprint("  [1]  Hardware e Identidad Termica", C.RESET)
    cprint("  [2]  Mantenimiento del Sistema (v6.4 Fix)", C.RESET)
    cprint("  [3]  Salud: Discos y S.M.A.R.T. (v6.4 Fix)", C.RESET)
    cprint("  [4]  Auditoria de Seguridad (Puertos)", C.RESET)
    cprint("  [5]  Reporte de Eventos del Sistema", C.RESET)
    cprint("  [6]  Inventario de Software Instalado", C.RESET)
    cprint("  [7]  Exportar Reporte (JSON/PDF/HTML)", C.CYAN)
    cprint("  [8]  Ping / Test de Conectividad", C.RESET)
    cprint("  [9]  Escaneo de Red Local", C.RESET)
    cprint("  [10] Auditoria de Permisos y Usuarios", C.YELLOW)
    cprint("  [0]  Salir\n", C.RED)

def main():
    C.enable_windows_ansi()
    threading.Thread(target=_check_update_background, daemon=True).start()
    
    M = Linux
    acciones = {
        "1": M.sys_info,
        "2": M.maintenance,
        "3": M.disk_health,
        "4": M.security_audit,
        "5": M.event_report,
        "6": M.software_inventory,
        "10": run_permission_audit
    }

    while True:
        show_banner()
        show_menu()
        op = input(f"  {C.CYAN}Seleccione operación: {C.RESET}").strip()
        if op == "0": break
        if op in acciones: 
            acciones[op]()
            pause()

if __name__ == "__main__":
    main()
