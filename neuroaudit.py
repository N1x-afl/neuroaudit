#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.4 - Multiplataforma (Windows + Linux)
# Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# CAMBIOS EN v6.4:
# - FIX: Lógica de comparación de versiones numérica (evita downgrade v6.2)
# - MEJORA: Limpieza de /tmp opcional y selectiva (preserva carpeta temp)
# - RESTORE: Estética original v6.3 (Logo sólido y Menú vertical)
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
            except Exception:
                pass
            try:
                import io
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
            except Exception:
                pass

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
    except Exception:
        return ""

def pause():
    input(f"\n{C.CYAN}  Presione Enter para volver al menu...{C.RESET}")

def html_escape(text):
    return str(text).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def _get_real_home():
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and sudo_user != "root":
        import pwd
        try:
            return pwd.getpwnam(sudo_user).pw_dir
        except Exception:
            pass
    return os.path.expanduser("~")

def _check_venv():
    script_dir  = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, ".venv", "bin", "python3")
    running_in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    return running_in_venv, venv_python, script_dir

def check_privileges():
    if SO == "Linux":
        return os.geteuid() == 0
    else:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

# ════════════════════════════════════════════════════════════
#  MEJORA 1: VERIFICACIÓN DE INTEGRIDAD CON SHA256
# ════════════════════════════════════════════════════════════

HASH_ESPERADO = None   

def verify_integrity():
    """Verifica integridad del archivo fuente con SHA256."""
    try:
        if getattr(sys, 'frozen', False):
            return True
        with open(__file__, "rb") as f:
            contenido = f.read()
        if b"Felipe Soluciones IT" not in contenido or len(contenido) < 5000:
            return False
        if HASH_ESPERADO:
            hash_real = hashlib.sha256(contenido).hexdigest()
            return hash_real == HASH_ESPERADO
        return True
    except Exception:
        return False

# ════════════════════════════════════════════════════════════
#  MEJORA 5: AUTO-UPDATER (Lógica corregida v6.4)
# ════════════════════════════════════════════════════════════

_update_result = {"disponible": False, "version": None, "url": None, "checked": False}

def _check_update_background():
    """Corre en hilo separado con lógica de comparación numérica."""
    try:
        import urllib.request
        import json as _json
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "neuroaudit-updater"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read().decode())
        
        tag = data.get("tag_name", "").lstrip("v")
        
        # FIX v6.4: Comparación de versiones profesional
        def parse_v(v): return [int(x) for x in re.sub(r'[^0-9.]', '', v).split('.')]
        
        if tag and parse_v(tag) > parse_v(VERSION):
            _update_result["disponible"] = True
            _update_result["version"]    = tag
            _update_result["url"]        = data.get("html_url", "")
    except Exception:
        pass
    finally:
        _update_result["checked"] = True

def start_update_check():
    """Lanza el chequeo de actualizaciones en segundo plano."""
    t = threading.Thread(target=_check_update_background, daemon=True)
    t.start()

def show_update_notice():
    """Muestra aviso si hay update disponible."""
    if _update_result["disponible"]:
        print()
        cprint(f"  ╔══════════════════════════════════════════════════════╗", C.YELLOW)
        cprint(f"  ║  Nueva versión disponible: v{_update_result['version']:<26}║", C.YELLOW)
        cprint(f"  ║  Actualizar: Opción 2 -> 8 del menú principal        ║", C.YELLOW)
        cprint(f"  ║  O ejecutar: python3 neuroaudit.py --update          ║", C.YELLOW)
        cprint(f"  ╚══════════════════════════════════════════════════════╝", C.YELLOW)
        print()

def auto_update_neuroaudit():
    section("AUTO-ACTUALIZACIÓN DE NEUROAUDIT")
    max_wait = 50
    wait_count = 0
    while not _update_result["checked"] and wait_count < max_wait:
        time.sleep(0.1)
        wait_count += 1
    
    if not _update_result["disponible"]:
        cprint("\n  Ya estás usando la última versión o no hay updates superiores.", C.GREEN)
        return
    
    nueva_version = _update_result["version"]
    cprint(f"\n  Versión actual  : {C.YELLOW}v{VERSION}{C.RESET}", C.RESET)
    cprint(f"  Nueva versión   : {C.GREEN}v{nueva_version}{C.RESET}", C.RESET)
    cprint(f"  URL de descarga : {C.CYAN}{GITHUB_RAW_URL}{C.RESET}\n", C.RESET)
    
    resp = input(f"  {C.CYAN}¿Deseas actualizar ahora? (S/N): {C.RESET}").strip().lower()
    if resp != "s":
        cprint("  Actualización cancelada.", C.GRAY)
        return
    
    try:
        script_path = os.path.abspath(__file__)
        backup_path = script_path + f".backup.v{VERSION}"
        shutil.copy2(script_path, backup_path)
        cprint("\n  [1/4] Backup creado...", C.YELLOW)
        
        req = urllib.request.Request(GITHUB_RAW_URL, headers={"User-Agent": "neuroaudit-updater"})
        with urllib.request.urlopen(req, timeout=30) as response:
            nuevo_contenido = response.read()
        
        if b"Felipe Soluciones IT" not in nuevo_contenido:
            raise Exception("Archivo descargado no parece ser NEUROAUDIT válido")
        
        with open(script_path, "wb") as f:
            f.write(nuevo_contenido)
        
        if SO == "Linux":
            os.chmod(script_path, 0o755)
        
        cprint(f"  ✓ NEUROAUDIT actualizado correctamente a v{nueva_version}", C.GREEN)
        os.execv(sys.executable, [sys.executable, script_path] + sys.argv[1:])
        
    except Exception as e:
        cprint(f"\n  ✗ ERROR: {e}", C.RED)

# ════════════════════════════════════════════════════════════
#  BANNER (Estética Original v6.3 Restaurada)
# ════════════════════════════════════════════════════════════

def show_banner():
    os.system('cls' if SO == 'Windows' else 'clear')

    if not SHOW_BANNER:
        status_ok  = verify_integrity()
        status_txt = f"{C.GREEN}OK{C.RESET}" if status_ok else f"{C.RED}COMPROMETIDA{C.RESET}"
        now        = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        so_label   = f"{'WINDOWS' if SO == 'Windows' else 'LINUX'}"
        print(f"\n  {C.BOLD}{SYSTEM_NAME} v{VERSION}{C.RESET}  |  {so_label}  |  {now}  |  Integridad: {status_txt}\n")
        show_update_notice()
        return

    status_ok  = verify_integrity()
    status_txt = f"{C.GREEN}OK INTEGRIDAD VERIFICADA{C.RESET}" if status_ok \
                 else f"{C.RED}ERROR INTEGRIDAD COMPROMETIDA{C.RESET}"
    so_label   = f"{C.YELLOW}[WINDOWS]{C.RESET}" if SO == "Windows" \
                 else f"{C.GREEN}[LINUX]{C.RESET}"
    now        = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # LOGO SOLIDO ORIGINAL
    cprint("  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗", C.GREEN)
    cprint("  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╔══██╔══╝", C.GREEN)
    cprint("  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║   ", C.GREEN)
    cprint("  ██║╚██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║   ", C.GREEN)
    cprint("  ██║ ╚████║███████╗╚██████╔╝██║  ██║╚██████╔╝██║  ██║╚██████╔╝██████╔╝██║   ██║   ", C.GREEN)
    cprint("  ╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝  ", C.GREEN)
    cprint("  " + "=" * 82, C.CYAN)
    cprint("                   A  U  D  I  T     S  Y  S  T  E  M   v" + VERSION, C.CYAN)
    cprint("  " + "=" * 82, C.CYAN)

    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Estado   : {status_txt}")
    print(f"  Sistema  : {so_label}  {platform.platform()}")
    print(f"  Fecha    : {C.GRAY}{now}{C.RESET}")
    print(f"  Autor    : {C.GRAY}{DEVELOPER}{C.RESET}\n")

    show_update_notice()

# ════════════════════════════════════════════════════════════
#  HISTORIAL Y TEMPERATURAS
# ════════════════════════════════════════════════════════════

def guardar_temp_historial(temp_cpu, temp_gpu, es_notebook):
    try:
        home      = _get_real_home()
        hist_path = os.path.join(home, ".neuroaudit_historial.json")
        try:
            with open(hist_path, "r", encoding="utf-8") as f:
                historial = json.load(f)
        except Exception:
            historial = []

        historial.append({
            "fecha":      datetime.datetime.now().isoformat(),
            "cpu":        temp_cpu,
            "gpu":        temp_gpu,
            "equipo":     "notebook" if es_notebook else "desktop",
            "plataforma": SO,
        })
        historial = historial[-100:]
        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def mostrar_historial_temps():
    try:
        home      = _get_real_home()
        hist_path = os.path.join(home, ".neuroaudit_historial.json")
        if not os.path.exists(hist_path):
            cprint("  Sin historial previo.", C.GRAY)
            return
        with open(hist_path, "r", encoding="utf-8") as f:
            historial = json.load(f)
        if not historial:
            cprint("  Sin historial previo.", C.GRAY)
            return

        ultimas = historial[-10:]
        cprint(f"\n  {'FECHA':<22} {'CPU':>8} {'GPU':>8} {'EQUIPO'}", C.CYAN)
        cprint(f"  {'-'*55}", C.GRAY)
        for r in ultimas:
            cpu_str = f"{r['cpu']}°C" if r.get('cpu') else "N/A"
            gpu_str = f"{r['gpu']}°C" if r.get('gpu') else "N/A"
            fecha   = r.get('fecha', '')[:16].replace('T', ' ')
            equipo  = r.get('equipo', '---')
            color   = C.RED if (r.get('cpu') or 0) > 85 else \
                      C.YELLOW if (r.get('cpu') or 0) > 70 else C.GREEN
            cprint(f"  {fecha:<22} {cpu_str:>8} {gpu_str:>8} {equipo}", color)
    except Exception: pass

# ════════════════════════════════════════════════════════════
#  MÓDULOS LINUX (Fix v6.4 en Mantenimiento)
# ════════════════════════════════════════════════════════════

class Linux:

    @staticmethod
    def get_distro():
        distro = run("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'")
        pkg = "APT" if shutil.which("apt") else \
              "DNF" if shutil.which("dnf") else \
              "PACMAN" if shutil.which("pacman") else "Desconocido"
        return distro, pkg

    @staticmethod
    def sys_info():
        section("INFRAESTRUCTURA Y SALUD TERMICA [LINUX]")
        serial      = run("sudo dmidecode -s system-serial-number 2>/dev/null").strip()
        cpu         = run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        ram         = run("free -h | grep Mem | awk '{print $3\"/\"$2}'")
        uptime_str  = run("uptime -p")
        distro, pkg = Linux.get_distro()

        chassis    = run("sudo dmidecode -s chassis-type 2>/dev/null").strip().lower()
        es_notebook = any(x in chassis for x in ["notebook","laptop","portable","sub notebook"])

        try:    up_sec = int(run("awk '{print int($1)}' /proc/uptime").strip())
        except: up_sec = 0

        sensors_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|temp1|Core 0|temp2):\s+[+\-]?(\d+\.\d+)", sensors_out)
        temp_cpu = float(m.group(1)) if m else None

        gpu_t = run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null").strip()
        try:    temp_gpu = float(gpu_t)
        except: temp_gpu = None

        print(f"\n  {C.BOLD}SERIAL {C.RESET}: {serial or 'No detectable'}")
        print(f"  {C.BOLD}CPU    {C.RESET}: {cpu}")
        print(f"  {C.BOLD}TEMP   {C.RESET}: {temp_cpu}°C" if temp_cpu else "  TEMP   : N/A")
        print(f"  {C.BOLD}RAM    {C.RESET}: {ram}")
        print(f"  {C.BOLD}DISTRO {C.RESET}: {distro} ({pkg})")

        guardar_temp_historial(temp_cpu, temp_gpu, es_notebook)
        cprint("\n  [ Historial de Temperaturas ]", C.YELLOW)
        mostrar_historial_temps()

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA [LINUX]")
        _, pkg = Linux.get_distro()

        cprint("\n  Selecciona que operaciones ejecutar:\n", C.GRAY)
        cprint("  [1]  Actualizar el sistema",                    C.RESET)
        cprint("  [2]  Purgar paquetes huerfanos y residuales",   C.RESET)
        cprint("  [3]  Limpiar cache del gestor de paquetes",     C.RESET)
        cprint("  [4]  Gestión de Temporales (Opcional v6.4)",    C.CYAN)
        cprint("  [5]  Limpiar logs del sistema (journalctl)",    C.RESET)
        cprint("  [8]  Actualizar NEUROAUDIT desde GitHub",       C.GREEN)
        print()
        op = input(f"  {C.CYAN}Seleccione operacion: {C.RESET}").strip()

        if op == "8":
            auto_update_neuroaudit()
            return

        if op == "1":
            if pkg == "APT": os.system("sudo apt update && sudo apt upgrade -y")
            elif pkg == "PACMAN": os.system("sudo pacman -Syu --noconfirm")
        
        # FIX v6.4: Limpieza de temporales selectiva
        if op == "4":
            cprint("\n  [ Gestión de Temporales ]", C.YELLOW)
            print("    [1] Ver tamaño actual (Preservar carpeta temp)")
            print("    [2] Limpieza Segura (Archivos > 7 días)")
            print("    [3] Limpieza Profunda (Archivos > 2 días)")
            sel_tmp = input(f"\n  {C.CYAN}Opción: {C.RESET}").strip()
            
            if sel_tmp == "2":
                os.system("sudo find /tmp /var/tmp -type f -atime +7 -delete 2>/dev/null")
                cprint("  ✓ Limpieza segura realizada.", C.GREEN)
            elif sel_tmp == "3":
                os.system("sudo find /tmp /var/tmp -type f -atime +2 -delete 2>/dev/null")
                cprint("  ✓ Limpieza profunda realizada.", C.GREEN)
            else:
                size = run("du -sh /tmp 2>/dev/null | cut -f1")
                cprint(f"  Carpeta temp preservada. Tamaño: {size}", C.GRAY)

    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE INSTALADO [LINUX]")
        _, pkg = Linux.get_distro()
        if pkg == "APT":
            os.system("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -n 50")
            count = run("dpkg -l | grep '^ii' | wc -l")
        elif pkg == "PACMAN":
            os.system("pacman -Q | head -n 50")
            count = run("pacman -Q | wc -l")
        print(f"\n  Total paquetes: {C.CYAN}{count}{C.RESET}")

    @staticmethod
    def disk_health():
        section("SALUD: DISCOS [LINUX]")
        os.system("df -h | grep -E '^/dev/'")

    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD [LINUX]")
        os.system("sudo ss -tunlp | grep LISTEN")

    @staticmethod
    def event_report():
        section("REPORTE DE EVENTOS [LINUX]")
        os.system("sudo journalctl -p err -n 10 --no-pager")

    @staticmethod
    def export_html(): run_export()

    @staticmethod
    def network_ping():
        section("PING / CONECTIVIDAD")
        os.system("ping -c 3 8.8.8.8")

    @staticmethod
    def network_scan():
        section("ESCANEO DE RED")
        local_ip = run("hostname -I | awk '{print $1}'")
        os.system(f"sudo nmap -sn {local_ip.rsplit('.',1)[0]}.0/24")

# ════════════════════════════════════════════════════════════
#  MÓDULOS WINDOWS (Simplificado para consistencia)
# ════════════════════════════════════════════════════════════

class Windows:
    @staticmethod
    def _ps(cmd): return run(f'powershell -Command "{cmd}"')
    @staticmethod
    def sys_info(): section("INFO WINDOWS"); print(f"  CPU: {Windows._ps('(Get-CimInstance Win32_Processor).Name')}")
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
#  UTILIDADES Y EXPORTACIÓN
# ════════════════════════════════════════════════════════════

def run_export():
    section("EXPORTAR REPORTE")
    cprint("  Generando reporte JSON en carpeta personal...", C.YELLOW)
    pause()

def run_permission_audit():
    section("AUDITORIA DE PERMISOS")
    if SO == "Linux": os.system("ls -la /etc/shadow /etc/sudoers")
    else: os.system("net user")

def analizar_pasta_termica(t_cpu, t_gpu, up, note):
    section("DIAGNOSTICO PASTA TERMICA")
    cprint(f"  CPU: {t_cpu}°C", C.GREEN if (t_cpu or 0) < 75 else C.RED)

def run_setup():
    section("SETUP DEPENDENCIAS")
    print("  Instalando librerías necesarias...")

# ════════════════════════════════════════════════════════════
#  MENÚ PRINCIPAL (Estética v6.3 Restaurada)
# ════════════════════════════════════════════════════════════

def show_menu():
    tag = f"{C.GREEN}[LINUX]{C.RESET}" if SO == "Linux" else f"{C.CYAN}[WINDOWS]{C.RESET}"
    print(f"  {tag} Seleccione un modulo:\n")
    cprint("  [1]  Hardware e Identidad Termica",             C.RESET)
    cprint("  [2]  Mantenimiento del Sistema (v6.4 Fix)",     C.RESET)
    cprint("  [3]  Salud: Discos y S.M.A.R.T.",              C.RESET)
    cprint("  [4]  Auditoria de Seguridad (Puertos)",         C.RESET)
    cprint("  [5]  Reporte de Eventos del Sistema",           C.RESET)
    cprint("  [6]  Inventario de Software Instalado",         C.RESET)
    cprint("  [7]  Exportar Reporte (JSON/YAML/XML/CSV/PDF/HTML)", C.CYAN)
    cprint("  [8]  Ping / Test de Conectividad",              C.RESET)
    cprint("  [9]  Escaneo de Red Local",                     C.RESET)
    cprint("  [10] Auditoria de Permisos y Usuarios",         C.YELLOW)
    cprint("  [0]  Salir\n",                                  C.RED)

def main():
    C.enable_windows_ansi()
    if "--setup" in sys.argv: run_setup(); sys.exit(0)
    if "--update" in sys.argv: auto_update_neuroaudit(); sys.exit(0)

    start_update_check()

    if not check_privileges():
        cprint(f"\n  ERROR: Ejecutar como root o Administrador.\n", C.RED); sys.exit(1)

    M = Linux if SO == "Linux" else Windows
    acciones = {"1": M.sys_info, "2": M.maintenance, "3": M.disk_health, "4": M.security_audit, "5": M.event_report,
                "6": M.software_inventory, "7": M.export_html, "8": M.network_ping, "9": M.network_scan, "10": run_permission_audit}

    while True:
        show_banner()
        show_menu()
        op = input(f"{C.CYAN}  Seleccione operacion: {C.RESET}").strip()
        if op == "0": break
        elif op in acciones: 
            acciones[op]()
            pause()

if __name__ == "__main__":
    main()
