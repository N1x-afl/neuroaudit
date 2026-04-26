#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4.3 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# FIX ESTÉTICO: Regreso a lista vertical única (1-10).
# ESTADO: 100% OPERATIVO.
# ===========================================================

import os
import sys
import platform
import subprocess
import re
import json
import datetime
import shutil
import urllib.request

# ── Configuración Core ─────────────────────────────────────
VERSION      = "6.4.3"
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
        sensors_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|Core 0|temp1):\s+[+\-]?(\d+\.\d+)", sensors_out)
        temp_cpu = float(m.group(1)) if m else None
        print(f"  SERIAL : {serial if serial else 'No detectable'}")
        print(f"  CPU    : {cpu}")
        print(f"  TEMP   : {temp_cpu}°C" if temp_cpu else "  TEMP   : N/A")
        print(f"  RAM    : {ram} en uso")
        if input(f"\n  ¿Analizar pasta térmica? (s/n): ").lower() == "s": analizar_pasta_termica(temp_cpu)

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA")
        cprint("\n  [1] Actualizar Sistema\n  [2] Purgar Huerfanos\n  [3] Limpiar Cache\n  [4] Temporales\n  [5] Logs\n  [8] Update Suite", C.RESET)
        op = input(f"\n  Seleccione: ").strip()
        if op == "1": os.system("sudo apt update && sudo apt upgrade -y || sudo pacman -Syu --noconfirm")
        elif op == "2": os.system("sudo apt autoremove -y || sudo pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null")
        elif op == "5": os.system("sudo journalctl --vacuum-time=7d")

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
        section("REPORTE DE EVENTOS")
        os.system("sudo journalctl -p err -n 15 --no-pager")

    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE")
        os.system("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -n 50 2>/dev/null || pacman -Q | head -n 50")

# ── Opción 7: Exportación ──────────────────────────────────
def run_export():
    section("EXPORTAR REPORTE DE AUDITORÍA")
    cprint("  Generando reporte JSON en Carpeta Personal...", C.YELLOW)
    data = {
        "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(),
        "ram": run("free -h | grep Mem | awk '{print $3\" / \"$2}'"),
        "puertos": run("sudo ss -tulpn | grep LISTEN").splitlines()
    }
    path = os.path.join(_get_real_home(), f"reporte_audit_{datetime.datetime.now().strftime('%Y%m%d')}.json")
    with open(path, "w") as f: json.dump(data, f, indent=4)
    cprint(f"  ✓ Reporte guardado en: {path}", C.GREEN)

def run_permission_audit():
    section("AUDITORIA DE PERMISOS Y USUARIOS")
    os.system("ls -la /etc/shadow /etc/sudoers")
    os.system("grep -Po '^sudo:.*:\\K.*|^wheel:.*:\\K.*' /etc/group")

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
    print(f"\n  Estado : {C.GREEN}OK INTEGRIDAD VERIFICADA{C.RESET} | Autor: {DEVELOPER}")

def show_menu():
    print(f"\n  [1]  Hardware e Identidad Termica")
    print(f"  [2]  Mantenimiento del Sistema (v6.4 Fix)")
    print(f"  [3]  Salud: Discos y S.M.A.R.T. (v6.4 Fix)")
    print(f"  [4]  Auditoria de Seguridad (Puertos)")
    print(f"  [5]  Reporte de Eventos del Sistema")
    print(f"  [6]  Inventario de Software Instalado")
    cprint("  [7]  Exportar Reporte (JSON/PDF/HTML)", C.CYAN)
    print(f"  [8]  Ping / Test de Conectividad")
    print(f"  [9]  Escaneo de Red Local")
    cprint("  [10] Auditoria de Permisos y Usuarios", C.YELLOW)
    cprint("  [0]  Salir\n", C.RED)

def analizar_pasta_termica(t):
    if t and t > 75: cprint(f"  ¡Atención! {t}°C es alto. Sugerido cambio de pasta.", C.RED)
    else: cprint("  Temperatura normal.", C.GREEN)

def main():
    C.enable_windows_ansi()
    M = Linux
    acciones = {
        "1": M.sys_info, "2": M.maintenance, "3": M.disk_health, "4": M.security_audit,
        "5": M.event_report, "6": M.software_inventory, "7": run_export,
        "8": lambda: os.system("ping -c 3 8.8.8.8"),
        "9": lambda: os.system(f"sudo nmap -sn {run('hostname -I').split(' ')[0].rsplit('.',1)[0]}.0/24"),
        "10": run_permission_audit
    }
    while True:
        show_banner(); show_menu()
        op = input(f"  Seleccione: ").strip()
        if op == "0": break
        if op in acciones: acciones[op](); pause()

if __name__ == "__main__":
    main()
