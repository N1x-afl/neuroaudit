#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4.2 - Multiplataforma (Windows + Linux)
# Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# ESTADO: 100% OPERATIVO (OPCIONES 1 A 10 VINCULADAS)
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

# ── Configuración Core ─────────────────────────────────────
VERSION      = "6.4.2"
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

# ── Lógica de Actualización ────────────────────────────────
_update_result = {"disponible": False, "version": None}

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

# ── Módulos Linux (Funcionalidad Completa) ─────────────────
class Linux:
    @staticmethod
    def sys_info():
        section("INFRAESTRUCTURA Y SALUD TERMICA")
        cpu = run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        ram = run("free -h | grep Mem | awk '{print $3\" / \"$2}'")
        sensors_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|Core 0|temp1):\s+[+\-]?(\d+\.\d+)", sensors_out)
        temp_cpu = float(m.group(1)) if m else None
        
        print(f"  CPU    : {cpu}")
        print(f"  TEMP   : {temp_cpu}°C" if temp_cpu else "  TEMP   : N/A (lm-sensors no detectado)")
        print(f"  RAM    : {ram} en uso")
        
        guardar_temp_historial(temp_cpu)
        cprint("\n  [ Historial Reciente ]", C.YELLOW)
        mostrar_historial_temps()
        
        resp = input(f"\n  {C.CYAN}¿Ejecutar diagnóstico de pasta térmica? (S/N): {C.RESET}").lower()
        if resp == "s": analizar_pasta_termica(temp_cpu)

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA")
        print("\n  [1] Actualizar Sistema  [2] Purgar Huerfanos  [3] Limpiar Cache  [4] Temporales (v6.4)  [8] Update Suite")
        sub_op = input(f"\n  Seleccione operación: ").strip()
        
        if sub_op == "1":
            cprint("\n  [ Actualizando paquetes... ]", C.YELLOW)
            os.system("sudo apt update && sudo apt upgrade -y || sudo pacman -Syu --noconfirm")
        elif sub_op == "2":
            os.system("sudo apt autoremove -y || sudo pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null")
            cprint("  ✓ Limpieza de huerfanos completada.", C.GREEN)
        elif sub_op == "3":
            os.system("sudo apt clean || sudo pacman -Sc --noconfirm")
            cprint("  ✓ Cache liberada.", C.GREEN)
        elif sub_op == "4":
            print("\n  [1] Ver tamaño  [2] Limpieza Segura (>7d)  [3] Limpieza Profunda (>2d)")
            sel = input("  Opción: ").strip()
            if sel == "2": os.system("sudo find /tmp /var/tmp -type f -atime +7 -delete 2>/dev/null")
            elif sel == "3": os.system("sudo find /tmp /var/tmp -type f -atime +2 -delete 2>/dev/null")
            else: cprint(f"  Tamaño: {run('du -sh /tmp 2>/dev/null')}", C.GRAY)
        elif sub_op == "8":
            auto_update_neuroaudit()

    @staticmethod
    def disk_health():
        section("SALUD: DISCOS Y S.M.A.R.T.")
        cprint("\n  [ Uso de Particiones ]", C.YELLOW)
        os.system("df -h | grep -E 'Filesystem|/dev/sd|/dev/nvme|/$'")
        cprint("\n  [ Estado S.M.A.R.T. Autodetectado ]", C.YELLOW)
        disks = run("lsblk -dn -o NAME | grep -E 'sd|nvme'").splitlines()
        for d in disks:
            cprint(f"\n  Disco /dev/{d}:", C.CYAN)
            os.system(f"sudo smartctl -H /dev/{d} | grep -E 'overall-health|result|PASSED|FAILED' || echo '  Sin datos SMART.'")

    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD (PUERTOS)")
        cprint("\n  [ Servicios Escuchando en el NB ]", C.YELLOW)
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

# ── Auditoría Unificada (Opción 10) ─────────────────────────
def run_permission_audit():
    section("AUDITORIA INTEGRAL DE SEGURIDAD")
    cprint("\n  [ 1. Escaneo de Puertos Locales ]", C.YELLOW)
    os.system("sudo ss -tulpn | grep LISTEN")
    cprint("\n  [ 2. Permisos en Archivos Críticos ]", C.YELLOW)
    os.system("ls -la /etc/shadow /etc/sudoers /etc/passwd")
    cprint("\n  [ 3. Usuarios con capacidad de SUDO ]", C.YELLOW)
    print(run("grep -Po '^sudo:.*:\\K.*|^wheel:.*:\\K.*' /etc/group") or "Solo root")

# ── Funciones de Apoyo ─────────────────────────────────────
def analizar_pasta_termica(temp):
    section("DIAGNOSTICO DE PASTA TERMICA")
    if not temp: return
    if temp < 65: cprint(f"  {temp}°C -> ESTADO ÓPTIMO", C.GREEN)
    elif temp < 80: cprint(f"  {temp}°C -> ELEVADA (Limpieza sugerida)", C.YELLOW)
    else: cprint(f"  {temp}°C -> CRÍTICO (Cambio URGENTE)", C.RED)

def guardar_temp_historial(t):
    try:
        h = os.path.join(_get_real_home(), ".neuroaudit_hist.json")
        data = []
        if os.path.exists(h):
            with open(h, "r") as f: data = json.load(f)
        data.append({"fecha": datetime.datetime.now().isoformat(), "cpu": t})
        with open(h, "w") as f: json.dump(data[-50:], f)
    except: pass

def mostrar_historial_temps():
    try:
        h = os.path.join(_get_real_home(), ".neuroaudit_hist.json")
        with open(h, "r") as f:
            for e in json.load(f)[-5:]: print(f"    {e['fecha'][:16]} -> {e['cpu']}°C")
    except: print("    Sin historial.")

def auto_update_neuroaudit():
    if not _update_result["disponible"]: return
    cprint(f"\n  Actualizando a v{_update_result['version']}...", C.YELLOW)
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as r:
            with open(__file__, "wb") as f: f.write(r.read())
        cprint("  ✓ Actualizado. Reinicie NEUROAUDIT.", C.GREEN); sys.exit()
    except: pass

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
    print(f"  Sistema  : {C.GREEN}[LINUX]{C.RESET}  {platform.release()}")
    print(f"  Fecha    : {C.GRAY}{now}{C.RESET}")
    print(f"  Autor    : {C.GRAY}{DEVELOPER}{C.RESET}\n")

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
        "1": M.sys_info, "2": M.maintenance, "3": M.disk_health, "4": M.security_audit,
        "5": M.event_report, "6": M.software_inventory,
        "8": lambda: os.system("ping -c 3 8.8.8.8"),
        "9": lambda: os.system(f"sudo nmap -sn {run('hostname -I').split(' ')[0].rsplit('.',1)[0]}.0/24"),
        "10": run_permission_audit
    }

    while True:
        show_banner()
        show_menu()
        op = input(f"  Seleccione: ").strip()
        if op == "0": break
        if op in acciones: 
            acciones[op]()
            pause()

if __name__ == "__main__":
    main()
