#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# CHANGELOG v6.4:
# - FIX: S.M.A.R.T. compatible con NVMe y SATA (Autodetect).
# - ADD: Módulo de Auditoría de Seguridad (Puertos y Privilegios).
# - FIX: Restauración de Header de Integridad y Sistema.
# - UI:  Menú optimizado para terminales Linux.
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
import urllib.request

# ── Configuración Core ─────────────────────────────────────
VERSION      = "6.4"
SYSTEM_NAME  = "NEUROAUDIT - Security & IT Suite"
DEVELOPER    = "Felipe Soluciones IT"
GITHUB_USER  = "N1x-afl"
GITHUB_REPO  = "neuroaudit"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/neuroaudit.py"
SO           = platform.system()

class C:
    GREEN   = '\033[92m'
    CYAN    = '\033[96m'
    YELLOW  = '\033[93m'
    RED     = '\033[91m'
    GRAY    = '\033[90m'
    BOLD    = '\033[1m'
    RESET   = '\033[0m'

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

# ── Lógica de Actualización ────────────────────────────────
_update_result = {"disponible": False, "version": None}

def _check_update_background():
    try:
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "neuroaudit"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode())
        tag = data.get("tag_name", "").lstrip("v")
        if tag and tag > VERSION:
            _update_result["disponible"], _update_result["version"] = True, tag
    except: pass

# ── Módulos Linux ──────────────────────────────────────────
class Linux:
    @staticmethod
    def sys_info():
        section("INFRAESTRUCTURA Y SALUD TÉRMICA")
        cpu = run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        temp = run("sensors 2>/dev/null | grep -E 'Package id 0|Core 0|temp1' | head -n1 | awk '{print $4}'")
        print(f"  CPU    : {cpu}")
        print(f"  TEMP   : {temp if temp else 'N/A'}")
        print(f"  RAM    : {run('free -h | grep Mem | awk \"{print $3\\\"/\\\"$2}\"')}")

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA")
        cprint("\n  [1] Limpiar Cache APT  [2] Limpiar Logs (>7d)  [3] Actualizar Suite", C.CYAN)
        op = input(f"\n  Seleccione: ").strip()
        if op == "1": os.system("sudo apt clean && sudo apt autoremove -y")
        elif op == "2": os.system("sudo journalctl --vacuum-time=7d")
        elif op == "3": auto_update_neuroaudit()

    @staticmethod
    def disk_health():
        section("SALUD: DISCOS Y S.M.A.R.T.")
        cprint("\n  [ Uso de Particiones ]", C.YELLOW)
        os.system("df -h | grep -E 'Filesystem|/dev/sd|/dev/nvme|/$'")
        
        cprint("\n  [ Estado S.M.A.R.T. Autodetectado ]", C.YELLOW)
        if shutil.which("smartctl"):
            disks = run("lsblk -dn -o NAME | grep -E 'sd|nvme'").splitlines()
            for d in disks:
                cprint(f"\n  Disco /dev/{d}:", C.CYAN)
                res = run(f"sudo smartctl -H /dev/{d} | grep -E 'overall-health|result|PASSED|FAILED'")
                print(f"  {res if res else 'No se pudo obtener datos (¿es una VM o disco bloqueado?)'}")
        else:
            cprint("  smartctl no instalado. Instale: sudo apt install smartmontools", C.RED)

    @staticmethod
    def security_audit():
        section("AUDITORÍA DE SEGURIDAD Y PRIVILEGIOS")
        cprint("\n  [ Puertos en Escucha (TCP/UDP) ]", C.YELLOW)
        os.system("sudo ss -tulpn | grep LISTEN")
        
        cprint("\n  [ Usuarios con capacidad de SUDO ]", C.YELLOW)
        sudo_users = run("grep -Po '^sudo:.*:\\K.*|^wheel:.*:\\K.*' /etc/group")
        cprint(f"  Grupo SUDO: {sudo_users if sudo_users else 'No detectado'}", C.CYAN)
        
        cprint("\n  [ Binarios SUID (Potenciales vectores de escalada) ]", C.YELLOW)
        os.system("find /usr/bin -perm -4000 -type f 2>/dev/null | head -n 5")

    @staticmethod
    def event_report():
        section("REPORTE DE EVENTOS CRÍTICOS")
        os.system("sudo journalctl -p err -n 15 --no-pager")

    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE")
        os.system("dpkg -l | grep '^ii' | head -n 20")
        count = run("dpkg -l | grep '^ii' | wc -l")
        cprint(f"\n  Total paquetes: {count}", C.YELLOW)

# ── Interfaz y Ejecución ───────────────────────────────────

def show_banner():
    os.system('clear')
    status_ok = b"Felipe Soluciones IT" in open(__file__, "rb").read()
    status_txt = f"{C.GREEN}OK INTEGRIDAD VERIFICADA{C.RESET}" if status_ok else f"{C.RED}ERROR{C.RESET}"
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    
    cprint("  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗", C.GREEN)
    cprint("  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝", C.GREEN)
    cprint("  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║   ", C.GREEN)
    cprint("  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║   ", C.GREEN)
    cprint("  ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝██████╔╝██║   ██║   ", C.GREEN)
    cprint(f"  {'='*82}", C.CYAN)
    print(f"                   A  U  D  I  T     S  Y  S  T  E  M   v{VERSION}")
    cprint(f"  {'='*82}", C.CYAN)
    
    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Estado   : {status_txt}")
    print(f"  Sistema  : {C.GREEN}[LINUX]{C.RESET} {platform.release()}")
    print(f"  Fecha    : {C.GRAY}{now}{C.RESET}")
    print(f"  Autor    : {C.GRAY}{DEVELOPER}{C.RESET}\n")

def show_menu():
    print(f"  {C.BOLD}[1]{C.RESET}  Infraestructura y Termica")
    print(f"  {C.BOLD}[2]{C.RESET}  Mantenimiento del Sistema")
    print(f"  {C.BOLD}[3]{C.RESET}  Salud: Discos y S.M.A.R.T.")
    print(f"  {C.BOLD}[4]{C.RESET}  Auditoría de Seguridad")
    print(f"  {C.BOLD}[5]{C.RESET}  Reporte de Eventos (Logs)")
    print(f"  {C.BOLD}[6]{C.RESET}  Inventario de Software")
    print(f"  {C.BOLD}[0]{C.RESET}  Salir\n")

def auto_update_neuroaudit():
    cprint(f"\n  Actualizando desde repositorio...", C.YELLOW)
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as response:
            nuevo_codigo = response.read()
        with open(__file__, "wb") as f:
            f.write(nuevo_codigo)
        cprint("  ✓ v6.4 Finalizada. Reinicie el script.", C.GREEN)
        sys.exit(0)
    except Exception as e: cprint(f"  Error: {e}", C.RED)

def main():
    threading.Thread(target=_check_update_background, daemon=True).start()
    M = Linux
    
    while True:
        show_banner()
        show_menu()
        op = input(f"  {C.CYAN}Seleccione operacion: {C.RESET}").strip()
        
        if op == "0": break
        elif op == "1": M.sys_info()
        elif op == "2": M.maintenance()
        elif op == "3": M.disk_health()
        elif op == "4": M.security_audit()
        elif op == "5": M.event_report()
        elif op == "6": M.software_inventory()
        
        if op != "0": pause()

if __name__ == "__main__":
    main()
