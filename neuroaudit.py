#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.2 - Multiplataforma (Windows + Linux)
# Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# USO:
#   Linux   : sudo python3 neuroaudit.py
#   Windows : python neuroaudit.py  (como Administrador)
#   Flags   : --no-banner   (oculta logo ASCII)
#             --cliente     (output simplificado para clientes)
#             --setup       (instalador de dependencias)
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

VERSION      = "6.2"
SYSTEM_NAME  = "NEUROAUDIT - Security & IT Suite"
DEVELOPER    = "Felipe Soluciones IT"
GITHUB_USER  = "N1x-afl"
GITHUB_REPO  = "neuroaudit"
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

# Para regenerar este hash después de editar el archivo, ejecutar:
#   python3 -c "import hashlib; print(hashlib.sha256(open('neuroaudit.py','rb').read()).hexdigest())"
# y pegar el resultado en HASH_ESPERADO.
# Dejar en None para deshabilitar la verificación de hash (modo desarrollo).
HASH_ESPERADO = None   # ← reemplazar con el hash real al distribuir

def verify_integrity():
    """Verifica integridad del archivo fuente con SHA256."""
    try:
        # Si está compilado con PyInstaller, confiar en el binario
        if getattr(sys, 'frozen', False):
            return True
        with open(__file__, "rb") as f:
            contenido = f.read()
        # Verificación básica: el desarrollador debe estar en el código
        if b"Felipe Soluciones IT" not in contenido or len(contenido) < 5000:
            return False
        # Verificación avanzada con hash (si está configurado)
        if HASH_ESPERADO:
            hash_real = hashlib.sha256(contenido).hexdigest()
            return hash_real == HASH_ESPERADO
        return True
    except Exception:
        return False

# ════════════════════════════════════════════════════════════
#  MEJORA 5: AUTO-UPDATER (chequeo de versión en GitHub)
# ════════════════════════════════════════════════════════════

_update_result = {"disponible": False, "version": None, "url": None, "checked": False}

def _check_update_background():
    """Corre en hilo separado para no bloquear el arranque."""
    try:
        import urllib.request
        import json as _json
        url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={"User-Agent": "neuroaudit-updater"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = _json.loads(resp.read().decode())
        tag = data.get("tag_name", "").lstrip("v")
        html_url = data.get("html_url", "")
        if tag and tag != VERSION:
            _update_result["disponible"] = True
            _update_result["version"]    = tag
            _update_result["url"]        = html_url
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
        cprint(f"  ║  Actualizar: git pull  (en la carpeta del proyecto)  ║", C.YELLOW)
        cprint(f"  ║  {_update_result['url'][:52]:<52}  ║", C.YELLOW)
        cprint(f"  ╚══════════════════════════════════════════════════════╝", C.YELLOW)
        print()

# ════════════════════════════════════════════════════════════
#  BANNER
# ════════════════════════════════════════════════════════════

def show_banner():
    os.system('cls' if SO == 'Windows' else 'clear')

    if not SHOW_BANNER:
        # Banner mínimo para --no-banner
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
#  MEJORA 4: HISTORIAL DE TEMPERATURAS PERSISTENTE
# ════════════════════════════════════════════════════════════

def guardar_temp_historial(temp_cpu, temp_gpu, es_notebook):
    """Guarda lectura de temperatura en historial JSON persistente."""
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
        historial = historial[-100:]   # conservar últimas 100 lecturas
        with open(hist_path, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def mostrar_historial_temps():
    """Muestra tendencia de temperatura de las últimas lecturas."""
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

        # Tendencia
        cpus = [r['cpu'] for r in ultimas if r.get('cpu')]
        if len(cpus) >= 2:
            tendencia = cpus[-1] - cpus[0]
            if tendencia > 10:
                cprint(f"\n  TENDENCIA: +{tendencia:.1f}°C — temperatura en aumento sostenido.", C.RED)
                cprint("  Revisar ventilación y considerar cambio de pasta térmica.", C.YELLOW)
            elif tendencia < -5:
                cprint(f"\n  TENDENCIA: {tendencia:.1f}°C — temperatura bajando (buen estado).", C.GREEN)
            else:
                cprint(f"\n  TENDENCIA: {tendencia:+.1f}°C — temperatura estable.", C.GREEN)
    except Exception as e:
        cprint(f"  Error leyendo historial: {e}", C.YELLOW)

# ════════════════════════════════════════════════════════════
#  MÓDULOS LINUX
# ════════════════════════════════════════════════════════════

class Linux:

    @staticmethod
    def get_distro():
        distro = run("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'")
        pkg = "APT" if shutil.which("apt") else \
              "DNF" if shutil.which("dnf") else \
              "PACMAN" if shutil.which("pacman") else "Desconocido"
        return distro, pkg

    # ── 1: Hardware & Temperatura ────────────────────────────
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

        if temp_cpu:
            umbral = 75 if es_notebook else 70
            if temp_cpu < umbral:
                temp_str = f"{C.GREEN}{temp_cpu}°C (Normal){C.RESET}"
            elif temp_cpu < 85:
                temp_str = f"{C.YELLOW}{temp_cpu}°C (Elevada){C.RESET}"
            else:
                temp_str = f"{C.RED}{temp_cpu}°C CRITICA ⚠{C.RESET}"
        else:
            temp_str = f"{C.YELLOW}N/A (sudo apt install lm-sensors){C.RESET}"

        gpu_t = run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null").strip()
        try:    temp_gpu = float(gpu_t)
        except: temp_gpu = None

        if MODO_CLIENTE:
            Linux._sys_info_cliente(temp_cpu, temp_gpu, ram, uptime_str, es_notebook)
        else:
            print(f"\n  {C.BOLD}SERIAL {C.RESET}: {serial or 'No detectable'}")
            print(f"  {C.BOLD}EQUIPO {C.RESET}: {'NOTEBOOK' if es_notebook else 'DESKTOP'}")
            print(f"  {C.BOLD}CPU    {C.RESET}: {cpu}")
            print(f"  {C.BOLD}TEMP   {C.RESET}: {temp_str}")
            if temp_gpu:
                print(f"  {C.BOLD}TEMP GPU{C.RESET}: {C.CYAN}{temp_gpu}°C{C.RESET}")
            print(f"  {C.BOLD}RAM    {C.RESET}: {ram} en uso")
            print(f"  {C.BOLD}UPTIME {C.RESET}: {uptime_str}")
            print(f"  {C.BOLD}DISTRO {C.RESET}: {distro} ({pkg})")
            cprint("\n  [ GPU(s) Detectadas ]", C.YELLOW)
            gpu = run("lspci | grep -i 'vga\\|3d\\|display'")
            print(f"  {gpu or 'No detectada'}")

        # Guardar en historial
        guardar_temp_historial(temp_cpu, temp_gpu, es_notebook)

        # Mostrar historial de tendencia
        cprint("\n  [ Historial de Temperaturas ]", C.YELLOW)
        mostrar_historial_temps()

        print()
        resp = input(f"  {C.CYAN}Ejecutar diagnostico de pasta termica? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            analizar_pasta_termica(temp_cpu, temp_gpu, up_sec, es_notebook)

    @staticmethod
    def _sys_info_cliente(temp_cpu, temp_gpu, ram, uptime_str, es_notebook):
        """Output simplificado para mostrar frente al cliente."""
        section("DIAGNÓSTICO DE EQUIPO — Felipe Soluciones IT")
        umbral_ok  = 75 if es_notebook else 70
        umbral_alt = 85 if es_notebook else 80
        print()

        # CPU
        if temp_cpu:
            if temp_cpu < umbral_ok:
                cprint(f"  ✓  CPU funcionando correctamente ({temp_cpu}°C)", C.GREEN)
            elif temp_cpu < umbral_alt:
                cprint(f"  ⚠  Temperatura CPU elevada ({temp_cpu}°C) — se recomienda limpieza", C.YELLOW)
            else:
                cprint(f"  ✗  Temperatura CPU crítica ({temp_cpu}°C) — requiere atención urgente", C.RED)
        else:
            cprint("  ℹ  Temperatura CPU: no disponible", C.GRAY)

        # GPU
        if temp_gpu:
            gpu_umbral = 80 if es_notebook else 75
            if temp_gpu < gpu_umbral:
                cprint(f"  ✓  GPU funcionando correctamente ({temp_gpu}°C)", C.GREEN)
            else:
                cprint(f"  ⚠  Temperatura GPU elevada ({temp_gpu}°C)", C.YELLOW)

        # RAM
        cprint(f"  ✓  Memoria RAM: {ram} en uso", C.GREEN)
        cprint(f"  ✓  Tiempo de uso del sistema: {uptime_str}", C.GREEN)

    # ── 2: Mantenimiento ─────────────────────────────────────
    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA [LINUX]")
        _, pkg = Linux.get_distro()

        cprint("\n  Selecciona que operaciones ejecutar:\n", C.GRAY)
        cprint("  [1]  Actualizar el sistema",                    C.RESET)
        cprint("  [2]  Purgar paquetes huerfanos y residuales",   C.RESET)
        cprint("  [3]  Limpiar cache del gestor de paquetes",     C.RESET)
        cprint("  [4]  Limpiar /tmp y archivos temporales",       C.RESET)
        cprint("  [5]  Limpiar logs del sistema (journalctl)",    C.RESET)
        cprint("  [6]  Limpiar cache de usuario (~/.cache)",      C.RESET)
        cprint("  [7]  TODO lo anterior",                         C.CYAN)
        print()
        op = input(f"  {C.CYAN}Seleccione operacion: {C.RESET}").strip()

        hacer = set()
        if op == "7":   hacer = {"1","2","3","4","5","6"}
        elif op in {"1","2","3","4","5","6"}: hacer = {op}
        else:
            cprint("  Opcion no valida.", C.YELLOW)
            return

        if "1" in hacer:
            cprint("\n  [ Actualizaciones del Sistema ]", C.YELLOW)
            if pkg == "APT":
                os.system("sudo apt update")
                upgradable = run("apt list --upgradable 2>/dev/null | grep -c upgradable")
                cprint(f"  Paquetes a actualizar: {upgradable}", C.CYAN)
                if upgradable.strip() != "0":
                    resp = input(f"  {C.CYAN}Instalar actualizaciones? (S/N): {C.RESET}").strip().lower()
                    if resp == "s":
                        os.system("sudo apt upgrade -y")
                        cprint("  Sistema actualizado.", C.GREEN)
                    else:
                        cprint("  Actualizacion omitida.", C.GRAY)
                else:
                    cprint("  El sistema ya esta actualizado.", C.GREEN)
            elif pkg == "DNF":
                upgradable = run("dnf check-update 2>/dev/null | grep -c '^[a-zA-Z]'")
                cprint(f"  Paquetes a actualizar: {upgradable}", C.CYAN)
                resp = input(f"  {C.CYAN}Instalar actualizaciones? (S/N): {C.RESET}").strip().lower()
                if resp == "s": os.system("sudo dnf upgrade -y")
            elif pkg == "PACMAN":
                os.system("sudo pacman -Syu --noconfirm")
            else:
                cprint("  Gestor de paquetes no soportado.", C.RED)

        if "2" in hacer:
            cprint("\n  [ Purga de Paquetes Huerfanos y Residuales ]", C.YELLOW)
            if pkg == "APT":
                huerfanos  = run("apt-get autoremove --dry-run 2>/dev/null | grep '^Remov' | wc -l").strip()
                residuales = run("dpkg -l | grep '^rc' | wc -l").strip()
                cprint(f"  Paquetes huerfanos   : {huerfanos}", C.CYAN)
                cprint(f"  Paquetes residuales  : {residuales}", C.CYAN)
                if int(huerfanos or 0) > 0:
                    resp = input(f"  {C.CYAN}Eliminar paquetes huerfanos? (S/N): {C.RESET}").strip().lower()
                    if resp == "s":
                        os.system("sudo apt autoremove -y")
                        cprint("  Huerfanos eliminados.", C.GREEN)
                if int(residuales or 0) > 0:
                    resp = input(f"  {C.CYAN}Purgar configuraciones residuales? (S/N): {C.RESET}").strip().lower()
                    if resp == "s":
                        os.system("dpkg -l | grep '^rc' | awk '{print $2}' | xargs sudo dpkg --purge 2>/dev/null")
                        cprint("  Residuales purgados.", C.GREEN)
                if int(huerfanos or 0) == 0 and int(residuales or 0) == 0:
                    cprint("  No hay paquetes huerfanos ni residuales.", C.GREEN)
            elif pkg == "DNF":
                os.system("sudo dnf autoremove -y")
                cprint("  Huerfanos eliminados.", C.GREEN)
            elif pkg == "PACMAN":
                huerfanos = run("pacman -Qdtq 2>/dev/null")
                if huerfanos.strip():
                    cprint(f"  Paquetes huerfanos:\n{huerfanos}", C.CYAN)
                    resp = input(f"  {C.CYAN}Eliminar huerfanos? (S/N): {C.RESET}").strip().lower()
                    if resp == "s":
                        os.system("sudo pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null")
                        cprint("  Huerfanos eliminados.", C.GREEN)
                else:
                    cprint("  No hay paquetes huerfanos.", C.GREEN)

        if "3" in hacer:
            cprint("\n  [ Limpieza de Cache del Gestor ]", C.YELLOW)
            if pkg == "APT":
                cache_size = run("du -sh /var/cache/apt/archives/ 2>/dev/null | cut -f1")
                cprint(f"  Tamanio cache APT: {cache_size}", C.CYAN)
                resp = input(f"  {C.CYAN}Limpiar cache APT? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    os.system("sudo apt clean && sudo apt autoclean")
                    new_size = run("du -sh /var/cache/apt/archives/ 2>/dev/null | cut -f1")
                    cprint(f"  Cache limpiada. Nuevo tamanio: {new_size}", C.GREEN)
            elif pkg == "DNF":
                os.system("sudo dnf clean all")
                cprint("  Cache DNF limpiada.", C.GREEN)
            elif pkg == "PACMAN":
                cache_size = run("du -sh /var/cache/pacman/pkg/ 2>/dev/null | cut -f1")
                cprint(f"  Tamanio cache pacman: {cache_size}", C.CYAN)
                resp = input(f"  {C.CYAN}Limpiar cache pacman (mantener 2 versiones)? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    if shutil.which("paccache"):
                        os.system("sudo paccache -rk2")
                    else:
                        os.system("sudo pacman -Sc --noconfirm")
                    cprint("  Cache pacman limpiada.", C.GREEN)

        if "4" in hacer:
            cprint("\n  [ Limpieza de /tmp y Temporales ]", C.YELLOW)
            for tmp in ["/tmp", "/var/tmp"]:
                if os.path.exists(tmp):
                    size  = run(f"du -sh {tmp} 2>/dev/null | cut -f1")
                    count = run(f"find {tmp} -type f -atime +2 2>/dev/null | wc -l").strip()
                    cprint(f"  {tmp:<15} {size:<10} ({count} archivos > 2 dias)", C.CYAN)
            resp = input(f"  {C.CYAN}Limpiar archivos de mas de 2 dias? (S/N): {C.RESET}").strip().lower()
            if resp == "s":
                os.system("sudo find /tmp -type f -atime +2 -delete 2>/dev/null")
                os.system("sudo find /var/tmp -type f -atime +2 -delete 2>/dev/null")
                os.system("sudo find /tmp /var/tmp -type d -empty -delete 2>/dev/null")
                cprint("  Temporales limpiados.", C.GREEN)

        if "5" in hacer:
            cprint("\n  [ Limpieza de Logs del Sistema ]", C.YELLOW)
            log_size = run("journalctl --disk-usage 2>/dev/null | grep -oE '[0-9.]+ [A-Z]?B'")
            cprint(f"  Tamanio actual de logs: {log_size}", C.CYAN)
            cprint("  Opciones:", C.GRAY)
            cprint("    [1] Conservar ultimos 7 dias",  C.RESET)
            cprint("    [2] Conservar ultimos 30 dias", C.RESET)
            cprint("    [3] Conservar solo 500 MB",     C.RESET)
            cprint("    [4] Omitir",                    C.RESET)
            sub = input(f"  {C.CYAN}Seleccione: {C.RESET}").strip()
            if sub == "1":   os.system("sudo journalctl --vacuum-time=7d");   cprint("  Logs > 7 dias eliminados.",  C.GREEN)
            elif sub == "2": os.system("sudo journalctl --vacuum-time=30d");  cprint("  Logs > 30 dias eliminados.", C.GREEN)
            elif sub == "3": os.system("sudo journalctl --vacuum-size=500M"); cprint("  Logs reducidos a 500 MB.",   C.GREEN)
            else: cprint("  Limpieza de logs omitida.", C.GRAY)
            gz_size = run("find /var/log -name '*.gz' -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1")
            if gz_size and gz_size.strip() != "0":
                resp = input(f"  {C.CYAN}Eliminar logs comprimidos .gz ({gz_size})? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    os.system("sudo find /var/log -name '*.gz' -delete 2>/dev/null")
                    os.system("sudo find /var/log -name '*.old' -delete 2>/dev/null")
                    cprint("  Logs comprimidos eliminados.", C.GREEN)

        if "6" in hacer:
            cprint("\n  [ Limpieza de Cache de Usuario (~/.cache) ]", C.YELLOW)
            cache_dir = os.path.expanduser("~/.cache")
            if os.path.exists(cache_dir):
                size = run(f"du -sh {cache_dir} 2>/dev/null | cut -f1")
                cprint(f"  Tamanio de ~/.cache: {size}", C.CYAN)
                top = run(f"du -sh {cache_dir}/* 2>/dev/null | sort -rh | head -8")
                if top:
                    cprint("  Mas grandes:", C.GRAY)
                    for line in top.splitlines():
                        print(f"    {line}")
                resp = input(f"  {C.CYAN}Limpiar ~/.cache? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    os.system(f"rm -rf {cache_dir}/* 2>/dev/null")
                    cprint("  Cache de usuario limpiada.", C.GREEN)
            else:
                cprint("  ~/.cache no existe.", C.GRAY)

        cprint("\n  [ Resumen Post-Mantenimiento ]", C.CYAN)
        disk_libre = run("df -h / | awk 'NR==2{print $4}'")
        ram_libre  = run("free -h | awk '/^Mem/{print $7}'")
        cprint(f"  Espacio libre en /: {C.GREEN}{disk_libre}{C.RESET}")
        cprint(f"  RAM disponible    : {C.GREEN}{ram_libre}{C.RESET}")

    # ── 3: Salud de Discos ───────────────────────────────────
    @staticmethod
    def disk_health():
        section("SALUD: DISCOS Y ALMACENAMIENTO [LINUX]")
        cprint("\n  [ Uso de Particiones ]", C.YELLOW)
        os.system("df -h | grep -E 'Filesystem|/dev/sd|/dev/nvme|/dev/mapper|/$'")
        cprint("\n  [ Unidades de Almacenamiento ]", C.YELLOW)
        os.system("lsblk -o NAME,SIZE,MODEL,TYPE,MOUNTPOINT | grep -E 'NAME|disk'")
        cprint("\n  [ Estado S.M.A.R.T. ]", C.YELLOW)
        if shutil.which("smartctl"):
            disks = run("lsblk -dn -o NAME | grep -E '^sd|^nvme'").splitlines()
            if disks:
                for d in disks:
                    cprint(f"\n  Disco /dev/{d}:", C.CYAN)
                    os.system(f"sudo smartctl -H /dev/{d} | grep -E 'overall-health|result'")
            else:
                cprint("  No se detectaron discos compatibles.", C.YELLOW)
        else:
            cprint("  smartctl no encontrado. Instalar: sudo apt install smartmontools", C.YELLOW)
        cprint("\n  [ Salud de Bateria ]", C.YELLOW)
        bat = run("upower -e 2>/dev/null | grep BAT")
        if bat:
            os.system(f"upower -i {bat} | grep -E 'state|percentage|capacity'")
        else:
            print("  Bateria: N/A")

    # ── 4: Auditoría de Seguridad (con confirmación) ─────────
    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD [LINUX]")

        # ── MEJORA 2: Aviso de confirmación ──────────────────
        cprint("\n  ⚠  AVISO: Este módulo escanea puertos activos y conexiones de red.", C.YELLOW)
        cprint("     En entornos corporativos puede activar alertas de seguridad.", C.YELLOW)
        cprint("     Úsalo solo en equipos que sean de tu propiedad o con autorización.", C.YELLOW)
        resp = input(f"\n  {C.CYAN}  Confirmar ejecución (S/N): {C.RESET}").strip().lower()
        if resp != "s":
            cprint("  Módulo cancelado.", C.GRAY)
            return

        cprint("\n  [ Puertos en Escucha ]", C.YELLOW)
        os.system("sudo ss -tunlp | grep LISTEN")
        cprint("\n  [ Estado del Firewall (UFW) ]", C.YELLOW)
        if shutil.which("ufw"):
            os.system("sudo ufw status verbose")
        elif shutil.which("firewall-cmd"):
            os.system("sudo firewall-cmd --list-all")
        else:
            cprint("  UFW/firewalld no encontrado.", C.YELLOW)
            os.system("sudo iptables -L -n --line-numbers 2>/dev/null | head -30")
        cprint("\n  [ Usuarios del Sistema ]", C.YELLOW)
        os.system("cat /etc/passwd | grep -E '/bin/bash|/bin/sh' | cut -d: -f1,3,6")
        cprint("\n  [ Ultimos Logins ]", C.YELLOW)
        os.system("last | head -10")
        cprint("\n  [ Intentos de Login Fallidos ]", C.YELLOW)
        os.system("sudo grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -10 || "
                  "sudo journalctl _SYSTEMD_UNIT=sshd.service | grep 'Failed' | tail -10")
        cprint("\n  [ Procesos con Conexiones de Red ]", C.YELLOW)
        os.system("sudo ss -tp | grep ESTAB | head -15")

    # ── 5: Reporte de Eventos ────────────────────────────────
    @staticmethod
    def event_report():
        section("REPORTE DE EVENTOS DEL SISTEMA [LINUX]")
        cprint("\n  [ Errores Criticos (journalctl) ]", C.YELLOW)
        os.system("sudo journalctl -p err -n 20 --no-pager 2>/dev/null || "
                  "sudo grep -i 'error\\|critical' /var/log/syslog 2>/dev/null | tail -20")
        cprint("\n  [ Ultimos Reinicios ]", C.YELLOW)
        os.system("last reboot | head -10")
        cprint("\n  [ Servicios con Fallo ]", C.YELLOW)
        os.system("systemctl --failed --no-pager 2>/dev/null")
        cprint("\n  [ Uso de Memoria y OOM Killer ]", C.YELLOW)
        os.system("sudo journalctl -k | grep -i 'oom\\|killed' | tail -10 2>/dev/null || echo '  Sin eventos OOM recientes.'")
        cprint("\n  [ Temperatura de Disco (dmesg) ]", C.YELLOW)
        os.system("sudo dmesg | grep -i 'temperature\\|thermal\\|overheat' | tail -10 || echo '  Sin alertas termicas.'")

    # ── 6: Inventario de Software ────────────────────────────
    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE INSTALADO [LINUX]")
        _, pkg = Linux.get_distro()
        cprint("\n  [ Paquetes Instalados ]", C.YELLOW)
        if pkg == "APT":
            out   = run("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -60")
            count = run("dpkg -l | grep '^ii' | wc -l")
        elif pkg == "DNF":
            out   = run("rpm -qa --qf '%{NAME} %{VERSION}\n' | sort | head -60")
            count = run("rpm -qa | wc -l")
        elif pkg == "PACMAN":
            out   = run("pacman -Q | head -60")
            count = run("pacman -Q | wc -l")
        else:
            out = ""; count = "?"
        print(f"\n  Total de paquetes instalados: {C.CYAN}{count}{C.RESET}\n")
        if out:
            for line in out.splitlines():
                print(f"  {line}")
        cprint(f"\n  (Mostrando primeros 60 de {count})", C.GRAY)
        cprint("\n  [ Aplicaciones Snap/Flatpak ]", C.YELLOW)
        if shutil.which("snap"):
            snaps = run("snap list 2>/dev/null")
            print(snaps or "  Sin apps Snap.")
        if shutil.which("flatpak"):
            flatpaks = run("flatpak list --app --columns=name,version 2>/dev/null")
            print(flatpaks or "  Sin apps Flatpak.")

    # ── 7: Exportar Reporte ──────────────────────────────────
    @staticmethod
    def export_html():
        run_export()

    # ── 8: Ping / Conectividad ───────────────────────────────
    @staticmethod
    def network_ping():
        section("PING / TEST DE CONECTIVIDAD [LINUX]")
        defaults = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "google.com", "github.com"]
        extra    = input(f"  {C.CYAN}Agregar IPs/dominios separados por coma (Enter para omitir): {C.RESET}").strip()
        targets  = defaults + [t.strip() for t in extra.split(",") if t.strip()]
        cprint(f"\n  {'DESTINO':<25} {'ESTADO':<12} {'LATENCIA'}", C.YELLOW)
        cprint(f"  {'-'*55}", C.GRAY)
        for t in targets:
            result = run(f"ping -c 2 -W 2 {t} 2>/dev/null")
            if "2 received" in result or "1 received" in result:
                match   = re.search(r"min/avg/max.*?=([\d.]+)/([\d.]+)", result)
                latency = f"{match.group(2)} ms" if match else "OK"
                cprint(f"  {t:<25} {'ONLINE':<12} {latency}", C.GREEN)
            else:
                cprint(f"  {t:<25} {'OFFLINE':<12} ---", C.RED)
        cprint("\n  [ Resolucion DNS ]", C.YELLOW)
        for domain in ["google.com", "cloudflare.com", "github.com"]:
            dns    = run(f"dig +short {domain} 2>/dev/null || nslookup {domain} 2>/dev/null | grep 'Address' | tail -1")
            status = C.GREEN + "OK" + C.RESET if dns else C.RED + "FALLO" + C.RESET
            print(f"  {domain:<25} {status}  {dns[:40]}")
        cprint("\n  [ Interfaces de Red ]", C.YELLOW)
        os.system("ip -br addr show 2>/dev/null || ifconfig 2>/dev/null | grep -E 'inet|flags'")

    # ── 9: Escaneo de Red Local (con confirmación) ───────────
    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL [LINUX]")

        # ── MEJORA 2: Aviso de confirmación ──────────────────
        cprint("\n  ⚠  AVISO: El escaneo de red puede activar alertas en firewalls", C.YELLOW)
        cprint("     o sistemas de detección de intrusos (IDS/IPS) corporativos.", C.YELLOW)
        cprint("     Úsalo solo en redes de tu propiedad o con autorización expresa.", C.YELLOW)
        resp = input(f"\n  {C.CYAN}  Confirmar ejecución (S/N): {C.RESET}").strip().lower()
        if resp != "s":
            cprint("  Módulo cancelado.", C.GRAY)
            return

        gateway  = run("ip route | grep default | awk '{print $3}' | head -1")
        local_ip = run("hostname -I | awk '{print $1}'")
        iface    = run("ip route | grep default | awk '{print $5}' | head -1")
        if not gateway:
            cprint("  No se detectó gateway. Verificar conexión de red.", C.RED)
            return
        parts  = local_ip.rsplit(".", 1)
        subnet = parts[0] + ".0/24" if len(parts) == 2 else "192.168.1.0/24"
        print(f"\n  IP Local  : {C.CYAN}{local_ip}{C.RESET}")
        print(f"  Gateway   : {C.CYAN}{gateway}{C.RESET}")
        print(f"  Interfaz  : {C.CYAN}{iface}{C.RESET}")
        print(f"  Subred    : {C.CYAN}{subnet}{C.RESET}")
        cprint(f"\n  Escaneando {subnet} (ping sweep)...", C.YELLOW)
        cprint(f"  {'IP':<20} {'HOSTNAME':<30} {'ESTADO'}", C.YELLOW)
        cprint(f"  {'-'*65}", C.GRAY)
        if shutil.which("nmap"):
            cprint("  Usando nmap para escaneo detallado...\n", C.GRAY)
            raw        = run(f"sudo nmap -sn {subnet} 2>/dev/null", timeout=60)
            current_ip = ""
            for line in raw.splitlines():
                ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if "Nmap scan report" in line and ip_match:
                    current_ip = ip_match.group(1)
                elif "Host is up" in line and current_ip:
                    hostname = run(f"hostname -f {current_ip} 2>/dev/null || echo ''")
                    marker   = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if current_ip == local_ip else ""
                    cprint(f"  {current_ip:<20} {hostname[:28]:<30} ONLINE {marker}", C.GREEN)
                    current_ip = ""
        else:
            cprint("  nmap no encontrado, usando ping sweep basico...", C.GRAY)
            base   = parts[0] + "." if len(parts) == 2 else "192.168.1."
            activos = 0
            for i in range(1, 255):
                ip     = f"{base}{i}"
                result = run(f"ping -c 1 -W 1 {ip} 2>/dev/null")
                if "1 received" in result or "bytes from" in result:
                    hostname = run(f"nslookup {ip} 2>/dev/null | grep 'name =' | awk '{{print $4}}'") or "---"
                    marker   = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if ip == local_ip else ""
                    cprint(f"  {ip:<20} {hostname[:28]:<30} ONLINE {marker}", C.GREEN)
                    activos += 1
            cprint(f"\n  Total dispositivos activos: {activos}", C.CYAN)
        cprint("\n  [ Tabla ARP - Dispositivos Recientes ]", C.YELLOW)
        os.system("arp -n 2>/dev/null | grep -v 'incomplete' | head -20")


# ════════════════════════════════════════════════════════════
#  MÓDULOS WINDOWS
# ════════════════════════════════════════════════════════════

class Windows:

    @staticmethod
    def _ps(cmd):
        full = f'powershell -NoProfile -ExecutionPolicy Bypass -Command "{cmd}"'
        return run(full)

    # ── 1: Hardware & Temperatura ────────────────────────────
    @staticmethod
    def sys_info():
        section("INFRAESTRUCTURA Y SALUD TERMICA [WINDOWS]")
        cpu    = Windows._ps("(Get-CimInstance Win32_Processor).Name.Trim()")
        serial = Windows._ps("(Get-CimInstance Win32_BIOS).SerialNumber.Trim()")
        ram_obj= Windows._ps(
            "$r=Get-CimInstance Win32_OperatingSystem;"
            "[math]::Round(($r.TotalVisibleMemorySize-$r.FreePhysicalMemory)/1MB,2).ToString()"
            "+' / '+"
            "[math]::Round($r.TotalVisibleMemorySize/1MB,2).ToString()+' GB'"
        )
        uptime = Windows._ps(
            "$r=Get-CimInstance Win32_OperatingSystem;"
            "$u=(Get-Date)-$r.LastBootUpTime;"
            "'{0}d {1}h {2}m' -f $u.Days,$u.Hours,$u.Minutes"
        )
        chassis_raw = Windows._ps(
            "(Get-CimInstance Win32_SystemEnclosure).ChassisTypes | "
            "ForEach-Object { $_ } | Select-Object -First 1"
        ).strip()
        try:
            chassis_type = int(chassis_raw)
            es_notebook  = chassis_type in [8,9,10,11,12,14,18,21]
        except Exception:
            es_notebook = False

        try:
            up_sec = int(Windows._ps(
                "$r=Get-CimInstance Win32_OperatingSystem;"
                "[int](((Get-Date)-$r.LastBootUpTime).TotalSeconds)"
            ).strip())
        except Exception:
            up_sec = 0

        temp_cmd = (
            "try { $t=Get-CimInstance -Namespace 'root/OpenHardwareMonitor' -ClassName Sensor "
            "-Filter \"SensorType='Temperature' AND Name LIKE '%CPU%'\" -EA Stop | "
            "Select-Object -First 1; [math]::Round($t.Value,1) } catch { 'N/A' }"
        )
        temp_val = Windows._ps(temp_cmd)
        try:
            temp_cpu = float(temp_val)
            umbral   = 75 if es_notebook else 70
            if temp_cpu < umbral:
                temp_str = f"{C.GREEN}{temp_cpu}°C (Normal){C.RESET}"
            elif temp_cpu < 85:
                temp_str = f"{C.YELLOW}{temp_cpu}°C (Elevada){C.RESET}"
            else:
                temp_str = f"{C.RED}{temp_cpu}°C CRITICA ⚠{C.RESET}"
        except ValueError:
            temp_cpu = None
            temp_str = f"{C.YELLOW}N/A (requiere OpenHardwareMonitor como Admin){C.RESET}"

        gpu_temp_cmd = (
            "try { $t=Get-CimInstance -Namespace 'root/OpenHardwareMonitor' -ClassName Sensor "
            "-Filter \"SensorType='Temperature' AND Name LIKE '%GPU%'\" -EA Stop | "
            "Select-Object -First 1; [math]::Round($t.Value,1) } catch { 'N/A' }"
        )
        gpu_val = Windows._ps(gpu_temp_cmd)
        try:    temp_gpu = float(gpu_val)
        except: temp_gpu = None

        if MODO_CLIENTE:
            Windows._sys_info_cliente(temp_cpu, temp_gpu, ram_obj, uptime, es_notebook)
        else:
            print(f"\n  {C.BOLD}SERIAL  {C.RESET}: {serial or 'No detectable'}")
            print(f"  {C.BOLD}EQUIPO  {C.RESET}: {'NOTEBOOK' if es_notebook else 'DESKTOP'}")
            print(f"  {C.BOLD}CPU     {C.RESET}: {cpu}")
            print(f"  {C.BOLD}TEMP CPU{C.RESET}: {temp_str}")
            if temp_gpu:
                print(f"  {C.BOLD}TEMP GPU{C.RESET}: {C.CYAN}{temp_gpu}°C{C.RESET}")
            print(f"  {C.BOLD}RAM     {C.RESET}: {ram_obj}")
            print(f"  {C.BOLD}UPTIME  {C.RESET}: {uptime}")
            cprint("\n  [ GPU(s) Detectadas ]", C.YELLOW)
            gpu = Windows._ps(
                "Get-CimInstance Win32_VideoController | "
                "Select-Object Name,@{N='RAM(MB)';E={[math]::Round($_.AdapterRAM/1MB,0)}},DriverVersion | "
                "Format-Table -AutoSize | Out-String"
            )
            print(gpu)

        # Guardar en historial
        guardar_temp_historial(temp_cpu, temp_gpu, es_notebook)

        # Mostrar historial
        cprint("\n  [ Historial de Temperaturas ]", C.YELLOW)
        mostrar_historial_temps()

        resp = input(f"  {C.CYAN}Ejecutar diagnostico de pasta termica? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            analizar_pasta_termica(temp_cpu, temp_gpu, up_sec, es_notebook)

    @staticmethod
    def _sys_info_cliente(temp_cpu, temp_gpu, ram, uptime, es_notebook):
        section("DIAGNÓSTICO DE EQUIPO — Felipe Soluciones IT")
        umbral_ok  = 75 if es_notebook else 70
        umbral_alt = 85 if es_notebook else 80
        print()
        if temp_cpu:
            if temp_cpu < umbral_ok:
                cprint(f"  ✓  CPU funcionando correctamente ({temp_cpu}°C)", C.GREEN)
            elif temp_cpu < umbral_alt:
                cprint(f"  ⚠  Temperatura CPU elevada ({temp_cpu}°C) — se recomienda limpieza", C.YELLOW)
            else:
                cprint(f"  ✗  Temperatura CPU crítica ({temp_cpu}°C) — requiere atención urgente", C.RED)
        else:
            cprint("  ℹ  Temperatura CPU: requiere OpenHardwareMonitor instalado", C.GRAY)
        if temp_gpu:
            gpu_umbral = 80 if es_notebook else 75
            if temp_gpu < gpu_umbral:
                cprint(f"  ✓  GPU funcionando correctamente ({temp_gpu}°C)", C.GREEN)
            else:
                cprint(f"  ⚠  Temperatura GPU elevada ({temp_gpu}°C)", C.YELLOW)
        cprint(f"  ✓  Memoria RAM: {ram} en uso", C.GREEN)
        cprint(f"  ✓  Tiempo de uso del sistema: {uptime}", C.GREEN)

    # ── 2: Mantenimiento ─────────────────────────────────────
    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA [WINDOWS]")
        cprint("\n  [ Verificando PSWindowsUpdate ]", C.YELLOW)
        has_mod = Windows._ps(
            "if(Get-Module -ListAvailable -Name PSWindowsUpdate -EA SilentlyContinue)"
            "{'SI'} else {'NO'}"
        )
        if has_mod.strip() == "NO":
            cprint("  Instalando PSWindowsUpdate...", C.YELLOW)
            Windows._ps(
                "Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force | Out-Null;"
                "Install-Module -Name PSWindowsUpdate -Scope CurrentUser -Force"
            )
            cprint("  PSWindowsUpdate instalado.", C.GREEN)
        cprint("\n  [ Actualizaciones Disponibles ]", C.YELLOW)
        updates = Windows._ps(
            "Import-Module PSWindowsUpdate; "
            "Get-WindowsUpdate | Select-Object KB,Title | Format-Table -AutoSize | Out-String"
        )
        if updates.strip():
            print(updates)
            resp = input(f"  {C.CYAN}Instalar todas las actualizaciones? (S/N): {C.RESET}")
            if resp.lower() == 's':
                Windows._ps(
                    "Import-Module PSWindowsUpdate; "
                    "Get-WindowsUpdate -AcceptAll -Install -AutoReboot:$false"
                )
        else:
            cprint("  Sistema actualizado.", C.GREEN)
        cprint("\n  [ Limpieza de Temporales ]", C.YELLOW)
        temp_paths = [
            os.environ.get("TEMP", ""),
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp"),
            os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Prefetch"),
        ]
        total = 0
        for p in temp_paths:
            if p and os.path.exists(p):
                size = sum(
                    os.path.getsize(os.path.join(dp, f))
                    for dp, _, files in os.walk(p)
                    for f in files
                    if os.path.exists(os.path.join(dp, f))
                )
                total += size
                liberado = 0
                for dp, dirs, files in os.walk(p):
                    for f in files:
                        try:
                            fp = os.path.join(dp, f)
                            fsize = os.path.getsize(fp)
                            os.remove(fp)
                            liberado += fsize
                        except Exception:
                            pass
                cprint(f"  Limpiado: {p}  ({liberado/1024/1024:.1f} MB liberados de {size/1024/1024:.1f} MB)", C.GREEN)
                total += liberado
        cprint(f"  Total liberado: {total/1024/1024:.1f} MB", C.CYAN)
        cprint("\n  [ Optimizacion de Unidades ]", C.YELLOW)
        drives = Windows._ps(
            "Get-Volume | Where-Object {$_.DriveType -eq 'Fixed' -and $_.DriveLetter} | "
            "Select-Object -ExpandProperty DriveLetter"
        )
        for d in drives.splitlines():
            d = d.strip()
            if d:
                cprint(f"  Optimizando {d}:...", C.GRAY)
                Windows._ps(f"Optimize-Volume -DriveLetter {d} -ReTrim -EA SilentlyContinue")
                cprint(f"  {d}: OK", C.GREEN)

    # ── 3: Salud de Discos ───────────────────────────────────
    @staticmethod
    def disk_health():
        section("SALUD: DISCOS Y ALMACENAMIENTO [WINDOWS]")
        cprint("\n  [ Uso de Particiones ]", C.YELLOW)
        partitions = Windows._ps(
            "Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | "
            "Select-Object Name,"
            "@{N='Usado GB';E={[math]::Round($_.Used/1GB,2)}},"
            "@{N='Libre GB';E={[math]::Round($_.Free/1GB,2)}},"
            "@{N='Total GB';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}},"
            "@{N='Uso %';E={[math]::Round($_.Used/($_.Used+$_.Free)*100,1)}} | "
            "Format-Table -AutoSize | Out-String"
        )
        print(partitions)
        cprint("\n  [ Discos Fisicos ]", C.YELLOW)
        disks = Windows._ps(
            "Get-PhysicalDisk | Select-Object FriendlyName,MediaType,HealthStatus,OperationalStatus | "
            "Format-Table -AutoSize | Out-String"
        )
        print(disks)
        cprint("\n  [ Estado S.M.A.R.T. ]", C.YELLOW)
        smart = Windows._ps(
            "Get-WmiObject -Namespace root\\wmi -Class MSStorageDriver_FailurePredictStatus "
            "-EA SilentlyContinue | Select-Object InstanceName,PredictFailure | "
            "Format-Table -AutoSize | Out-String"
        )
        print(smart or "  Sin datos SMART disponibles via WMI.")

    # ── 4: Auditoría de Seguridad (con confirmación) ─────────
    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD [WINDOWS]")

        # ── MEJORA 2: Aviso de confirmación ──────────────────
        cprint("\n  ⚠  AVISO: Este módulo lista puertos activos y usuarios del sistema.", C.YELLOW)
        cprint("     En entornos corporativos puede activar alertas de seguridad.", C.YELLOW)
        cprint("     Úsalo solo en equipos que sean de tu propiedad o con autorización.", C.YELLOW)
        resp = input(f"\n  {C.CYAN}  Confirmar ejecución (S/N): {C.RESET}").strip().lower()
        if resp != "s":
            cprint("  Módulo cancelado.", C.GRAY)
            return

        cprint("\n  [ Puertos en Escucha ]", C.YELLOW)
        ports = Windows._ps(
            "Get-NetTCPConnection -State Listen -EA SilentlyContinue | "
            "Select-Object LocalAddress,LocalPort,"
            "@{N='Proceso';E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).Name}} | "
            "Sort-Object LocalPort | Format-Table -AutoSize | Out-String"
        )
        print(ports)
        cprint("\n  [ Estado del Firewall ]", C.YELLOW)
        fw = Windows._ps(
            "Get-NetFirewallProfile | "
            "Select-Object Name,Enabled,DefaultInboundAction,DefaultOutboundAction | "
            "Format-Table -AutoSize | Out-String"
        )
        print(fw)
        cprint("\n  [ Usuarios Locales ]", C.YELLOW)
        users = Windows._ps(
            "Get-LocalUser | Select-Object Name,Enabled,LastLogon,PasswordLastSet | "
            "Format-Table -AutoSize | Out-String"
        )
        print(users)
        cprint("\n  [ Ultimos 5 Intentos de Login Fallidos ]", C.YELLOW)
        events = Windows._ps(
            "try { Get-WinEvent -FilterHashtable @{LogName='Security';Id=4625} "
            "-MaxEvents 5 -EA Stop | Select-Object TimeCreated,Message | "
            "ForEach-Object { $_.TimeCreated.ToString() } } catch { 'Sin eventos.' }"
        )
        for line in events.splitlines():
            cprint(f"  {line}", C.RED)

    # ── 5: Reporte de Eventos ────────────────────────────────
    @staticmethod
    def event_report():
        section("REPORTE DE EVENTOS DEL SISTEMA [WINDOWS]")
        logs = [
            ("Errores Criticos del Sistema", "System",      1),
            ("Errores del Sistema",          "System",      2),
            ("Errores de Aplicacion",        "Application", 2),
            ("Advertencias del Sistema",     "System",      3),
        ]
        for name, log, level in logs:
            cprint(f"\n  [ {name} ]", C.YELLOW)
            out = Windows._ps(
                f"try {{ Get-WinEvent -FilterHashtable @{{LogName='{log}';Level={level};"
                f"StartTime=(Get-Date).AddDays(-1)}} -MaxEvents 10 -EA Stop | "
                f"Select-Object TimeCreated,Id,@{{N='Msg';E={{($_.Message -split '`n')[0]}}}}"
                f" | Format-Table -AutoSize | Out-String }} catch {{ 'Sin eventos.' }}"
            )
            print(out or "  Sin eventos recientes.")
        cprint("\n  [ Ultimos Reinicios ]", C.YELLOW)
        reboots = Windows._ps(
            "try { Get-WinEvent -FilterHashtable @{LogName='System';Id=@(1074,6006,6008)} "
            "-MaxEvents 5 -EA Stop | "
            "Select-Object TimeCreated,Id | Format-Table -AutoSize | Out-String } "
            "catch { 'Sin datos de reinicios.' }"
        )
        print(reboots)

    # ── 6: Inventario de Software ────────────────────────────
    @staticmethod
    def software_inventory():
        section("INVENTARIO DE SOFTWARE INSTALADO [WINDOWS]")
        cprint("\n  Recopilando programas instalados...", C.GRAY)
        sw = Windows._ps(
            "$paths = @("
            "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
            "'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
            "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*');"
            "$all = $paths | ForEach-Object { Get-ItemProperty $_ -EA SilentlyContinue } | "
            "Where-Object { $_.DisplayName } | "
            "Select-Object DisplayName,DisplayVersion,Publisher | Sort-Object DisplayName;"
            "Write-Host \"Total: $($all.Count) programas\";"
            "$all | Format-Table -AutoSize | Out-String"
        )
        print(sw)

    # ── 7: Exportar Reporte ──────────────────────────────────
    @staticmethod
    def export_html():
        run_export()

    # ── 8: Ping / Conectividad ───────────────────────────────
    @staticmethod
    def network_ping():
        section("PING / TEST DE CONECTIVIDAD [WINDOWS]")
        defaults = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "google.com", "github.com"]
        extra    = input(f"  {C.CYAN}Agregar IPs/dominios separados por coma (Enter para omitir): {C.RESET}").strip()
        targets  = defaults + [t.strip() for t in extra.split(",") if t.strip()]
        cprint(f"\n  {'DESTINO':<25} {'ESTADO':<12} {'LATENCIA'}", C.YELLOW)
        cprint(f"  {'-'*55}", C.GRAY)
        for t in targets:
            result  = run(f"ping -n 2 -w 2000 {t}", timeout=10)
            if "TTL=" in result or "ttl=" in result:
                match   = re.search(r"Media = (\d+)ms|Promedio = (\d+)ms|Average = (\d+)ms|(\d+)ms", result)
                latency = f"{match.group(0)}" if match else "OK"
                cprint(f"  {t:<25} {'ONLINE':<12} {latency}", C.GREEN)
            else:
                cprint(f"  {t:<25} {'OFFLINE':<12} ---", C.RED)
        cprint("\n  [ Resolucion DNS ]", C.YELLOW)
        for domain in ["google.com", "cloudflare.com", "github.com"]:
            dns   = Windows._ps(
                f"try{{(Resolve-DnsName {domain} -EA Stop | "
                f"Select-Object -First 1).IPAddress}}catch{{'FALLO'}}"
            )
            color = C.GREEN if dns.strip() != "FALLO" else C.RED
            cprint(f"  {domain:<25} {dns.strip()[:40]}", color)
        cprint("\n  [ Interfaces de Red ]", C.YELLOW)
        ifaces = Windows._ps(
            "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4'} | "
            "Select-Object InterfaceAlias,IPAddress,PrefixLength | "
            "Format-Table -AutoSize | Out-String"
        )
        print(ifaces)

    # ── 9: Escaneo de Red Local (con confirmación) ───────────
    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL [WINDOWS]")

        # ── MEJORA 2: Aviso de confirmación ──────────────────
        cprint("\n  ⚠  AVISO: El escaneo de red puede activar alertas en firewalls", C.YELLOW)
        cprint("     o sistemas de detección de intrusos (IDS/IPS) corporativos.", C.YELLOW)
        cprint("     Úsalo solo en redes de tu propiedad o con autorización expresa.", C.YELLOW)
        resp = input(f"\n  {C.CYAN}  Confirmar ejecución (S/N): {C.RESET}").strip().lower()
        if resp != "s":
            cprint("  Módulo cancelado.", C.GRAY)
            return

        local_ip = Windows._ps(
            "(Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and "
            "$_.IPAddress -notlike '169.*' -and $_.IPAddress -ne '127.0.0.1'} | "
            "Select-Object -First 1).IPAddress"
        ).strip()
        gateway = Windows._ps(
            "(Get-NetRoute | Where-Object {$_.DestinationPrefix -eq '0.0.0.0/0'} | "
            "Select-Object -First 1).NextHop"
        ).strip()
        if not local_ip:
            cprint("  No se detectó IP local. Verificar conexión.", C.RED)
            return
        parts  = local_ip.rsplit(".", 1)
        subnet = parts[0] + ".0/24" if len(parts) == 2 else "192.168.1.0/24"
        base   = parts[0] + "." if len(parts) == 2 else "192.168.1."
        print(f"\n  IP Local  : {C.CYAN}{local_ip}{C.RESET}")
        print(f"  Gateway   : {C.CYAN}{gateway}{C.RESET}")
        print(f"  Subred    : {C.CYAN}{subnet}{C.RESET}")
        if shutil.which("nmap"):
            cprint(f"\n  Escaneando {subnet} con nmap...", C.YELLOW)
            cprint(f"  {'IP':<20} {'ESTADO'}", C.YELLOW)
            cprint(f"  {'-'*35}", C.GRAY)
            raw        = run(f"nmap -sn {subnet}", timeout=60)
            current_ip = ""
            for line in raw.splitlines():
                ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if "Nmap scan report" in line and ip_match:
                    current_ip = ip_match.group(1)
                elif "Host is up" in line and current_ip:
                    marker = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if current_ip == local_ip else ""
                    cprint(f"  {current_ip:<20} ONLINE {marker}", C.GREEN)
                    current_ip = ""
        else:
            cprint(f"\n  Escaneando {subnet} (ping sweep, puede demorar)...", C.YELLOW)
            activos = 0
            for i in range(1, 255):
                ip     = f"{base}{i}"
                result = run(f"ping -n 1 -w 500 {ip}", timeout=3)
                if "TTL=" in result or "ttl=" in result:
                    marker = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if ip == local_ip else ""
                    cprint(f"  {ip:<20} ONLINE {marker}", C.GREEN)
                    activos += 1
            cprint(f"\n  Total dispositivos activos: {activos}", C.CYAN)
        cprint("\n  [ Tabla ARP - Dispositivos Recientes ]", C.YELLOW)
        arp = Windows._ps("arp -a | Out-String")
        print(arp)


# ════════════════════════════════════════════════════════════
#  MOTOR DE EXPORTACIÓN MULTI-FORMATO
# ════════════════════════════════════════════════════════════

def ensure_deps():
    import importlib
    ver = sys.version_info
    extra_paths = [
        f"/usr/local/lib/python{ver.major}.{ver.minor}/dist-packages",
        f"/usr/local/lib/python{ver.major}/dist-packages",
        f"/usr/lib/python{ver.major}.{ver.minor}/dist-packages",
        f"/usr/lib/python{ver.major}/dist-packages",
        f"/usr/lib/python3/dist-packages",
        f"/usr/local/lib/python3/dist-packages",
        os.path.expanduser(f"~/.local/lib/python{ver.major}.{ver.minor}/site-packages"),
        os.path.expanduser(f"~/.local/lib/python{ver.major}/site-packages"),
    ]
    for p in extra_paths:
        if os.path.exists(p) and p not in sys.path:
            sys.path.insert(0, p)
    importlib.invalidate_caches()
    deps = {"yaml": "pyyaml", "reportlab": "reportlab"}
    for mod, pkg in deps.items():
        try:
            __import__(mod)
            continue
        except ImportError:
            pass
        cprint(f"  Instalando {pkg}...", C.YELLOW)
        cmds = [
            [sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"],
            [sys.executable, "-m", "pip", "install", pkg],
            ["pip3", "install", pkg, "--break-system-packages"],
            [sys.executable, "-m", "pip", "install", pkg, "--user"],
        ]
        instalado = False
        for cmd in cmds:
            if not shutil.which(cmd[0]):
                continue
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                for p in extra_paths:
                    if os.path.exists(p) and p not in sys.path:
                        sys.path.insert(0, p)
                importlib.invalidate_caches()
                try:
                    __import__(mod)
                    instalado = True
                    cprint(f"  {pkg} instalado correctamente.", C.GREEN)
                    break
                except ImportError:
                    continue
        if not instalado:
            cprint(f"  No se pudo instalar {pkg} automaticamente.", C.RED)
            cprint(f"  Ejecuta: sudo pip install {pkg} --break-system-packages", C.CYAN)


def collect_report_data():
    cprint("  Recopilando datos del sistema...", C.GRAY)
    now  = datetime.datetime.now()
    data = {
        "meta": {
            "herramienta": SYSTEM_NAME, "version": VERSION, "autor": DEVELOPER,
            "sistema": SO, "plataforma": platform.platform(),
            "fecha": now.strftime("%Y-%m-%d"), "hora": now.strftime("%H:%M:%S"),
            "timestamp": now.isoformat(),
        },
        "hardware": {}, "discos": [], "usuarios": [],
        "puertos": [], "software": [], "eventos": [],
    }

    if SO == "Linux":
        data["hardware"] = {
            "cpu":    run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(),
            "serial": run("sudo dmidecode -s system-serial-number 2>/dev/null").strip() or "N/A",
            "ram":    run("free -h | grep Mem | awk '{print $3\"/\"$2}'"),
            "uptime": run("uptime -p"),
            "kernel": run("uname -r"),
            "distro": run("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'"),
        }
        s_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|temp1|Core 0):\s+[+\-]?(\d+\.\d+)", s_out)
        data["hardware"]["temperatura_cpu"] = f"{m.group(1)}°C" if m else "N/A"
        for line in run("df -h | grep '^/dev'").splitlines():
            parts = line.split()
            if len(parts) >= 6:
                data["discos"].append({
                    "dispositivo": parts[0], "tamanio": parts[1],
                    "usado": parts[2], "libre": parts[3],
                    "uso_pct": parts[4], "montaje": parts[5]
                })
        for line in run("cat /etc/passwd | grep -E '/bin/bash|/bin/sh'").splitlines():
            p = line.split(":")
            if len(p) >= 7:
                data["usuarios"].append({"usuario": p[0], "uid": p[2], "gid": p[3], "home": p[5], "shell": p[6]})
        for line in run("sudo ss -tunlp | grep LISTEN").splitlines():
            data["puertos"].append({"entrada": html_escape(line.strip())})
        pkg_mgr = "APT" if shutil.which("apt") else "DNF" if shutil.which("dnf") else "PACMAN"
        if pkg_mgr == "APT":   raw = run("dpkg -l | grep '^ii' | awk '{print $2\"|\"$3\"|\"$4}'")
        elif pkg_mgr == "DNF": raw = run("rpm -qa --qf '%{NAME}|%{VERSION}|%{VENDOR}\n'")
        else:                  raw = run("pacman -Q | awk '{print $1\"|\"$2\"|---\"}'")
        for line in raw.splitlines()[:200]:
            p = (line + "||").split("|")
            data["software"].append({"nombre": p[0], "version": p[1], "origen": p[2]})
        for line in run("sudo journalctl -p err -n 30 --no-pager --output=short 2>/dev/null").splitlines():
            if line.strip():
                data["eventos"].append({"entrada": html_escape(line.strip())})
    else:
        def ps(cmd): return Windows._ps(cmd)
        data["hardware"] = {
            "cpu":    ps("(Get-CimInstance Win32_Processor).Name.Trim()"),
            "serial": ps("(Get-CimInstance Win32_BIOS).SerialNumber.Trim()"),
            "ram":    ps("$r=Get-CimInstance Win32_OperatingSystem;[math]::Round(($r.TotalVisibleMemorySize-$r.FreePhysicalMemory)/1MB,2).ToString()+' / '+[math]::Round($r.TotalVisibleMemorySize/1MB,2).ToString()+' GB'"),
            "uptime": ps("$r=Get-CimInstance Win32_OperatingSystem;$u=(Get-Date)-$r.LastBootUpTime;'{0}d {1}h {2}m' -f $u.Days,$u.Hours,$u.Minutes"),
            "os":     ps("(Get-CimInstance Win32_OperatingSystem).Caption"),
            "temperatura_cpu": "Ver OpenHardwareMonitor",
        }
        disk_json = ps("Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | Select-Object Name,@{N='Usado';E={[math]::Round($_.Used/1GB,2)}},@{N='Libre';E={[math]::Round($_.Free/1GB,2)}},@{N='Total';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}},@{N='Pct';E={[math]::Round($_.Used/($_.Used+$_.Free)*100,1)}} | ConvertTo-Json")
        try:
            dl = json.loads(disk_json)
            if isinstance(dl, dict): dl = [dl]
            for d in dl:
                data["discos"].append({"unidad": d.get("Name",""), "usado_gb": d.get("Usado",""), "libre_gb": d.get("Libre",""), "total_gb": d.get("Total",""), "uso_pct": f"{d.get('Pct','')}%"})
        except Exception: pass
        user_json = ps("Get-LocalUser | Select-Object Name,Enabled,LastLogon | ConvertTo-Json")
        try:
            ul = json.loads(user_json)
            if isinstance(ul, dict): ul = [ul]
            for u in ul:
                data["usuarios"].append({"usuario": u.get("Name",""), "activo": str(u.get("Enabled","")), "ultimo_login": str(u.get("LastLogon",""))})
        except Exception: pass
        port_json = ps("Get-NetTCPConnection -State Listen -EA SilentlyContinue | Select-Object LocalAddress,LocalPort,@{N='Proceso';E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).Name}} | ConvertTo-Json")
        try:
            pl = json.loads(port_json)
            if isinstance(pl, dict): pl = [pl]
            for p in pl:
                data["puertos"].append({"direccion": p.get("LocalAddress",""), "puerto": p.get("LocalPort",""), "proceso": p.get("Proceso","")})
        except Exception: pass
        sw_json = ps("$paths=@('HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*','HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*');$paths | ForEach-Object {Get-ItemProperty $_ -EA SilentlyContinue} | Where-Object {$_.DisplayName} | Sort-Object DisplayName | Select-Object -First 200 DisplayName,DisplayVersion,Publisher | ConvertTo-Json")
        try:
            sl = json.loads(sw_json)
            if isinstance(sl, dict): sl = [sl]
            for s in sl:
                data["software"].append({"nombre": s.get("DisplayName",""), "version": s.get("DisplayVersion",""), "origen": s.get("Publisher","")})
        except Exception: pass
        ev_raw = ps("try{Get-WinEvent -FilterHashtable @{LogName='System';Level=@(1,2);StartTime=(Get-Date).AddDays(-1)} -MaxEvents 30 -EA Stop | Select-Object TimeCreated,Id,Message | ConvertTo-Json}catch{'[]'}")
        try:
            el = json.loads(ev_raw)
            if isinstance(el, dict): el = [el]
            for e in el:
                msg = str(e.get("Message","")).split("\n")[0][:120]
                data["eventos"].append({"fecha": str(e.get("TimeCreated","")), "id": str(e.get("Id","")), "msg": msg})
        except Exception: pass

    cprint(f"  Datos: hardware, {len(data['discos'])} discos, {len(data['usuarios'])} usuarios, "
           f"{len(data['puertos'])} puertos, {len(data['software'])} programas, {len(data['eventos'])} eventos.", C.GREEN)
    return data


def export_json(data, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

def export_yaml(data, path):
    import yaml
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def export_xml(data, path):
    import xml.etree.ElementTree as ET
    def dict_to_xml(parent, d):
        if isinstance(d, dict):
            for k, v in d.items():
                tag   = re.sub(r'[^a-zA-Z0-9_]', '_', str(k))
                child = ET.SubElement(parent, tag)
                dict_to_xml(child, v)
        elif isinstance(d, list):
            for item in d:
                child = ET.SubElement(parent, "item")
                dict_to_xml(child, item)
        else:
            parent.text = str(d) if d is not None else ""
    root = ET.Element("NEUROAUDIT_Report")
    dict_to_xml(root, data)
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="unicode", xml_declaration=True)

def export_csv(data, base_path):
    import csv
    archivos  = []
    secciones = {
        "hardware": [data["hardware"]], "discos": data["discos"],
        "usuarios": data["usuarios"],   "puertos": data["puertos"],
        "software": data["software"],   "eventos": data["eventos"],
    }
    for nombre, filas in secciones.items():
        if not filas: continue
        # Fix: usar rsplit para evitar reemplazos incorrectos en el path
        filepath = base_path.rsplit(".csv", 1)[0] + f"_{nombre}.csv"
        keys = list(filas[0].keys()) if filas else []
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filas)
        archivos.append(filepath)
    return archivos

def export_pdf(data, path):
    import sys as _sys, os as _os
    _script_dir = _os.path.dirname(_os.path.abspath(__file__))
    _venv_site  = _os.path.join(_script_dir, ".venv", "lib")
    if _os.path.exists(_venv_site):
        for _d in _os.listdir(_venv_site):
            _sp = _os.path.join(_venv_site, _d, "site-packages")
            if _os.path.exists(_sp) and _sp not in _sys.path:
                _sys.path.insert(0, _sp)
    for _mod in list(_sys.modules.keys()):
        if _mod == "PIL" or _mod.startswith("PIL."): del _sys.modules[_mod]

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable, PageBreak)

    doc    = SimpleDocTemplate(path, pagesize=A4,
                               leftMargin=2*cm, rightMargin=2*cm,
                               topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    titulo_style = ParagraphStyle("titulo", fontSize=36, textColor=colors.HexColor("#00ff88"),
        spaceBefore=30, spaceAfter=8, fontName="Helvetica-Bold", alignment=1, leading=42)
    sub_style    = ParagraphStyle("sub", fontSize=11, textColor=colors.HexColor("#58a6ff"),
        spaceBefore=6, spaceAfter=16, alignment=1, leading=16)
    autor_style  = ParagraphStyle("autor", fontSize=9, textColor=colors.HexColor("#8b949e"),
        spaceAfter=20, alignment=1)
    h2_style     = ParagraphStyle("h2", fontSize=12, textColor=colors.HexColor("#00ff88"),
        spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold", leading=16)

    COLOR_BG      = colors.HexColor("#0d1117")
    COLOR_HEADER  = colors.HexColor("#161b22")
    COLOR_BORDER  = colors.HexColor("#30363d")
    COLOR_TH      = colors.HexColor("#58a6ff")
    COLOR_TEXT    = colors.HexColor("#c9d1d9")
    COLOR_ROW_ALT = colors.HexColor("#1c2128")

    def make_table(headers, rows, col_widths=None):
        th_row = [Paragraph(f"<b>{h}</b>", ParagraphStyle("th",
                    fontSize=8, textColor=COLOR_TH, fontName="Helvetica-Bold")) for h in headers]
        table_data = [th_row]
        for row in rows:
            table_data.append([
                Paragraph(str(cell)[:120], ParagraphStyle("td",
                    fontSize=7.5, textColor=COLOR_TEXT, fontName="Helvetica"))
                for cell in row
            ])
        if col_widths is None:
            avail = 17*cm
            col_widths = [avail / len(headers)] * len(headers)
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND",     (0,0), (-1,0),  COLOR_HEADER),
            ("BACKGROUND",     (0,1), (-1,-1), COLOR_BG),
            ("GRID",           (0,0), (-1,-1), 0.4, COLOR_BORDER),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [COLOR_BG, COLOR_ROW_ALT]),
            ("TOPPADDING",     (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",  (0,0), (-1,-1), 4),
            ("LEFTPADDING",    (0,0), (-1,-1), 6),
        ]))
        return t

    story = []
    story.append(Spacer(1, 3.5*cm))
    story.append(HRFlowable(width="80%", color=colors.HexColor("#00ff88"), thickness=2, hAlign="CENTER", spaceAfter=20))
    story.append(Paragraph("NEUROAUDIT", titulo_style))
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(f"System Audit Report &nbsp;&nbsp;|&nbsp;&nbsp; v{VERSION} &nbsp;&nbsp;|&nbsp;&nbsp; {data['meta']['sistema']}", sub_style))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(f"{data['meta']['fecha']} &nbsp;&nbsp;{data['meta']['hora']} &nbsp;&nbsp;|&nbsp;&nbsp; {data['meta']['autor']}", autor_style))
    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="80%", color=colors.HexColor("#00ff88"), thickness=2, hAlign="CENTER", spaceAfter=30))
    story.append(Spacer(1, 0.6*cm))
    meta_rows = [[k.replace("_"," ").title(), str(v)] for k, v in data["meta"].items()]
    story.append(make_table(["Campo", "Valor"], meta_rows, [5*cm, 12*cm]))
    story.append(PageBreak())

    story.append(Paragraph("Hardware e Infraestructura", h2_style))
    hw_rows = [[k.replace("_"," ").title(), str(v)] for k, v in data["hardware"].items()]
    story.append(make_table(["Componente", "Valor"], hw_rows, [5*cm, 12*cm]))
    story.append(Spacer(1, 0.4*cm))

    if data["discos"]:
        story.append(Paragraph("Discos y Particiones", h2_style))
        keys = list(data["discos"][0].keys())
        story.append(make_table([k.replace("_"," ").title() for k in keys],
                                [[str(d.get(k,"")) for k in keys] for d in data["discos"]]))
        story.append(Spacer(1, 0.4*cm))

    if data["usuarios"]:
        story.append(Paragraph("Usuarios del Sistema", h2_style))
        keys = list(data["usuarios"][0].keys())
        story.append(make_table([k.replace("_"," ").title() for k in keys],
                                [[str(u.get(k,"")) for k in keys] for u in data["usuarios"]]))
        story.append(Spacer(1, 0.4*cm))

    if data["puertos"]:
        story.append(Paragraph("Puertos y Conexiones", h2_style))
        keys = list(data["puertos"][0].keys())
        story.append(make_table([k.replace("_"," ").title() for k in keys],
                                [[str(p.get(k,"")) for k in keys] for p in data["puertos"]]))
        story.append(PageBreak())

    if data["software"]:
        story.append(Paragraph(f"Software Instalado ({len(data['software'])} programas)", h2_style))
        keys = list(data["software"][0].keys())
        story.append(make_table([k.replace("_"," ").title() for k in keys],
                                [[str(s.get(k,""))[:80] for k in keys] for s in data["software"][:150]]))
        story.append(PageBreak())

    if data["eventos"]:
        story.append(Paragraph("Eventos del Sistema", h2_style))
        keys = list(data["eventos"][0].keys())
        story.append(make_table([k.replace("_"," ").title() for k in keys],
                                [[str(e.get(k,""))[:100] for k in keys] for e in data["eventos"]]))

    def add_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColorRGB(0.28, 0.31, 0.34)
        footer_txt = (f"NEUROAUDIT v{VERSION}  |  {DEVELOPER}  |  "
                      f"Generado: {data['meta']['fecha']} {data['meta']['hora']}  |  Pagina {doc_obj.page}")
        canvas_obj.drawCentredString(A4[0]/2, 1.2*cm, footer_txt)
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

def export_html_full(data, path):
    def rows_html(items, keys=None):
        if not items: return "<tr><td colspan='10'>Sin datos.</td></tr>"
        if keys is None: keys = list(items[0].keys())
        out = ""
        for item in items:
            out += "<tr>" + "".join(f"<td>{html_escape(str(item.get(k,'')))}</td>" for k in keys) + "</tr>"
        return out
    def thead(items, keys=None):
        if not items: return ""
        if keys is None: keys = list(items[0].keys())
        return "<tr>" + "".join(f"<th>{k.replace('_',' ').title()}</th>" for k in keys) + "</tr>"

    hw       = data["hardware"]
    hw_cards = "".join(
        f'<div class="info-item"><div class="label">{k.replace("_"," ").upper()}</div>'
        f'<div class="value">{html_escape(str(v))}</div></div>'
        for k, v in hw.items()
    )
    html = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8">
<title>NEUROAUDIT Report - {data['meta']['fecha']}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0d1117;color:#c9d1d9;font-family:Consolas,monospace;padding:24px}}
h1{{color:#00ff88;text-align:center;font-size:2.2em;letter-spacing:5px;padding:24px 0 6px}}
.subtitle{{text-align:center;color:#58a6ff;margin-bottom:24px;font-size:.9em}}
.badge{{display:inline-block;background:#161b22;border:1px solid #30363d;border-radius:6px;padding:4px 14px;margin:4px;font-size:.8em;color:#8b949e}}
.card{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:22px;margin:22px 0}}
.card h2{{color:#00ff88;border-bottom:1px solid #30363d;padding-bottom:8px;margin-bottom:16px;font-size:1em;letter-spacing:2px}}
table{{width:100%;border-collapse:collapse;font-size:.82em}}
th{{background:#21262d;color:#58a6ff;padding:9px;text-align:left;border-bottom:2px solid #30363d}}
td{{padding:6px 9px;border-bottom:1px solid #21262d;word-break:break-word}}
tr:nth-child(even) td{{background:#1c2128}}
tr:hover td{{background:#21262d}}
.info-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
.info-item{{background:#21262d;border-radius:8px;padding:14px}}
.info-item .label{{color:#8b949e;font-size:.72em;text-transform:uppercase;letter-spacing:1px}}
.info-item .value{{color:#e6edf3;font-size:.92em;margin-top:5px}}
.footer{{text-align:center;color:#484f58;font-size:.75em;margin-top:32px;padding-top:16px;border-top:1px solid #21262d}}
</style></head><body>
<h1>NEUROAUDIT</h1>
<div class="subtitle">System Audit Report &nbsp;|&nbsp; v{VERSION} &nbsp;|&nbsp; {data['meta']['sistema'].upper()} &nbsp;|&nbsp; {data['meta']['fecha']} {data['meta']['hora']}</div>
<div style="text-align:center;margin-bottom:22px">
  <span class="badge">Plataforma: {html_escape(data['meta']['plataforma'])}</span>
  <span class="badge">Autor: {DEVELOPER}</span>
</div>
<div class="card"><h2>HARDWARE E INFRAESTRUCTURA</h2><div class="info-grid">{hw_cards}</div></div>
<div class="card"><h2>DISCOS Y PARTICIONES ({len(data['discos'])} unidades)</h2><table><thead>{thead(data['discos'])}</thead><tbody>{rows_html(data['discos'])}</tbody></table></div>
<div class="card"><h2>USUARIOS DEL SISTEMA ({len(data['usuarios'])} usuarios)</h2><table><thead>{thead(data['usuarios'])}</thead><tbody>{rows_html(data['usuarios'])}</tbody></table></div>
<div class="card"><h2>PUERTOS EN ESCUCHA ({len(data['puertos'])} puertos)</h2><table><thead>{thead(data['puertos'])}</thead><tbody>{rows_html(data['puertos'])}</tbody></table></div>
<div class="card"><h2>SOFTWARE INSTALADO ({len(data['software'])} programas)</h2><table><thead>{thead(data['software'])}</thead><tbody>{rows_html(data['software'])}</tbody></table></div>
<div class="card"><h2>EVENTOS DEL SISTEMA ({len(data['eventos'])} eventos)</h2><table><thead>{thead(data['eventos'])}</thead><tbody>{rows_html(data['eventos'])}</tbody></table></div>
<div class="footer">NEUROAUDIT v{VERSION} &nbsp;|&nbsp; {DEVELOPER} &nbsp;|&nbsp; Generado: {data['meta']['fecha']} {data['meta']['hora']}</div>
</body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def run_export():
    section("EXPORTAR REPORTE - SELECCIONAR FORMATO")
    formatos = {
        "1": ("JSON",  ".json"),
        "2": ("YAML",  ".yaml"),
        "3": ("XML",   ".xml"),
        "4": ("CSV",   ".csv (multiples archivos por seccion)"),
        "5": ("PDF",   ".pdf"),
        "6": ("HTML",  ".html"),
        "7": ("TODOS", "todos los formatos"),
    }
    print()
    for k, (nombre, ext) in formatos.items():
        cprint(f"  [{k}]  {nombre:<6} — {ext}", C.RESET)
    print()
    opcion = input(f"  {C.CYAN}Seleccione formato: {C.RESET}").strip()
    if opcion not in formatos:
        cprint("  Opcion no valida.", C.YELLOW)
        return
    ensure_deps()
    data   = collect_report_data()
    now    = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    so_tag = "linux" if SO == "Linux" else "windows"
    if SO == "Windows":
        default_dir = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop", "NEUROAUDIT_Reportes")
    else:
        default_dir = os.path.join(_get_real_home(), "NEUROAUDIT_Reportes")
    cprint(f"\n  Carpeta de destino: {C.CYAN}{default_dir}{C.RESET}")
    resp = input(f"  {C.CYAN}Usar esta carpeta? (S/N): {C.RESET}").strip().lower()
    if resp == "n":
        nueva = input(f"  {C.CYAN}Ingresa la ruta completa: {C.RESET}").strip()
        rep_dir = nueva if (nueva and os.path.isabs(nueva)) else default_dir
    else:
        rep_dir = default_dir
    try:
        os.makedirs(rep_dir, exist_ok=True)
    except Exception as e:
        cprint(f"  Error creando carpeta: {e}", C.RED)
        rep_dir = os.path.expanduser("~")
    base      = os.path.join(rep_dir, f"reporte_{so_tag}_{now}")
    seleccion = list(formatos.keys())[:-1] if opcion == "7" else [opcion]
    generados = []
    for sel in seleccion:
        nombre = formatos[sel][0]
        cprint(f"\n  Generando {nombre}...", C.YELLOW)
        try:
            if sel == "1":   p = base+".json";  export_json(data, p);      generados.append(p)
            elif sel == "2": p = base+".yaml";  export_yaml(data, p);      generados.append(p)
            elif sel == "3": p = base+".xml";   export_xml(data, p);       generados.append(p)
            elif sel == "4": ps = export_csv(data, base+".csv");           generados.extend(ps)
            elif sel == "5": p = base+".pdf";   export_pdf(data, p);       generados.append(p)
            elif sel == "6": p = base+".html";  export_html_full(data, p); generados.append(p)
            cprint(f"  {nombre} OK", C.GREEN)
        except Exception as e:
            cprint(f"  Error generando {nombre}: {e}", C.RED)
    print()
    cprint("  ─── Archivos generados ───────────────────────────────", C.CYAN)
    for g in generados:
        cprint(f"  ✓  {g}", C.GREEN)
    if not generados:
        cprint("  No se genero ningun archivo.", C.RED)
    try:
        if SO == "Windows":
            os.startfile(rep_dir)
        else:
            sudo_user = os.environ.get("SUDO_USER")
            if sudo_user and sudo_user != "root":
                subprocess.Popen(["sudo", "-u", sudo_user, "xdg-open", rep_dir],
                                 env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":0"),
                                      "DBUS_SESSION_BUS_ADDRESS": os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")})
            else:
                subprocess.Popen(["xdg-open", rep_dir])
    except Exception:
        pass


# ════════════════════════════════════════════════════════════
#  MÓDULO 10: AUDITORÍA DE PERMISOS Y USUARIOS
# ════════════════════════════════════════════════════════════

def perm_alert(msg): cprint(f"  ⚠  RIESGO  : {msg}", C.RED)
def perm_ok(msg):    cprint(f"  OK         : {msg}", C.GREEN)
def perm_info(msg):  cprint(f"  INFO       : {msg}", C.YELLOW)

def audit_permissions_linux():
    section("AUDITORIA DE PERMISOS Y USUARIOS [LINUX]")
    cprint("\n  [ Usuario Actual ]", C.YELLOW)
    whoami  = run("whoami").strip()
    uid     = run("id -u").strip()
    groups  = run("id -Gn").strip()
    is_root = (uid == "0")
    print(f"  Usuario  : {C.CYAN}{whoami}{C.RESET}")
    print(f"  UID      : {uid}")
    print(f"  Grupos   : {groups}")
    if is_root: perm_alert("Corriendo como ROOT. Evitar uso cotidiano con root.")
    else:       perm_ok("No es root — usuario con privilegios normales.")
    if "sudo" in groups or "wheel" in groups:
        perm_alert(f"{whoami} tiene acceso SUDO — puede escalar privilegios.")
    else:
        perm_ok(f"{whoami} no tiene acceso sudo directo.")

    cprint("\n  [ Usuarios con Privilegios Elevados ]", C.YELLOW)
    for grp in ["sudo", "wheel", "admin"]:
        members = run(f"getent group {grp} 2>/dev/null | cut -d: -f4").strip()
        if members:
            cprint(f"  Grupo {grp:<8}: {members}", C.RESET)
            count = len([m for m in members.split(",") if m.strip()])
            if count > 2: perm_alert(f"El grupo '{grp}' tiene {count} miembros. Revisar.")
        else:
            cprint(f"  Grupo {grp:<8}: (vacio o no existe)", C.GRAY)
    uid0 = run("awk -F: '$3==0{print $1}' /etc/passwd").strip()
    if uid0:
        users_uid0 = [u for u in uid0.splitlines() if u.strip()]
        if len(users_uid0) > 1: perm_alert(f"Multiples usuarios con UID 0: {', '.join(users_uid0)}")
        else: perm_ok(f"Solo un usuario con UID 0: {users_uid0[0]}")

    cprint("\n  [ Listado de Usuarios del Sistema ]", C.YELLOW)
    cprint(f"  {'USUARIO':<20} {'UID':<8} {'GID':<8} {'SHELL':<20} {'HOME'}", C.CYAN)
    cprint(f"  {'-'*75}", C.GRAY)
    for line in run("getent passwd | sort -t: -k3 -n").splitlines():
        p = line.split(":")
        if len(p) < 7: continue
        user, uid_v, gid, home, shell = p[0], p[2], p[3], p[5], p[6].strip()
        uid_int = int(uid_v) if uid_v.isdigit() else 9999
        if uid_int == 0 or uid_int >= 1000:
            color = C.GREEN if uid_int >= 1000 else C.RED
            cprint(f"  {user:<20} {uid_v:<8} {gid:<8} {shell:<20} {home}", color)
            if shell in ["/bin/bash", "/bin/sh", "/bin/zsh"] and uid_int > 0:
                grps = run(f"groups {user} 2>/dev/null").replace(f"{user} : ", "")
                if "sudo" in grps or "wheel" in grps:
                    perm_alert(f"'{user}' tiene shell interactiva Y permisos sudo.")

    cprint("\n  [ Permisos en Carpetas Criticas ]", C.YELLOW)
    cprint(f"  {'RUTA':<35} {'PERMISOS':<12} {'PROPIETARIO':<15} {'ESTADO'}", C.CYAN)
    cprint(f"  {'-'*75}", C.GRAY)
    rutas_criticas = [
        ("/etc/passwd",          "644",  False),
        ("/etc/shadow",          "640",  False),
        ("/etc/sudoers",         "440",  False),
        ("/etc/ssh/sshd_config", "600",  False),
        ("/tmp",                 "1777", True),
        ("/var/log",             "755",  True),
        ("/root",                "700",  True),
        ("/home",                "755",  True),
        ("/etc/cron.d",          "755",  True),
        ("/usr/bin/passwd",      "4755", False),
    ]
    for ruta, perm_esperado, _ in rutas_criticas:
        if not os.path.exists(ruta):
            cprint(f"  {ruta:<35} {'N/A':<12} {'---':<15} No existe", C.GRAY)
            continue
        stat_out = run(f"stat -c '%a %U %G' {ruta} 2>/dev/null").strip().split()
        if len(stat_out) >= 3:
            perm_real, owner, group = stat_out[0], stat_out[1], stat_out[2]
            propietario = f"{owner}:{group}"
            if perm_real == perm_esperado:
                print(f"  {ruta:<35} {perm_real:<12} {propietario:<15} ", end="")
                cprint("OK", C.GREEN)
            else:
                print(f"  {ruta:<35} {perm_real:<12} {propietario:<15} ", end="")
                cprint(f"REVISAR (esperado: {perm_esperado})", C.RED)
                if ruta in ["/etc/shadow", "/etc/sudoers"]:
                    perm_alert(f"{ruta} tiene permisos incorrectos — riesgo alto.")

    cprint("\n  [ Archivos SUID/SGID (fuera de /usr y /bin) ]", C.YELLOW)
    suid = run("find / -perm /6000 -type f 2>/dev/null | grep -Ev '^/usr|^/bin|^/sbin|^/lib' | head -20")
    if suid.strip():
        for line in suid.splitlines(): perm_alert(f"SUID/SGID inusual: {line.strip()}")
    else:
        perm_ok("No se encontraron archivos SUID/SGID fuera de rutas estandar.")

    cprint("\n  [ Politica de Contrasenas ]", C.YELLOW)
    for campo, etiqueta in [("PASS_MAX_DAYS","Max dias"), ("PASS_MIN_DAYS","Min dias"),
                             ("PASS_MIN_LEN","Min largo"), ("PASS_WARN_AGE","Aviso dias")]:
        val = run(f"grep '^{campo}' /etc/login.defs 2>/dev/null | awk '{{print $2}}'").strip()
        print(f"  {etiqueta:<20}: {val or 'No definido'}")
    try:
        pass_max = int(run("grep '^PASS_MAX_DAYS' /etc/login.defs 2>/dev/null | awk '{print $2}'").strip() or 99999)
        pass_len = int(run("grep '^PASS_MIN_LEN'  /etc/login.defs 2>/dev/null | awk '{print $2}'").strip() or 0)
        if pass_max > 90: perm_alert("PASS_MAX_DAYS > 90 dias. Se recomienda maximo 90.")
        else: perm_ok(f"PASS_MAX_DAYS = {pass_max} dias (correcto).")
        if pass_len < 8: perm_alert("PASS_MIN_LEN < 8. Se recomienda minimo 8 caracteres.")
        else: perm_ok(f"PASS_MIN_LEN = {pass_len} (correcto).")
    except ValueError: pass

    cprint("\n  [ Usuarios sin Contrasena ]", C.YELLOW)
    no_pass = run("sudo awk -F: '($2==\"\" || $2==\"!\"){print $1}' /etc/shadow 2>/dev/null")
    if no_pass.strip():
        for u in no_pass.splitlines(): perm_alert(f"Usuario sin contrasena: {u.strip()}")
    else:
        perm_ok("Todos los usuarios tienen contrasena configurada.")

    cprint("\n  [ Limpiador de Temporales ]", C.YELLOW)
    total_size = 0
    for p in ["/tmp", "/var/tmp"]:
        if os.path.exists(p):
            size_raw = run(f"du -sb {p} 2>/dev/null | cut -f1").strip()
            try:
                size = int(size_raw); total_size += size; size_mb = size / 1024 / 1024
                color = C.RED if size_mb > 500 else C.YELLOW if size_mb > 100 else C.GREEN
                cprint(f"  {p:<20} {size_mb:.1f} MB", color)
                if size_mb > 500: perm_alert(f"{p} supera 500 MB — considerar limpieza.")
            except ValueError: pass
    total_mb = total_size / 1024 / 1024
    print(f"\n  Total temporales: {C.CYAN}{total_mb:.1f} MB{C.RESET}")
    if total_mb > 100:
        resp = input(f"\n  {C.CYAN}Limpiar temporales de mas de 2 dias? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            for p in ["/tmp", "/var/tmp"]:
                os.system(f"find {p} -type f -atime +2 -delete 2>/dev/null")
                os.system(f"find {p} -type d -empty -delete 2>/dev/null")
            perm_ok("Temporales limpiados correctamente.")
    else:
        perm_ok("Temporales dentro de limites normales.")


def audit_permissions_windows():
    section("AUDITORIA DE PERMISOS Y USUARIOS [WINDOWS]")
    def ps(cmd): return Windows._ps(cmd)

    cprint("\n  [ Usuario Actual ]", C.YELLOW)
    whoami   = run("whoami").strip()
    is_admin = check_privileges()
    print(f"  Usuario  : {C.CYAN}{whoami}{C.RESET}")
    if is_admin: perm_alert("Corriendo como Administrador. Usar cuenta estandar para tareas cotidianas.")
    else:        perm_ok("Usuario estandar — sin privilegios elevados activos.")

    cprint("\n  [ Usuarios Locales ]", C.YELLOW)
    users = ps("Get-LocalUser | Select-Object Name,Enabled,LastLogon,PasswordLastSet,PasswordNeverExpires,PasswordRequired | Format-Table -AutoSize | Out-String")
    print(users)
    never_exp = ps("Get-LocalUser | Where-Object {$_.PasswordNeverExpires -eq $true -and $_.Enabled} | Select-Object -ExpandProperty Name")
    if never_exp.strip():
        for u in never_exp.strip().splitlines():
            if u.strip(): perm_alert(f"'{u.strip()}' tiene contrasena que NUNCA expira.")
    else:
        perm_ok("Ningun usuario activo con contrasena que nunca expira.")

    cprint("\n  [ Miembros del Grupo Administradores ]", C.YELLOW)
    admins = ps("Get-LocalGroupMember -Group 'Administrators' -EA SilentlyContinue | Select-Object Name,PrincipalSource | Format-Table -AutoSize | Out-String")
    print(admins)
    admin_count = len([l for l in admins.splitlines() if l.strip() and "---" not in l and "Name" not in l])
    if admin_count > 2: perm_alert(f"Hay {admin_count} administradores locales. Revisar si todos son necesarios.")
    else: perm_ok(f"Cantidad de administradores: {admin_count} (aceptable).")

    cprint("\n  [ Politica de Contrasenas ]", C.YELLOW)
    policy = ps("net accounts 2>&1 | Out-String")
    print(policy)
    max_age = re.search(r"Maximum password age.*?(\d+)", policy)
    min_len = re.search(r"Minimum password length.*?(\d+)", policy)
    if max_age:
        days = int(max_age.group(1))
        if days > 90 or days == 0: perm_alert(f"Contrasena maxima: {days} dias. Recomendado: 90 o menos.")
        else: perm_ok(f"Expiracion: {days} dias (correcto).")
    if min_len:
        length = int(min_len.group(1))
        if length < 8: perm_alert(f"Longitud minima: {length}. Recomendado: 8 o mas.")
        else: perm_ok(f"Longitud minima: {length} caracteres (correcto).")

    cprint("\n  [ Limpiador de Temporales ]", C.YELLOW)
    temp_paths = [
        os.environ.get("TEMP", ""),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp"),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Prefetch"),
    ]
    total = 0
    for p in temp_paths:
        if p and os.path.exists(p):
            size = sum(os.path.getsize(os.path.join(dp, f))
                       for dp, _, files in os.walk(p)
                       for f in files if os.path.exists(os.path.join(dp, f)))
            total += size
            size_mb = size / 1024 / 1024
            color = C.RED if size_mb > 500 else C.YELLOW if size_mb > 100 else C.GREEN
            cprint(f"  {p:<50} {size_mb:.1f} MB", color)
    total_mb = total / 1024 / 1024
    print(f"\n  Total temporales: {C.CYAN}{total_mb:.1f} MB{C.RESET}")
    if total_mb > 100:
        resp = input(f"\n  {C.CYAN}Limpiar temporales ahora? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            limpiado = 0
            for p in temp_paths:
                if p and os.path.exists(p):
                    for dp, dirs, files in os.walk(p):
                        for f in files:
                            try:
                                fp = os.path.join(dp, f)
                                limpiado += os.path.getsize(fp)
                                os.remove(fp)
                            except Exception: pass
            perm_ok(f"Limpiados {limpiado/1024/1024:.1f} MB de temporales.")
    else:
        perm_ok("Temporales dentro de limites normales.")

def run_permission_audit():
    if SO == "Linux": audit_permissions_linux()
    else:             audit_permissions_windows()


# ════════════════════════════════════════════════════════════
#  DIAGNÓSTICO DE PASTA TÉRMICA
# ════════════════════════════════════════════════════════════

def analizar_pasta_termica(temp_cpu, temp_gpu, uptime_segundos, es_notebook):
    section("DIAGNOSTICO DE PASTA TERMICA")
    tipo = "NOTEBOOK" if es_notebook else "DESKTOP"
    cprint(f"  Tipo de equipo : {C.CYAN}{tipo}{C.RESET}")
    umbral_ok = 75 if es_notebook else 70
    umbral_alt = 85 if es_notebook else 80
    umbral_crit = 95 if es_notebook else 90

    cprint("\n  Temperatura CPU:", C.GRAY)
    if temp_cpu is not None:
        if temp_cpu < umbral_ok:         cprint(f"  {temp_cpu}°C   NORMAL — pasta termica en buen estado", C.GREEN)
        elif temp_cpu < umbral_alt:      cprint(f"  {temp_cpu}°C   ELEVADA — monitorear, limpiar ventiladores", C.YELLOW)
        elif temp_cpu < umbral_crit:     cprint(f"  {temp_cpu}°C   ALTA — se recomienda cambio de pasta termica", C.RED)
        else:                            cprint(f"  {temp_cpu}°C   CRITICA — cambio de pasta URGENTE ⚠", C.RED)
    else:
        cprint("  No se pudo leer la temperatura CPU.", C.YELLOW)

    cprint("\n  Temperatura GPU:", C.GRAY)
    if temp_gpu is not None:
        gpu_ok  = 80 if es_notebook else 75
        gpu_alt = 90 if es_notebook else 85
        if temp_gpu < gpu_ok:  cprint(f"  {temp_gpu}°C   NORMAL", C.GREEN)
        elif temp_gpu < gpu_alt: cprint(f"  {temp_gpu}°C   ELEVADA — verificar ventilacion", C.YELLOW)
        else:                   cprint(f"  {temp_gpu}°C   ALTA — revisar pasta termica GPU", C.RED)
    else:
        cprint("  No se pudo leer la temperatura GPU.", C.YELLOW)

    cprint("\n  Tiempo de uso en esta sesion:", C.GRAY)
    if uptime_segundos:
        horas = uptime_segundos // 3600
        mins  = (uptime_segundos % 3600) // 60
        cprint(f"  {horas}h {mins}m", C.CYAN)
        if temp_cpu and horas >= 2 and temp_cpu > umbral_alt:
            cprint("  Temperatura alta despues de 2+ horas — problema de disipacion.", C.RED)

    cprint("\n  Historial de temperatura CPU (3 lecturas / 5 seg):", C.GRAY)
    lecturas = []
    for i in range(3):
        if SO == "Linux":
            s_out = run("sensors 2>/dev/null")
            m     = re.search(r"(?:Package id 0|temp1|Core 0|temp2):\s+[+\-]?(\d+\.\d+)", s_out)
            t     = float(m.group(1)) if m else None
        else:
            t_raw = Windows._ps(
                "try { $t=Get-CimInstance -Namespace 'root/OpenHardwareMonitor' "
                "-ClassName Sensor -Filter \"SensorType='Temperature' AND Name LIKE '%CPU%'\""
                " -EA Stop | Select-Object -First 1; [math]::Round($t.Value,1) } catch { 'N/A' }"
            )
            try:    t = float(t_raw)
            except: t = None
        if t:
            lecturas.append(t)
            color = C.GREEN if t < umbral_ok else C.YELLOW if t < umbral_alt else C.RED
            cprint(f"  Lectura {i+1}: {t}°C", color)
        else:
            cprint(f"  Lectura {i+1}: N/A", C.YELLOW)
        if i < 2: time.sleep(5)

    if len(lecturas) >= 2:
        variacion = max(lecturas) - min(lecturas)
        if variacion > 10: cprint(f"\n  Variacion: {variacion:.1f}°C — temperatura inestable.", C.RED)
        else:              cprint(f"\n  Variacion: {variacion:.1f}°C — temperatura estable.", C.GREEN)

    # Guardar esta lectura en el historial
    guardar_temp_historial(temp_cpu, temp_gpu, es_notebook)

    cprint("\n  [ Recomendacion ]", C.CYAN)
    if temp_cpu is None:
        cprint("  Instalar sensor de temperatura para diagnostico completo.", C.YELLOW)
    elif temp_cpu < umbral_ok:
        cprint("  Pasta termica en buen estado. No requiere accion.", C.GREEN)
        if es_notebook: cprint("  Tip: limpiar ventiladores cada 6-12 meses.", C.GRAY)
    elif temp_cpu < umbral_alt:
        cprint("  Limpiar ventiladores y rejillas de ventilacion.", C.YELLOW)
        cprint("  Si persiste, considerar cambio de pasta termica.", C.YELLOW)
    else:
        cprint("  CAMBIO DE PASTA TERMICA RECOMENDADO.", C.RED)
        cprint("  1. Apagar y desconectar el equipo", C.GRAY)
        cprint("  2. Limpiar pasta vieja con alcohol isopropilico 90%+", C.GRAY)
        cprint("  3. Aplicar pasta nueva (Arctic MX-4, Thermal Grizzly, etc.)", C.GRAY)
        cprint("  4. Limpiar ventiladores y disipador", C.GRAY)
        if es_notebook: cprint("  5. Considerar servicio tecnico si no tenes experiencia", C.GRAY)


# ════════════════════════════════════════════════════════════
#  SETUP
# ════════════════════════════════════════════════════════════

def run_setup():
    C.enable_windows_ansi()
    os.system('cls' if SO == 'Windows' else 'clear')
    cprint("""
  +---------------------------------------------------------+
  |   NEUROAUDIT -- SETUP / INSTALADOR DE DEPENDENCIAS     |
  +---------------------------------------------------------+""", C.CYAN)
    cprint(f"  Sistema detectado : {SO} -- {platform.platform()}", C.GRAY)
    cprint(f"  Autor             : {DEVELOPER}\n", C.GRAY)
    if not check_privileges():
        cprint("  ERROR: El setup requiere privilegios de administrador/root.", C.RED)
        if SO == "Linux": cprint("  Uso: sudo python3 neuroaudit.py --setup\n", C.YELLOW)
        else:             cprint("  Ejecutar como Administrador.\n", C.YELLOW)
        sys.exit(1)

    if SO == "Linux":
        distro_raw = run("grep '^ID_LIKE=' /etc/os-release | cut -d= -f2 | tr -d '\"'").lower()
        distro_id  = run("grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '\"'").lower()
        combined   = distro_raw + " " + distro_id
        if any(x in combined for x in ["debian","ubuntu","mint","pop","kali","elementary"]):
            pkg_mgr = "apt"; pkg_cmd = "apt install -y"
            pkg_deps = {"lm-sensors": "lm-sensors", "smartctl": "smartmontools", "nmap": "nmap", "ufw": "ufw"}
        elif any(x in combined for x in ["fedora","rhel","centos","rocky","alma"]):
            pkg_mgr = "dnf"; pkg_cmd = "dnf install -y"
            pkg_deps = {"sensors": "lm_sensors", "smartctl": "smartmontools", "nmap": "nmap", "ufw": "ufw"}
        elif any(x in combined for x in ["arch","manjaro","endeavour"]):
            pkg_mgr = "pacman"; pkg_cmd = "pacman -S --noconfirm"
            pkg_deps = {"sensors": "lm_sensors", "smartctl": "smartmontools", "nmap": "nmap", "ufw": "ufw"}
        else:
            pkg_mgr = None; pkg_cmd = None; pkg_deps = {}

        section("DEPENDENCIAS DEL SISTEMA")
        print()
        if not pkg_mgr:
            cprint("  Gestor no reconocido. Instalar manualmente: lm-sensors smartmontools nmap ufw", C.YELLOW)
        else:
            cprint(f"  Gestor detectado: {C.CYAN}{pkg_mgr}{C.RESET}\n")
            faltantes = {}
            for cmd, pkg in pkg_deps.items():
                if shutil.which(cmd): cprint(f"  {'OK':<6} {cmd:<16} ya instalado", C.GREEN)
                else:                 cprint(f"  {'FALTA':<6} {cmd:<16} ({pkg})", C.YELLOW); faltantes[cmd] = pkg
            if faltantes:
                resp = input(f"\n  {C.CYAN}Instalar {len(faltantes)} dependencia(s)? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    if pkg_mgr == "apt": os.system("apt update -qq")
                    for cmd, pkg in faltantes.items():
                        cprint(f"  Instalando {pkg}...", C.YELLOW)
                        ret = os.system(f"sudo {pkg_cmd} {pkg}")
                        cprint(f"  {pkg} {'OK' if ret==0 else 'ERROR'}.", C.GREEN if ret==0 else C.RED)
            else:
                cprint("  Todas las dependencias del sistema estan instaladas.", C.GREEN)

        if shutil.which("ufw"):
            ufw_status = run("ufw status | head -1")
            if "inactive" in ufw_status.lower():
                resp = input(f"\n  {C.CYAN}Activar UFW (firewall)? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    os.system("sudo ufw --force enable")
                    cprint("  UFW activado.", C.GREEN)

    section("DEPENDENCIAS PYTHON")
    print()
    py_deps = {"yaml": ("pyyaml", "Exportacion YAML"), "reportlab": ("reportlab", "Exportacion PDF")}
    py_faltantes = {}
    for mod, (pkg, desc) in py_deps.items():
        try:    __import__(mod); cprint(f"  {'OK':<6} {pkg:<16} {desc}", C.GREEN)
        except ImportError: cprint(f"  {'FALTA':<6} {pkg:<16} {desc}", C.YELLOW); py_faltantes[mod] = (pkg, desc)
    if py_faltantes:
        resp = input(f"\n  {C.CYAN}Instalar {len(py_faltantes)} modulo(s) Python? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            for mod, (pkg, desc) in py_faltantes.items():
                cprint(f"  Instalando {pkg}...", C.YELLOW)
                r = subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True, text=True)
                if r.returncode != 0:
                    r = subprocess.run([sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"], capture_output=True, text=True)
                cprint(f"  {pkg} {'OK' if r.returncode==0 else 'ERROR'}.", C.GREEN if r.returncode==0 else C.RED)
    else:
        cprint("\n  Todos los modulos Python estan instalados.", C.GREEN)

    if SO == "Linux":
        section("ACCESO DIRECTO (OPCIONAL)")
        script_path = os.path.abspath(__file__)
        link_path   = "/usr/local/bin/neuroaudit"
        if os.path.exists(link_path):
            cprint(f"  Symlink ya existe: {link_path}", C.GREEN)
        else:
            resp = input(f"\n  {C.CYAN}Crear symlink 'sudo neuroaudit'? (S/N): {C.RESET}").strip().lower()
            if resp == "s":
                try:
                    os.chmod(script_path, 0o755)
                    os.symlink(script_path, link_path)
                    cprint(f"  Symlink creado: {link_path}", C.GREEN)
                except Exception as e:
                    cprint(f"  Error: {e}", C.RED)

    section("RESUMEN DEL SETUP")
    print()
    cprint("  Setup completado.\n", C.GREEN)
    if SO == "Linux":
        for nombre, found in {"lm-sensors/sensors": shutil.which("sensors"), "smartmontools": shutil.which("smartctl"), "nmap": shutil.which("nmap"), "ufw": shutil.which("ufw")}.items():
            estado = f"{C.GREEN}OK{C.RESET}" if found else f"{C.RED}NO INSTALADO{C.RESET}"
            print(f"  {nombre:<25} {estado}")
    print()
    for mod, (pkg, desc) in py_deps.items():
        try:    __import__(mod); print(f"  {pkg:<25} {C.GREEN}OK{C.RESET}")
        except: print(f"  {pkg:<25} {C.RED}NO INSTALADO{C.RESET}")
    print()
    cprint("  Para iniciar NEUROAUDIT:", C.CYAN)
    if SO == "Linux": cprint("    sudo python3 neuroaudit.py", C.GRAY)
    else:             cprint("    python neuroaudit.py  (como Administrador)", C.GRAY)
    cprint("\n  Flags disponibles:", C.GRAY)
    cprint("    --no-banner   Oculta el logo ASCII (util en entornos corporativos)", C.GRAY)
    cprint("    --cliente     Output simplificado para mostrar frente al cliente", C.GRAY)
    print()
    input(f"  {C.CYAN}Presione Enter para salir...{C.RESET}")


# ════════════════════════════════════════════════════════════
#  MENÚ PRINCIPAL
# ════════════════════════════════════════════════════════════

def show_menu():
    tag = f"{C.GREEN}[LINUX]{C.RESET}" if SO == "Linux" else f"{C.CYAN}[WINDOWS]{C.RESET}"
    if MODO_CLIENTE:
        cprint(f"  {tag} {C.YELLOW}[MODO CLIENTE]{C.RESET}  Seleccione un modulo:\n")
    else:
        print(f"  {tag} Seleccione un modulo:\n")
    cprint("  [1]  Hardware e Identidad Termica",             C.RESET)
    cprint("  [2]  Mantenimiento del Sistema",                C.RESET)
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

    if "--setup" in sys.argv:
        run_setup()
        sys.exit(0)

    # Lanzar chequeo de actualizaciones en segundo plano
    start_update_check()

    if SO == "Linux":
        in_venv, venv_python, script_dir = _check_venv()
        launcher = os.path.join(script_dir, "neuroaudit")
        if not in_venv and os.path.exists(venv_python):
            cprint("\n  Detectado entorno virtual (venv) sin usar.", C.YELLOW)
            cprint(f"  Para mejores resultados usa: {launcher}", C.CYAN)
            resp = input(f"  {C.CYAN}Continuar de todas formas? (S/N): {C.RESET}").strip().lower()
            if resp != "s":
                cprint(f"\n  Ejecuta: {launcher}\n", C.GREEN)
                sys.exit(0)

    if not check_privileges():
        cprint(f"\n  ERROR: Ejecutar como root (Linux) o Administrador (Windows).\n", C.RED)
        if SO == "Linux":
            cprint("  Uso: sudo python3 neuroaudit.py\n", C.YELLOW)
        else:
            cprint("  Ejecutar cmd/PowerShell como Administrador.\n", C.YELLOW)
        sys.exit(1)

    M = Linux if SO == "Linux" else Windows

    acciones = {
        "1":  M.sys_info,
        "2":  M.maintenance,
        "3":  M.disk_health,
        "4":  M.security_audit,
        "5":  M.event_report,
        "6":  M.software_inventory,
        "7":  M.export_html,
        "8":  M.network_ping,
        "9":  M.network_scan,
        "10": run_permission_audit,
    }

    while True:
        show_banner()
        show_menu()
        op = input(f"{C.CYAN}  Seleccione operacion: {C.RESET}").strip()
        if op == "0":
            cprint(f"\n  Hasta luego. -- {DEVELOPER}\n", C.GREEN)
            break
        elif op in acciones:
            acciones[op]()
            pause()
        else:
            cprint("  Opcion no valida.", C.YELLOW)
            pause()

if __name__ == "__main__":
    main()
