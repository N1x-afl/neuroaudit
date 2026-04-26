#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4 - Multiplataforma (Windows + Linux)
# Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# CAMBIOS EN v6.4:
# - RESTORE: Logo original de bloques ASCII.
# - RESTORE: Lista detallada en inventario de software (head -n 50).
# - FIX: Comparador de versiones numérico (evita downgrade v6.2).
# - MEJORA: Limpieza de /tmp opcional y selectiva.
# ===========================================================

import os
import sys

# ── Fix de paths para sudo ──────────────────────────────────
def _fix_sys_path():
    import sysconfig
    _ver = sys.version_info
    _paths = [
        f"/usr/local/lib/python{_ver.major}.{_ver.minor}/dist-packages",
        f"/usr/local/lib/python{_ver.major}/dist-packages",
        f"/usr/lib/python{_ver.major}.{_ver.minor}/dist-packages",
        f"/usr/lib/python3/dist-packages",
        os.path.expanduser(f"~/.local/lib/python{_ver.major}.{_ver.minor}/site-packages"),
    ]
    for _p in _paths:
        if os.path.exists(_p) and _p not in sys.path:
            sys.path.insert(0, _p)
_fix_sys_path()

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

VERSION      = "6.4"
SYSTEM_NAME  = "NEUROAUDIT - Security & IT Suite"
DEVELOPER    = "Felipe Soluciones IT"
GITHUB_USER  = "N1x-afl"
GITHUB_REPO  = "neuroaudit"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/neuroaudit.py"
SO           = platform.system()

# ── Flags de línea de comandos ──────────────────────────────
SHOW_BANNER   = "--no-banner"  not in sys.argv
MODO_CLIENTE  = "--cliente"    in sys.argv

# ── Colores ANSI ────────────────────────────────────────────
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
                kernel32.SetConsoleOutputCP(65001)
                kernel32.SetConsoleCP(65001)
            except Exception: pass

def cprint(text, color=C.RESET, bold=False):
    prefix = C.BOLD if bold else ''
    print(f"{prefix}{color}{text}{C.RESET}")

def section(title):
    print()
    cprint(f"  +{'─'*56}+", C.CYAN)
    cprint(f"  │  {title:<54}│", C.CYAN)
    cprint(f"  +{'─'*56}+", C.CYAN)

def run(cmd, shell=True, timeout=15):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except Exception: return ""

def pause():
    input(f"\n{C.CYAN}  Presione Enter para volver al menu...{C.RESET}")

def _get_real_home():
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and sudo_user != "root":
        import pwd
        try: return pwd.getpwnam(sudo_user).pw_dir
        except Exception: pass
    return os.path.expanduser("~")

def check_privileges():
    if SO == "Linux": return os.geteuid() == 0
    else:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception: return False

# ════════════════════════════════════════════════════════════
#  UPDATER LÓGICA v6.4
# ════════════════════════════════════════════════════════════

_update_result = {"disponible": False, "version": None, "url": None, "checked": False}

def _check_update_background():
    try:
        import urllib.request
        import json as _json
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "neuroaudit-updater"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read().decode())
        tag = data.get("tag_name", "").lstrip("v")
        def parse_v(v): return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]
        if tag and parse_v(tag) > parse_v(VERSION):
            _update_result["disponible"] = True
            _update_result["version"]    = tag
            _update_result["url"]        = data.get("html_url", "")
    except Exception: pass
    finally: _update_result["checked"] = True

def start_update_check():
    t = threading.Thread(target=_check_update_background, daemon=True)
    t.start()

def show_update_notice():
    if _update_result["disponible"]:
        cprint(f"\n  [ Nueva versión disponible: v{_update_result['version']} ]", C.YELLOW, bold=True)

# ════════════════════════════════════════════════════════════
#  MÓDULOS LINUX
# ════════════════════════════════════════════════════════════

class Linux:
    @staticmethod
    def get_distro():
        distro = run("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'")
        pkg = "APT" if shutil.which("apt") else "PACMAN" if shutil.which("pacman") else "DNF" if shutil.which("dnf") else "Desconocido"
        return distro, pkg

    @staticmethod
    def sys_info():
        section("HARDWARE Y TEMPERATURA [LINUX]")
        distro, pkg = Linux.get_distro()
        cpu = run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        sensors_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|temp1|Core 0|temp2):\s+[+\-]?(\d+\.\d+)", sensors_out)
        temp_cpu = float(m.group(1)) if m else None
        print(f"  CPU    : {cpu}")
        print(f"  TEMP   : {temp_cpu}°C" if temp_cpu else "  TEMP   : N/A")
        print(f"  DISTRO : {distro} ({pkg})")
        guardar_temp_historial(temp_cpu, None, False)

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA [LINUX]")
        cprint("\n  [4] Gestión de Temporales", C.CYAN)
        cprint("  [8] Actualizar NEUROAUDIT", C.GREEN)
        op = input(f"\n  {C.CYAN}Seleccione: {C.RESET}").strip()
        
        if op == "8": 
            auto_update_neuroaudit()
        elif op == "4":
            print("\n  [1] Ver tamaño  [2] Borrar > 7 días  [3] Borrar > 2 días")
            sel = input(f"  Opcion: ").strip()
            if sel == "2": os.system("sudo find /tmp /var/tmp -type f -atime +7 -delete 2>/dev/null")
            elif sel == "3": os.system("sudo find /tmp /var/tmp -type f -atime +2 -delete 2>/dev/null")
            else: cprint(f"  Tamaño actual: {run('du -sh /tmp 2>/dev/null')}", C.GRAY)

    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE DETALLADO [LINUX]")
        _, pkg = Linux.get_distro()
        if pkg == "APT":
            os.system("dpkg-query -W -f='${binary:Package} [${Version}]\\n' | head -n 50")
            count = run("dpkg -l | grep '^ii' | wc -l")
        elif pkg == "PACMAN":
            os.system("pacman -Q | head -n 50")
            count = run("pacman -Q | wc -l")
        else: count = "N/A"
        cprint(f"\n  [ Mostrando primeros 50 de {count} paquetes totales ]", C.YELLOW)

    @staticmethod
    def disk_health():
        section("SALUD DE DISCOS")
        os.system("df -h | grep -E '^/dev/'")

    @staticmethod
    def security_audit():
        section("AUDITORÍA DE PUERTOS")
        os.system("sudo ss -tunlp | grep LISTEN")

    @staticmethod
    def event_report():
        section("EVENTOS DEL SISTEMA")
        os.system("sudo journalctl -p err -n 10 --no-pager")

    @staticmethod
    def network_ping():
        section("TEST CONECTIVIDAD")
        os.system("ping -c 3 8.8.8.8")

    @staticmethod
    def network_scan():
        section("ESCANEO RED LOCAL")
        local_ip = run("hostname -I | awk '{print $1}'")
        if local_ip: os.system(f"sudo nmap -sn {local_ip.rsplit('.', 1)[0]}.0/24")

class Windows:
    @staticmethod
    def sys_info(): section("INFO WINDOWS"); print("Módulo Windows simplificado.")
    @staticmethod
    def maintenance(): pass
    @staticmethod
    def software_inventory(): os.system("wmic product get name")
    @staticmethod
    def disk_health(): pass
    @staticmethod
    def security_audit(): pass
    @staticmethod
    def event_report(): pass
    @staticmethod
    def network_ping(): os.system("ping 8.8.8.8")
    @staticmethod
    def network_scan(): os.system("arp -a")

# ════════════════════════════════════════════════════════════
#  FUNCIONES DE APOYO
# ════════════════════════════════════════════════════════════

def guardar_temp_historial(t_cpu, t_gpu, notebook):
    path = os.path.join(_get_real_home(), ".neuroaudit_hist.json")
    hist = []
    if os.path.exists(path):
        try:
            with open(path, "r") as f: hist = json.load(f)
        except: pass
    hist.append({"fecha": datetime.datetime.now().isoformat(), "cpu": t_cpu})
    with open(path, "w") as f: json.dump(hist[-50:], f)

def auto_update_neuroaudit():
    section("UPDATE NEUROAUDIT")
    if not _update_result["disponible"]:
        cprint("  Ya estás en la versión más reciente.", C.GREEN); return
    cprint(f"  Actualizando a v{_update_result['version']}...", C.YELLOW)
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as response:
            data = response.read()
        with open(os.path.abspath(__file__), "wb") as f: f.write(data)
        cprint("  ✓ Actualización completa. Reinicie el programa.", C.GREEN); sys.exit(0)
    except Exception as e: cprint(f"  Error: {e}", C.RED)

def run_permission_audit():
    section("AUDITORÍA DE PERMISOS")
    if SO == "Linux": os.system("ls -la /etc/shadow /etc/sudoers")
    else: os.system("net user")

def show_banner():
    os.system('cls' if SO == 'Windows' else 'clear')
    # Restaurado el Logo solicitado por Felipe
    cprint("  _   _ _____ _   _ ____   ___     _   _ ____ ___ _____ ", C.GREEN)
    cprint(" | \\ | | ____| | | |  _ \\ / _ \\   / \\ | |  _ \\_ _|_   _|", C.GREEN)
    cprint(" |  \\| |  _| | | | | |_) | | | | / _ \\| | | | | |  | |  ", C.GREEN)
    cprint(" | |\\  | |___| |_| |  _ <| |_| |/ ___ \\ |_| | | |  | |  ", C.GREEN)
    cprint(" |_| \\_|_____|\\___/|_| \\_\\\\___//_/   \\_\\____/___| |_|  ", C.GREEN)
    cprint(f"  {'='*58} v{VERSION}", C.CYAN)
    show_update_notice()

def show_menu():
    print(f"\n  [1] Hardware y Temperatura       [6] Inventario Software")
    print(f"  [2] Mantenimiento (v6.4 Fix)     [7] Exportar Reporte")
    print(f"  [3] Salud de Discos              [8] Test Conectividad")
    print(f"  [4] Seguridad de Puertos         [9] Escaneo Red Local")
    print(f"  [5] Eventos del Sistema          [10] Auditoría Permisos")
    print(f"  [0] Salir\n")

def main():
    C.enable_windows_ansi()
    start_update_check()
    if not check_privileges():
        cprint("\n  ERROR: Ejecute como Administrador/Root.\n", C.RED); sys.exit(1)

    M = Linux if SO == "Linux" else Windows
    acciones = {"1": M.sys_info, "2": M.maintenance, "3": M.disk_health, "4": M.security_audit, "5": M.event_report,
                "6": M.software_inventory, "7": Linux.get_distro, "8": M.network_ping, "9": M.network_scan, "10": run_permission_audit}

    while True:
        show_banner()
        show_menu()
        op = input(f"  Seleccione operacion: ").strip()
        if op == "0": break
        if op in acciones: 
            acciones[op]()
            pause()

if __name__ == "__main__":
    main()
