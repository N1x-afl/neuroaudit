#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.1 - Multiplataforma (Windows + Linux)
# Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# USO:
#   Linux   : sudo python3 neuroaudit.py
#   Windows : python neuroaudit.py  (como Administrador)
# ===========================================================

import os
import sys

# ── Fix de paths para sudo (resuelve imports cuando se corre con sudo) ──
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

def _get_real_home():
    """Retorna el home del usuario real aunque se corra con sudo."""
    # SUDO_USER contiene el usuario original cuando se usa sudo
    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user and sudo_user != "root":
        import pwd
        try:
            return pwd.getpwnam(sudo_user).pw_dir
        except Exception:
            pass
    return os.path.expanduser("~")

import subprocess

def _check_venv():
    """Verifica si se esta corriendo dentro del venv de NEUROAUDIT."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = os.path.join(script_dir, ".venv", "bin", "python3")
    running_in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    return running_in_venv, venv_python, script_dir


import re
import json
import datetime
import shutil

VERSION     = "6.1"
SYSTEM_NAME = "NEUROAUDIT - Security & IT Suite"
DEVELOPER   = "Felipe Soluciones IT"
SO          = platform.system()   # "Windows" o "Linux"

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
        """Habilita colores ANSI y UTF-8 en la consola de Windows."""
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
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding="utf-8", errors="replace")
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding="utf-8", errors="replace")
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
    """Ejecuta un comando y retorna stdout como string."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True,
            text=True, timeout=timeout
        )
        return result.stdout.strip()
    except Exception:
        return ""

def pause():
    input(f"\n{C.CYAN}  Presione Enter para volver al menu...{C.RESET}")

# ── Verificacion de integridad ───────────────────────────────
def verify_integrity():
    try:
        with open(__file__, "r", encoding="utf-8") as f:
            content = f.read()
        return "Felipe Soluciones IT" in content and len(content) > 5000
    except Exception:
        return False

# ── Banner ───────────────────────────────────────────────────
def show_banner():
    os.system('cls' if SO == 'Windows' else 'clear')
    status_ok  = verify_integrity()
    status_txt = f"{C.GREEN}OK INTEGRIDAD VERIFICADA{C.RESET}" if status_ok \
                 else f"{C.RED}ERROR INTEGRIDAD COMPROMETIDA{C.RESET}"
    so_label   = f"{C.YELLOW}[WINDOWS]{C.RESET}" if SO == "Windows" \
                 else f"{C.GREEN}[LINUX]{C.RESET}"
    now        = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    if SO == "Linux":
        cprint("  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗", C.GREEN)
        cprint("  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╔══██╔══╝", C.GREEN)
        cprint("  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║  ", C.GREEN)
        cprint("  ██║╠██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║  ", C.GREEN)
        cprint("  ██║ ╠████║███████╗╠██████╔╝██║  ██║╠██████╔╝██║  ██║╠██████╔╝██████╔╝██║   ██║  ", C.GREEN)
        cprint("  ╔═╝  ╔═══╝╔══════╝ ╔═════╝ ╔═╝  ╔═╝ ╔═════╝ ╔═╝  ╔═╝ ╔═════╝ ╔═════╝ ╔═╝   ╔═╝  ", C.GREEN)
        cprint("  " + "=" * 82, C.CYAN)
        cprint("                   A  U  D  I  T     S  Y  S  T  E  M   v" + VERSION, C.CYAN)
        cprint("  " + "=" * 82, C.CYAN)
    else:
        # Logo Unicode para Windows Terminal (mismo que Linux)
        cprint("  ███╗   ██╗███████╗██╗   ██╗██████╗  ██████╗  █████╗ ██╗   ██╗██████╗ ██╗████████╗", C.GREEN)
        cprint("  ████╗  ██║██╔════╝██║   ██║██╔══██╗██╔═══██╗██╔══██╗██║   ██║██╔══██╗██║╔══██╔══╝", C.GREEN)
        cprint("  ██╔██╗ ██║█████╗  ██║   ██║██████╔╝██║   ██║███████║██║   ██║██║  ██║██║   ██║  ", C.GREEN)
        cprint("  ██║╠██╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══██║██║   ██║██║  ██║██║   ██║  ", C.GREEN)
        cprint("  ██║ ╠████║███████╗╠██████╔╝██║  ██║╠██████╔╝██║  ██║╠██████╔╝██████╔╝██║   ██║  ", C.GREEN)
        cprint("  ╔═╝  ╔═══╝╔══════╝ ╔═════╝ ╔═╝  ╔═╝ ╔═════╝ ╔═╝  ╔═╝ ╔═════╝ ╔═════╝ ╔═╝   ╔═╝  ", C.GREEN)
        cprint("  " + "=" * 82, C.CYAN)
        cprint("                   A  U  D  I  T     S  Y  S  T  E  M   v" + VERSION, C.CYAN)
        cprint("  " + "=" * 82, C.CYAN)

    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Estado   : {status_txt}")
    print(f"  Sistema  : {so_label}  {platform.platform()}")
    print(f"  Fecha    : {C.GRAY}{now}{C.RESET}")
    print(f"  Autor    : {C.GRAY}{DEVELOPER}{C.RESET}\n")

# ════════════════════════════════════════════════════════════
#  MODULOS LINUX
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
        serial     = run("sudo dmidecode -s system-serial-number 2>/dev/null").strip()
        cpu        = run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        ram        = run("free -h | grep Mem | awk '{print $3\"/\"$2}'")
        uptime_str = run("uptime -p")
        distro, pkg = Linux.get_distro()

        # Detectar notebook o desktop
        chassis = run("sudo dmidecode -s chassis-type 2>/dev/null").strip().lower()
        es_notebook = any(x in chassis for x in ["notebook","laptop","portable","sub notebook"])

        # Uptime en segundos
        try:    up_sec = int(run("awk '{print int($1)}' /proc/uptime").strip())
        except: up_sec = 0

        # Temperatura CPU
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

        # Temperatura GPU (nvidia)
        gpu_t = run("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader 2>/dev/null").strip()
        try:    temp_gpu = float(gpu_t)
        except: temp_gpu = None

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

        # Diagnostico pasta termica
        print()
        resp = input(f"  {C.CYAN}Ejecutar diagnostico de pasta termica? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            analizar_pasta_termica(temp_cpu, temp_gpu, up_sec, es_notebook)


    # ── 2: Mantenimiento ─────────────────────────────────────
    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA [LINUX]")
        _, pkg = Linux.get_distro()

        # Submenú de mantenimiento
        cprint("\n  Selecciona que operaciones ejecutar:\n", C.GRAY)
        cprint("  [1]  Actualizar el sistema", C.RESET)
        cprint("  [2]  Purgar paquetes huerfanos y residuales", C.RESET)
        cprint("  [3]  Limpiar cache del gestor de paquetes", C.RESET)
        cprint("  [4]  Limpiar /tmp y archivos temporales", C.RESET)
        cprint("  [5]  Limpiar logs del sistema (journalctl)", C.RESET)
        cprint("  [6]  Limpiar cache de usuario (~/.cache)", C.RESET)
        cprint("  [7]  TODO lo anterior", C.CYAN)
        print()
        op = input(f"  {C.CYAN}Seleccione operacion: {C.RESET}").strip()

        hacer = set()
        if op == "7":
            hacer = {"1","2","3","4","5","6"}
        elif op in {"1","2","3","4","5","6"}:
            hacer = {op}
        else:
            cprint("  Opcion no valida.", C.YELLOW)
            return

        # ── 1: Actualizar ────────────────────────────────────
        if "1" in hacer:
            cprint("\n  [ Actualizaciones del Sistema ]", C.YELLOW)
            if pkg == "APT":
                cprint("  Ejecutando apt update + upgrade...", C.GRAY)
                os.system("sudo apt update")
                # Mostrar cuantos paquetes se van a actualizar
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
                if resp == "s":
                    os.system("sudo dnf upgrade -y")
            elif pkg == "PACMAN":
                os.system("sudo pacman -Syu --noconfirm")
            else:
                cprint("  Gestor de paquetes no soportado.", C.RED)

        # ── 2: Purgar huerfanos y residuales ─────────────────
        if "2" in hacer:
            cprint("\n  [ Purga de Paquetes Huerfanos y Residuales ]", C.YELLOW)
            if pkg == "APT":
                # Mostrar que se va a purgar antes
                huerfanos = run("apt-get autoremove --dry-run 2>/dev/null | grep '^Remov' | wc -l").strip()
                residuales = run("dpkg -l | grep '^rc' | wc -l").strip()
                cprint(f"  Paquetes huerfanos   : {huerfanos}", C.CYAN)
                cprint(f"  Paquetes residuales  : {residuales}", C.CYAN)

                if int(huerfanos or 0) > 0:
                    resp = input(f"  {C.CYAN}Eliminar paquetes huerfanos? (S/N): {C.RESET}").strip().lower()
                    if resp == "s":
                        os.system("sudo apt autoremove -y")
                        cprint("  Huerfanos eliminados.", C.GREEN)

                if int(residuales or 0) > 0:
                    resp = input(f"  {C.CYAN}Purgar configuraciones residuales ({residuales} paquetes)? (S/N): {C.RESET}").strip().lower()
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

        # ── 3: Cache del gestor ──────────────────────────────
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

        # ── 4: /tmp y temporales ─────────────────────────────
        if "4" in hacer:
            cprint("\n  [ Limpieza de /tmp y Temporales ]", C.YELLOW)
            for tmp in ["/tmp", "/var/tmp"]:
                if os.path.exists(tmp):
                    size = run(f"du -sh {tmp} 2>/dev/null | cut -f1")
                    count = run(f"find {tmp} -type f -atime +2 2>/dev/null | wc -l").strip()
                    cprint(f"  {tmp:<15} {size:<10} ({count} archivos > 2 dias)", C.CYAN)
            resp = input(f"  {C.CYAN}Limpiar archivos de mas de 2 dias? (S/N): {C.RESET}").strip().lower()
            if resp == "s":
                os.system("sudo find /tmp -type f -atime +2 -delete 2>/dev/null")
                os.system("sudo find /var/tmp -type f -atime +2 -delete 2>/dev/null")
                os.system("sudo find /tmp /var/tmp -type d -empty -delete 2>/dev/null")
                cprint("  Temporales limpiados.", C.GREEN)

        # ── 5: Logs del sistema ──────────────────────────────
        if "5" in hacer:
            cprint("\n  [ Limpieza de Logs del Sistema ]", C.YELLOW)
            log_size = run("journalctl --disk-usage 2>/dev/null | grep -oE '[0-9.]+ [A-Z]?B'")
            cprint(f"  Tamanio actual de logs: {log_size}", C.CYAN)
            cprint("  Opciones de limpieza:", C.GRAY)
            cprint("    [1] Conservar ultimos 7 dias", C.RESET)
            cprint("    [2] Conservar ultimos 30 dias", C.RESET)
            cprint("    [3] Conservar solo 500 MB", C.RESET)
            cprint("    [4] Omitir", C.RESET)
            sub = input(f"  {C.CYAN}Seleccione: {C.RESET}").strip()
            if sub == "1":
                os.system("sudo journalctl --vacuum-time=7d")
                cprint("  Logs > 7 dias eliminados.", C.GREEN)
            elif sub == "2":
                os.system("sudo journalctl --vacuum-time=30d")
                cprint("  Logs > 30 dias eliminados.", C.GREEN)
            elif sub == "3":
                os.system("sudo journalctl --vacuum-size=500M")
                cprint("  Logs reducidos a 500 MB.", C.GREEN)
            else:
                cprint("  Limpieza de logs omitida.", C.GRAY)
            # Logs comprimidos en /var/log
            gz_size = run("find /var/log -name '*.gz' -exec du -ch {} + 2>/dev/null | tail -1 | cut -f1")
            if gz_size and gz_size.strip() != "0":
                resp = input(f"  {C.CYAN}Eliminar logs comprimidos .gz en /var/log ({gz_size})? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    os.system("sudo find /var/log -name '*.gz' -delete 2>/dev/null")
                    os.system("sudo find /var/log -name '*.old' -delete 2>/dev/null")
                    cprint("  Logs comprimidos eliminados.", C.GREEN)

        # ── 6: Cache de usuario ──────────────────────────────
        if "6" in hacer:
            cprint("\n  [ Limpieza de Cache de Usuario (~/.cache) ]", C.YELLOW)
            cache_dir = os.path.expanduser("~/.cache")
            if os.path.exists(cache_dir):
                size = run(f"du -sh {cache_dir} 2>/dev/null | cut -f1")
                cprint(f"  Tamanio de ~/.cache: {size}", C.CYAN)
                # Mostrar las subcarpetas mas grandes
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

        # ── Resumen ──────────────────────────────────────────
        cprint("\n  [ Resumen Post-Mantenimiento ]", C.CYAN)
        disk_libre = run("df -h / | awk 'NR==2{print $4}'")
        cprint(f"  Espacio libre en /: {C.GREEN}{disk_libre}{C.RESET}")
        ram_libre  = run("free -h | awk '/^Mem/{print $7}'")
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

    # ── 4: Auditoria de Seguridad ────────────────────────────
    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD [LINUX]")

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
            out = run("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -60")
            count = run("dpkg -l | grep '^ii' | wc -l")
        elif pkg == "DNF":
            out = run("rpm -qa --qf '%{NAME} %{VERSION}\n' | sort | head -60")
            count = run("rpm -qa | wc -l")
        elif pkg == "PACMAN":
            out = run("pacman -Q | head -60")
            count = run("pacman -Q | wc -l")
        else:
            out = ""
            count = "?"

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

    # ── 7: Reporte HTML ──────────────────────────────────────
    @staticmethod
    def export_html():
        section("EXPORTAR REPORTE A HTML [LINUX]")
        Linux._generate_html()

    @staticmethod
    def _generate_html():
        distro, pkg = Linux.get_distro()
        cpu    = run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2").strip()
        ram    = run("free -h | grep Mem | awk '{print $3 \"/\" $2}'")
        uptime = run("uptime -p")
        serial = run("sudo dmidecode -s system-serial-number 2>/dev/null").strip() or "N/A"
        now    = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        label  = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        # Discos
        disk_raw = run("df -h | grep '^/dev'").splitlines()
        disk_rows = ""
        for line in disk_raw:
            parts = line.split()
            if len(parts) >= 6:
                uso = parts[4].replace('%', '')
                color = '#e74c3c' if int(uso) > 85 else '#f39c12' if int(uso) > 65 else '#2ecc71'
                disk_rows += f"<tr><td>{parts[0]}</td><td>{parts[1]}</td><td>{parts[2]}</td>" \
                             f"<td>{parts[3]}</td><td style='color:{color};font-weight:bold'>{parts[4]}</td>" \
                             f"<td>{parts[5]}</td></tr>"

        # Puertos
        port_raw = run("sudo ss -tunlp | grep LISTEN").splitlines()
        port_rows = "".join(f"<tr><td colspan='3'>{html_escape(l)}</td></tr>" for l in port_raw)

        # Usuarios
        users_raw = run("cat /etc/passwd | grep -E '/bin/bash|/bin/sh'").splitlines()
        user_rows = "".join(f"<tr><td colspan='3'>{html_escape(u)}</td></tr>" for u in users_raw)

        # Servicios fallidos
        svc_raw = run("systemctl --failed --no-pager 2>/dev/null").splitlines()
        svc_rows = "".join(f"<tr><td colspan='2'>{html_escape(s)}</td></tr>" for s in svc_raw if s.strip())

        # Eventos criticos
        ev_raw = run("sudo journalctl -p err -n 20 --no-pager 2>/dev/null").splitlines()
        ev_rows = "".join(f"<tr><td>{html_escape(e)}</td></tr>" for e in ev_raw if e.strip())

        # Software
        if pkg == "APT":
            sw_raw = run("dpkg -l | grep '^ii' | awk '{print $2, $3}'").splitlines()
            sw_count = run("dpkg -l | grep '^ii' | wc -l")
        elif pkg == "DNF":
            sw_raw = run("rpm -qa --qf '%{NAME} %{VERSION}\n' | sort").splitlines()
            sw_count = run("rpm -qa | wc -l")
        else:
            sw_raw = []
            sw_count = "?"
        sw_rows = "".join(f"<tr><td colspan='2'>{html_escape(s)}</td></tr>" for s in sw_raw[:100])

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>NEUROAUDIT Report Linux - {now}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d1117; color: #c9d1d9; font-family: 'Consolas', monospace; padding: 20px; }}
  h1 {{ color: #00ff88; text-align: center; font-size: 2em; padding: 20px 0 5px; letter-spacing: 4px; }}
  .subtitle {{ text-align:center; color:#58a6ff; margin-bottom:20px; font-size:0.9em; }}
  .badge {{ display:inline-block; background:#161b22; border:1px solid #30363d; border-radius:6px;
            padding:4px 12px; margin:4px; font-size:0.8em; color:#8b949e; }}
  .card {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:20px; margin:20px 0; }}
  .card h2 {{ color:#00ff88; border-bottom:1px solid #30363d; padding-bottom:8px;
               margin-bottom:15px; font-size:1em; letter-spacing:2px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.82em; }}
  th {{ background:#21262d; color:#58a6ff; padding:8px; text-align:left; border-bottom:2px solid #30363d; }}
  td {{ padding:6px 8px; border-bottom:1px solid #21262d; word-break:break-all; }}
  tr:hover td {{ background:#1c2128; }}
  .info-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }}
  .info-item {{ background:#21262d; border-radius:6px; padding:12px; }}
  .info-item .label {{ color:#8b949e; font-size:0.75em; text-transform:uppercase; letter-spacing:1px; }}
  .info-item .value {{ color:#c9d1d9; font-size:0.9em; margin-top:4px; }}
  .footer {{ text-align:center; color:#484f58; font-size:0.75em; margin-top:30px;
             padding-top:15px; border-top:1px solid #21262d; }}
  .tag-linux {{ color: #2ecc71; font-weight: bold; }}
</style>
</head>
<body>
<h1>NEUROAUDIT</h1>
<div class="subtitle">System Audit Report &nbsp;|&nbsp; v{VERSION} &nbsp;|&nbsp;
  <span class="tag-linux">LINUX</span> &nbsp;|&nbsp; {label}</div>
<div style="text-align:center;margin-bottom:20px;">
  <span class="badge">OS: {distro}</span>
  <span class="badge">PKG: {pkg}</span>
  <span class="badge">Autor: {DEVELOPER}</span>
</div>

<div class="card">
  <h2>INFRAESTRUCTURA</h2>
  <div class="info-grid">
    <div class="info-item"><div class="label">Serial</div><div class="value">{serial}</div></div>
    <div class="info-item"><div class="label">CPU</div><div class="value">{cpu}</div></div>
    <div class="info-item"><div class="label">RAM</div><div class="value">{ram}</div></div>
    <div class="info-item"><div class="label">Uptime</div><div class="value">{uptime}</div></div>
    <div class="info-item"><div class="label">Distro</div><div class="value">{distro}</div></div>
    <div class="info-item"><div class="label">Gestor</div><div class="value">{pkg}</div></div>
  </div>
</div>

<div class="card">
  <h2>USO DE DISCOS</h2>
  <table><thead><tr><th>Dispositivo</th><th>Tamanio</th><th>Usado</th>
  <th>Libre</th><th>Uso %</th><th>Montaje</th></tr></thead>
  <tbody>{disk_rows}</tbody></table>
</div>

<div class="card">
  <h2>USUARIOS DEL SISTEMA</h2>
  <table><thead><tr><th colspan="3">Entrada /etc/passwd</th></tr></thead>
  <tbody>{user_rows}</tbody></table>
</div>

<div class="card">
  <h2>PUERTOS EN ESCUCHA</h2>
  <table><thead><tr><th colspan="3">ss -tunlp LISTEN</th></tr></thead>
  <tbody>{port_rows}</tbody></table>
</div>

<div class="card">
  <h2>SERVICIOS CON FALLO</h2>
  <table><thead><tr><th colspan="2">systemctl --failed</th></tr></thead>
  <tbody>{svc_rows or "<tr><td colspan='2'>Sin servicios fallidos.</td></tr>"}</tbody></table>
</div>

<div class="card">
  <h2>EVENTOS CRITICOS (journalctl -p err)</h2>
  <table><thead><tr><th>Evento</th></tr></thead>
  <tbody>{ev_rows or "<tr><td>Sin eventos criticos recientes.</td></tr>"}</tbody></table>
</div>

<div class="card">
  <h2>SOFTWARE INSTALADO ({sw_count} paquetes - mostrando 100)</h2>
  <table><thead><tr><th colspan="2">Paquete / Version</th></tr></thead>
  <tbody>{sw_rows}</tbody></table>
</div>

<div class="footer">
  NEUROAUDIT v{VERSION} &nbsp;|&nbsp; {DEVELOPER} &nbsp;|&nbsp;
  Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
</div>
</body>
</html>"""

        home     = _get_real_home()
        rep_dir  = os.path.join(home, "NEUROAUDIT_Reportes")
        os.makedirs(rep_dir, exist_ok=True)
        filepath = os.path.join(rep_dir, f"reporte_linux_{now}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        cprint(f"\n  Reporte guardado en: {filepath}", C.GREEN)
        try:
            # Abrir como usuario real (no root) para evitar errores de D-Bus
            sudo_user = os.environ.get("SUDO_USER")
            if sudo_user and sudo_user != "root":
                subprocess.Popen(["sudo", "-u", sudo_user, "xdg-open", filepath],
                                 env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":0"),
                                      "DBUS_SESSION_BUS_ADDRESS": os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")})
            else:
                subprocess.Popen(["xdg-open", filepath])
        except Exception:
            cprint("  Abrir manualmente el archivo HTML.", C.YELLOW)


    # ── 8: Ping / Conectividad ───────────────────────────────
    @staticmethod
    def network_ping():
        section("PING / TEST DE CONECTIVIDAD [LINUX]")

        defaults = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "google.com", "github.com"]
        cprint("\n  Destinos predeterminados + personalizados", C.GRAY)
        extra = input(f"  {C.CYAN}Agregar IPs/dominios separados por coma (Enter para omitir): {C.RESET}").strip()
        targets = defaults + [t.strip() for t in extra.split(",") if t.strip()]

        cprint(f"\n  {'DESTINO':<25} {'ESTADO':<12} {'LATENCIA'}", C.YELLOW)
        cprint(f"  {'-'*55}", C.GRAY)
        for t in targets:
            result = run(f"ping -c 2 -W 2 {t} 2>/dev/null")
            if "2 received" in result or "1 received" in result:
                match = re.search(r"min/avg/max.*?=([\d.]+)/([\d.]+)", result)
                latency = f"{match.group(2)} ms" if match else "OK"
                cprint(f"  {t:<25} {'ONLINE':<12} {latency}", C.GREEN)
            else:
                cprint(f"  {t:<25} {'OFFLINE':<12} ---", C.RED)

        # Test DNS
        cprint("\n  [ Resolucion DNS ]", C.YELLOW)
        for domain in ["google.com", "cloudflare.com", "github.com"]:
            dns = run(f"dig +short {domain} 2>/dev/null || nslookup {domain} 2>/dev/null | grep 'Address' | tail -1")
            status = C.GREEN + "OK" + C.RESET if dns else C.RED + "FALLO" + C.RESET
            print(f"  {domain:<25} {status}  {dns[:40]}")

        # Velocidad de red (interfaces)
        cprint("\n  [ Interfaces de Red ]", C.YELLOW)
        os.system("ip -br addr show 2>/dev/null || ifconfig 2>/dev/null | grep -E 'inet|flags'")

    # ── 9: Escaneo de Red Local ──────────────────────────────
    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL [LINUX]")

        # Detectar gateway e IP local
        gateway = run("ip route | grep default | awk '{print $3}' | head -1")
        local_ip = run("hostname -I | awk '{print $1}'")
        iface   = run("ip route | grep default | awk '{print $5}' | head -1")

        if not gateway:
            cprint("  No se detectó gateway. Verificar conexión de red.", C.RED)
            return

        # Calcular subnet /24
        parts   = local_ip.rsplit(".", 1)
        subnet  = parts[0] + ".0/24" if len(parts) == 2 else "192.168.1.0/24"

        print(f"\n  IP Local  : {C.CYAN}{local_ip}{C.RESET}")
        print(f"  Gateway   : {C.CYAN}{gateway}{C.RESET}")
        print(f"  Interfaz  : {C.CYAN}{iface}{C.RESET}")
        print(f"  Subred    : {C.CYAN}{subnet}{C.RESET}")

        cprint(f"\n  Escaneando {subnet} (ping sweep)...", C.YELLOW)
        cprint(f"  {'IP':<20} {'HOSTNAME':<30} {'ESTADO'}", C.YELLOW)
        cprint(f"  {'-'*65}", C.GRAY)

        # Usar nmap si está disponible, si no hacer ping sweep manual
        if shutil.which("nmap"):
            cprint("  Usando nmap para escaneo detallado...\n", C.GRAY)
            raw = run(f"sudo nmap -sn {subnet} 2>/dev/null", timeout=60)
            # Parsear salida de nmap
            current_ip = ""
            for line in raw.splitlines():
                ip_match = re.search(r"(\d+\.\d+\.\d+\.\d+)", line)
                if "Nmap scan report" in line and ip_match:
                    current_ip = ip_match.group(1)
                elif "Host is up" in line and current_ip:
                    hostname = run(f"hostname -f {current_ip} 2>/dev/null || echo ''")
                    marker = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if current_ip == local_ip else ""
                    cprint(f"  {current_ip:<20} {hostname[:28]:<30} ONLINE {marker}", C.GREEN)
                    current_ip = ""
        else:
            cprint("  nmap no encontrado, usando ping sweep basico...", C.GRAY)
            cprint("  (instalar nmap para escaneo completo: sudo apt install nmap)\n", C.GRAY)
            base = parts[0] + "." if len(parts) == 2 else "192.168.1."
            activos = 0
            for i in range(1, 255):
                ip = f"{base}{i}"
                result = run(f"ping -c 1 -W 1 {ip} 2>/dev/null")
                if "1 received" in result or "bytes from" in result:
                    hostname = run(f"nslookup {ip} 2>/dev/null | grep 'name =' | awk '{{print $4}}'") or "---"
                    marker = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if ip == local_ip else ""
                    cprint(f"  {ip:<20} {hostname[:28]:<30} ONLINE {marker}", C.GREEN)
                    activos += 1
            cprint(f"\n  Total dispositivos activos: {activos}", C.CYAN)

        # Tabla ARP (dispositivos vistos recientemente)
        cprint("\n  [ Tabla ARP - Dispositivos Recientes ]", C.YELLOW)
        os.system("arp -n 2>/dev/null | grep -v 'incomplete' | head -20")


# ════════════════════════════════════════════════════════════
#  MODULOS WINDOWS
# ════════════════════════════════════════════════════════════

class Windows:

    @staticmethod
    def _ps(cmd):
        """Ejecuta un comando PowerShell y retorna salida."""
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

        # Detectar notebook o desktop via WMI
        chassis_raw = Windows._ps(
            "(Get-CimInstance Win32_SystemEnclosure).ChassisTypes | "
            "ForEach-Object { $_ } | Select-Object -First 1"
        ).strip()
        # ChassisTypes: 8,9,10,11,12,14=notebook/laptop, resto=desktop
        try:
            chassis_type = int(chassis_raw)
            es_notebook  = chassis_type in [8,9,10,11,12,14,18,21]
        except Exception:
            es_notebook = False

        # Uptime en segundos
        try:
            up_sec = int(Windows._ps(
                "$r=Get-CimInstance Win32_OperatingSystem;"
                "[int](((Get-Date)-$r.LastBootUpTime).TotalSeconds)"
            ).strip())
        except Exception:
            up_sec = 0

        # Temperatura CPU via OpenHardwareMonitor
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

        # Temperatura GPU via OpenHardwareMonitor
        gpu_temp_cmd = (
            "try { $t=Get-CimInstance -Namespace 'root/OpenHardwareMonitor' -ClassName Sensor "
            "-Filter \"SensorType='Temperature' AND Name LIKE '%GPU%'\" -EA Stop | "
            "Select-Object -First 1; [math]::Round($t.Value,1) } catch { 'N/A' }"
        )
        gpu_val = Windows._ps(gpu_temp_cmd)
        try:    temp_gpu = float(gpu_val)
        except: temp_gpu = None

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

        # Diagnostico pasta termica
        resp = input(f"  {C.CYAN}Ejecutar diagnostico de pasta termica? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            analizar_pasta_termica(temp_cpu, temp_gpu, up_sec, es_notebook)


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
                for dp, dirs, files in os.walk(p):
                    for f in files:
                        try:
                            os.remove(os.path.join(dp, f))
                        except Exception:
                            pass
                cprint(f"  Limpiado: {p}  ({size/1024/1024:.1f} MB)", C.GREEN)
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

    # ── 4: Auditoria de Seguridad ────────────────────────────
    @staticmethod
    def security_audit():
        section("AUDITORIA DE SEGURIDAD [WINDOWS]")

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

    # ── 8: Ping / Conectividad ───────────────────────────────
    @staticmethod
    def network_ping():
        section("PING / TEST DE CONECTIVIDAD [WINDOWS]")

        defaults = ["8.8.8.8", "8.8.4.4", "1.1.1.1", "google.com", "github.com"]
        extra = input(f"  {C.CYAN}Agregar IPs/dominios separados por coma (Enter para omitir): {C.RESET}").strip()
        targets = defaults + [t.strip() for t in extra.split(",") if t.strip()]

        cprint(f"\n  {'DESTINO':<25} {'ESTADO':<12} {'LATENCIA'}", C.YELLOW)
        cprint(f"  {'-'*55}", C.GRAY)
        for t in targets:
            result = run(f"ping -n 2 -w 2000 {t}", timeout=10)
            if "TTL=" in result or "ttl=" in result:
                match = re.search(r"Media = (\d+)ms|Promedio = (\d+)ms|Average = (\d+)ms|(\d+)ms", result)
                latency = f"{match.group(0)}" if match else "OK"
                cprint(f"  {t:<25} {'ONLINE':<12} {latency}", C.GREEN)
            else:
                cprint(f"  {t:<25} {'OFFLINE':<12} ---", C.RED)

        cprint("\n  [ Resolucion DNS ]", C.YELLOW)
        for domain in ["google.com", "cloudflare.com", "github.com"]:
            dns = Windows._ps(
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

    # ── 9: Escaneo de Red Local ──────────────────────────────
    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL [WINDOWS]")

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

        parts = local_ip.rsplit(".", 1)
        subnet = parts[0] + ".0/24" if len(parts) == 2 else "192.168.1.0/24"
        base   = parts[0] + "." if len(parts) == 2 else "192.168.1."

        print(f"\n  IP Local  : {C.CYAN}{local_ip}{C.RESET}")
        print(f"  Gateway   : {C.CYAN}{gateway}{C.RESET}")
        print(f"  Subred    : {C.CYAN}{subnet}{C.RESET}")

        if shutil.which("nmap"):
            cprint(f"\n  Escaneando {subnet} con nmap...", C.YELLOW)
            cprint(f"  {'IP':<20} {'ESTADO'}", C.YELLOW)
            cprint(f"  {'-'*35}", C.GRAY)
            raw = run(f"nmap -sn {subnet}", timeout=60)
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
            cprint("  instalar nmap para resultados mas rapidos y detallados", C.GRAY)
            cprint(f"\n  {'IP':<20} {'ESTADO'}", C.YELLOW)
            cprint(f"  {'-'*35}", C.GRAY)
            activos = 0
            for i in range(1, 255):
                ip = f"{base}{i}"
                result = run(f"ping -n 1 -w 500 {ip}", timeout=3)
                if "TTL=" in result or "ttl=" in result:
                    marker = f"{C.YELLOW}[TU EQUIPO]{C.RESET}" if ip == local_ip else ""
                    cprint(f"  {ip:<20} ONLINE {marker}", C.GREEN)
                    activos += 1
            cprint(f"\n  Total dispositivos activos: {activos}", C.CYAN)

        cprint("\n  [ Tabla ARP - Dispositivos Recientes ]", C.YELLOW)
        arp = Windows._ps("arp -a | Out-String")
        print(arp)

    # ── 7: Reporte HTML ──────────────────────────────────────
    @staticmethod
    def export_html():
        section("EXPORTAR REPORTE A HTML [WINDOWS]")

        now   = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        label = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        cpu    = Windows._ps("(Get-CimInstance Win32_Processor).Name.Trim()")
        serial = Windows._ps("(Get-CimInstance Win32_BIOS).SerialNumber.Trim()")
        os_ver = Windows._ps("(Get-CimInstance Win32_OperatingSystem).Caption")
        ram    = Windows._ps(
            "$r=Get-CimInstance Win32_OperatingSystem;"
            "[math]::Round(($r.TotalVisibleMemorySize-$r.FreePhysicalMemory)/1MB,2).ToString()"
            "+' / '+"
            "[math]::Round($r.TotalVisibleMemorySize/1MB,2).ToString()+' GB'"
        )
        uptime = Windows._ps(
            "$r=Get-CimInstance Win32_OperatingSystem;$u=(Get-Date)-$r.LastBootUpTime;"
            "'{0}d {1}h {2}m' -f $u.Days,$u.Hours,$u.Minutes"
        )

        # Discos
        disk_raw = Windows._ps(
            "Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | "
            "Select-Object Name,"
            "@{N='U';E={[math]::Round($_.Used/1GB,2)}},"
            "@{N='F';E={[math]::Round($_.Free/1GB,2)}},"
            "@{N='T';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}},"
            "@{N='P';E={[math]::Round($_.Used/($_.Used+$_.Free)*100,1)}} | "
            "ConvertTo-Json"
        )
        disk_rows = ""
        try:
            disks = json.loads(disk_raw)
            if isinstance(disks, dict):
                disks = [disks]
            for d in disks:
                pct   = d.get('P', 0)
                color = '#e74c3c' if pct > 85 else '#f39c12' if pct > 65 else '#2ecc71'
                disk_rows += (f"<tr><td>{d.get('Name','')}</td><td>{d.get('U','')} GB</td>"
                              f"<td>{d.get('F','')} GB</td><td>{d.get('T','')} GB</td>"
                              f"<td style='color:{color};font-weight:bold'>{pct}%</td></tr>")
        except Exception:
            disk_rows = f"<tr><td colspan='5'>{html_escape(disk_raw[:200])}</td></tr>"

        # Software
        sw_raw = Windows._ps(
            "$paths=@('HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
            "'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
            "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*');"
            "$paths | ForEach-Object { Get-ItemProperty $_ -EA SilentlyContinue } | "
            "Where-Object { $_.DisplayName } | Sort-Object DisplayName | "
            "Select-Object -First 100 DisplayName,DisplayVersion | ConvertTo-Json"
        )
        sw_rows = ""
        try:
            sw_list = json.loads(sw_raw)
            if isinstance(sw_list, dict):
                sw_list = [sw_list]
            sw_rows = "".join(
                f"<tr><td>{html_escape(str(s.get('DisplayName','')))}</td>"
                f"<td>{html_escape(str(s.get('DisplayVersion','')))}</td></tr>"
                for s in sw_list
            )
        except Exception:
            sw_rows = "<tr><td colspan='2'>Error al obtener software.</td></tr>"

        # Puertos
        port_raw = Windows._ps(
            "Get-NetTCPConnection -State Listen -EA SilentlyContinue | "
            "Select-Object LocalAddress,LocalPort,"
            "@{N='P';E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).Name}} | "
            "Sort-Object LocalPort | ConvertTo-Json"
        )
        port_rows = ""
        try:
            ports = json.loads(port_raw)
            if isinstance(ports, dict):
                ports = [ports]
            port_rows = "".join(
                f"<tr><td>{p.get('LocalAddress','')}</td>"
                f"<td>{p.get('LocalPort','')}</td>"
                f"<td>{p.get('P','')}</td></tr>"
                for p in ports
            )
        except Exception:
            port_rows = f"<tr><td colspan='3'>{html_escape(port_raw[:300])}</td></tr>"

        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>NEUROAUDIT Report Windows - {now}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d1117; color: #c9d1d9; font-family: 'Consolas', monospace; padding: 20px; }}
  h1 {{ color: #00ff88; text-align: center; font-size: 2em; padding: 20px 0 5px; letter-spacing: 4px; }}
  .subtitle {{ text-align:center; color:#58a6ff; margin-bottom:20px; font-size:0.9em; }}
  .badge {{ display:inline-block; background:#161b22; border:1px solid #30363d; border-radius:6px;
            padding:4px 12px; margin:4px; font-size:0.8em; color:#8b949e; }}
  .card {{ background:#161b22; border:1px solid #30363d; border-radius:8px; padding:20px; margin:20px 0; }}
  .card h2 {{ color:#00ff88; border-bottom:1px solid #30363d; padding-bottom:8px;
               margin-bottom:15px; font-size:1em; letter-spacing:2px; }}
  table {{ width:100%; border-collapse:collapse; font-size:0.82em; }}
  th {{ background:#21262d; color:#58a6ff; padding:8px; text-align:left; border-bottom:2px solid #30363d; }}
  td {{ padding:6px 8px; border-bottom:1px solid #21262d; word-break:break-all; }}
  tr:hover td {{ background:#1c2128; }}
  .info-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px; }}
  .info-item {{ background:#21262d; border-radius:6px; padding:12px; }}
  .info-item .label {{ color:#8b949e; font-size:0.75em; text-transform:uppercase; letter-spacing:1px; }}
  .info-item .value {{ color:#c9d1d9; font-size:0.9em; margin-top:4px; }}
  .footer {{ text-align:center; color:#484f58; font-size:0.75em; margin-top:30px;
             padding-top:15px; border-top:1px solid #21262d; }}
  .tag-win {{ color:#58a6ff; font-weight:bold; }}
</style>
</head>
<body>
<h1>NEUROAUDIT</h1>
<div class="subtitle">System Audit Report &nbsp;|&nbsp; v{VERSION} &nbsp;|&nbsp;
  <span class="tag-win">WINDOWS</span> &nbsp;|&nbsp; {label}</div>
<div style="text-align:center;margin-bottom:20px;">
  <span class="badge">OS: {os_ver}</span>
  <span class="badge">Autor: {DEVELOPER}</span>
</div>

<div class="card">
  <h2>INFRAESTRUCTURA</h2>
  <div class="info-grid">
    <div class="info-item"><div class="label">Serial</div><div class="value">{serial}</div></div>
    <div class="info-item"><div class="label">CPU</div><div class="value">{cpu}</div></div>
    <div class="info-item"><div class="label">RAM</div><div class="value">{ram}</div></div>
    <div class="info-item"><div class="label">Uptime</div><div class="value">{uptime}</div></div>
    <div class="info-item"><div class="label">Sistema</div><div class="value">{os_ver}</div></div>
  </div>
</div>

<div class="card">
  <h2>USO DE DISCOS</h2>
  <table><thead><tr><th>Unidad</th><th>Usado</th><th>Libre</th><th>Total</th><th>Uso %</th></tr></thead>
  <tbody>{disk_rows}</tbody></table>
</div>

<div class="card">
  <h2>PUERTOS EN ESCUCHA</h2>
  <table><thead><tr><th>Direccion</th><th>Puerto</th><th>Proceso</th></tr></thead>
  <tbody>{port_rows}</tbody></table>
</div>

<div class="card">
  <h2>SOFTWARE INSTALADO (primeros 100)</h2>
  <table><thead><tr><th>Nombre</th><th>Version</th></tr></thead>
  <tbody>{sw_rows}</tbody></table>
</div>

<div class="footer">
  NEUROAUDIT v{VERSION} &nbsp;|&nbsp; {DEVELOPER} &nbsp;|&nbsp;
  Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
</div>
</body>
</html>"""

        rep_dir  = os.path.join(os.path.expanduser("~"), "Desktop", "NEUROAUDIT_Reportes")
        os.makedirs(rep_dir, exist_ok=True)
        filepath = os.path.join(rep_dir, f"reporte_windows_{now}.html")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        cprint(f"\n  Reporte guardado en: {filepath}", C.GREEN)
        try:
            os.startfile(filepath)
        except Exception:
            cprint("  Abrir manualmente el archivo HTML.", C.YELLOW)


# ════════════════════════════════════════════════════════════
#  MOTOR DE EXPORTACION MULTI-FORMATO
# ════════════════════════════════════════════════════════════

def ensure_deps():
    """Localiza e instala dependencias Python con manejo robusto de paths para sudo."""
    import importlib

    # Forzar inclusion de TODAS las rutas posibles donde pip instala paquetes
    # Esto resuelve el problema cuando se corre con sudo y sys.path es distinto
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
            continue  # ya disponible
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
                # Refrescar paths y reintentar import
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
            cprint(f"  Ejecuta esto manualmente y vuelve a intentar:", C.YELLOW)
            cprint(f"  sudo pip install {pkg} --break-system-packages", C.CYAN)


def collect_report_data():
    """Recopila todos los datos del sistema en un dict estructurado."""
    cprint("  Recopilando datos del sistema...", C.GRAY)
    now = datetime.datetime.now()
    data = {
        "meta": {
            "herramienta":  SYSTEM_NAME,
            "version":      VERSION,
            "autor":        DEVELOPER,
            "sistema":      SO,
            "plataforma":   platform.platform(),
            "fecha":        now.strftime("%Y-%m-%d"),
            "hora":         now.strftime("%H:%M:%S"),
            "timestamp":    now.isoformat(),
        },
        "hardware":   {},
        "discos":     [],
        "usuarios":   [],
        "puertos":    [],
        "software":   [],
        "eventos":    [],
    }

    if SO == "Linux":
        # Hardware
        data["hardware"] = {
            "cpu":    run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(),
            "serial": run("sudo dmidecode -s system-serial-number 2>/dev/null").strip() or "N/A",
            "ram":    run("free -h | grep Mem | awk '{print $3\"/\"$2}'"),
            "uptime": run("uptime -p"),
            "kernel": run("uname -r"),
            "distro": run("grep '^PRETTY_NAME=' /etc/os-release | cut -d'=' -f2 | tr -d '\"'"),
        }
        # Temperatura
        s_out = run("sensors 2>/dev/null")
        m = re.search(r"(?:Package id 0|temp1|Core 0):\s+[+\-]?(\d+\.\d+)", s_out)
        data["hardware"]["temperatura_cpu"] = f"{m.group(1)}°C" if m else "N/A"

        # Discos
        for line in run("df -h | grep '^/dev'").splitlines():
            parts = line.split()
            if len(parts) >= 6:
                data["discos"].append({
                    "dispositivo": parts[0], "tamanio": parts[1],
                    "usado": parts[2], "libre": parts[3],
                    "uso_pct": parts[4], "montaje": parts[5]
                })

        # Usuarios
        for line in run("cat /etc/passwd | grep -E '/bin/bash|/bin/sh'").splitlines():
            p = line.split(":")
            if len(p) >= 7:
                data["usuarios"].append({
                    "usuario": p[0], "uid": p[2], "gid": p[3],
                    "home": p[5], "shell": p[6]
                })

        # Puertos
        for line in run("sudo ss -tunlp | grep LISTEN").splitlines():
            data["puertos"].append({"entrada": line.strip()})

        # Software
        pkg_mgr = "APT" if shutil.which("apt") else "DNF" if shutil.which("dnf") else "PACMAN"
        if pkg_mgr == "APT":
            raw = run("dpkg -l | grep '^ii' | awk '{print $2\"|\"$3\"|\"$4}'")
        elif pkg_mgr == "DNF":
            raw = run("rpm -qa --qf '%{NAME}|%{VERSION}|%{VENDOR}\n'")
        else:
            raw = run("pacman -Q | awk '{print $1\"|\"$2\"|---\"}'")
        for line in raw.splitlines()[:200]:
            p = (line + "||").split("|")
            data["software"].append({"nombre": p[0], "version": p[1], "origen": p[2]})

        # Eventos
        raw_ev = run("sudo journalctl -p err -n 30 --no-pager --output=short 2>/dev/null")
        for line in raw_ev.splitlines():
            if line.strip():
                data["eventos"].append({"entrada": line.strip()})

    else:
        # Windows
        def ps(cmd):
            return Windows._ps(cmd)

        data["hardware"] = {
            "cpu":    ps("(Get-CimInstance Win32_Processor).Name.Trim()"),
            "serial": ps("(Get-CimInstance Win32_BIOS).SerialNumber.Trim()"),
            "ram":    ps("$r=Get-CimInstance Win32_OperatingSystem;[math]::Round(($r.TotalVisibleMemorySize-$r.FreePhysicalMemory)/1MB,2).ToString()+' / '+[math]::Round($r.TotalVisibleMemorySize/1MB,2).ToString()+' GB'"),
            "uptime": ps("$r=Get-CimInstance Win32_OperatingSystem;$u=(Get-Date)-$r.LastBootUpTime;'{0}d {1}h {2}m' -f $u.Days,$u.Hours,$u.Minutes"),
            "os":     ps("(Get-CimInstance Win32_OperatingSystem).Caption"),
            "temperatura_cpu": "Ver OpenHardwareMonitor",
        }

        # Discos
        disk_json = ps(
            "Get-PSDrive -PSProvider FileSystem | Where-Object {$_.Used -gt 0} | "
            "Select-Object Name,"
            "@{N='Usado';E={[math]::Round($_.Used/1GB,2)}},"
            "@{N='Libre';E={[math]::Round($_.Free/1GB,2)}},"
            "@{N='Total';E={[math]::Round(($_.Used+$_.Free)/1GB,2)}},"
            "@{N='Pct';E={[math]::Round($_.Used/($_.Used+$_.Free)*100,1)}} | ConvertTo-Json"
        )
        try:
            dl = json.loads(disk_json)
            if isinstance(dl, dict): dl = [dl]
            for d in dl:
                data["discos"].append({
                    "unidad": d.get("Name",""), "usado_gb": d.get("Usado",""),
                    "libre_gb": d.get("Libre",""), "total_gb": d.get("Total",""),
                    "uso_pct": f"{d.get('Pct','')}%"
                })
        except Exception:
            pass

        # Usuarios
        user_json = ps("Get-LocalUser | Select-Object Name,Enabled,LastLogon | ConvertTo-Json")
        try:
            ul = json.loads(user_json)
            if isinstance(ul, dict): ul = [ul]
            for u in ul:
                data["usuarios"].append({
                    "usuario": u.get("Name",""),
                    "activo":  str(u.get("Enabled","")),
                    "ultimo_login": str(u.get("LastLogon",""))
                })
        except Exception:
            pass

        # Puertos
        port_json = ps(
            "Get-NetTCPConnection -State Listen -EA SilentlyContinue | "
            "Select-Object LocalAddress,LocalPort,"
            "@{N='Proceso';E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).Name}} | "
            "ConvertTo-Json"
        )
        try:
            pl = json.loads(port_json)
            if isinstance(pl, dict): pl = [pl]
            for p in pl:
                data["puertos"].append({
                    "direccion": p.get("LocalAddress",""),
                    "puerto":    p.get("LocalPort",""),
                    "proceso":   p.get("Proceso","")
                })
        except Exception:
            pass

        # Software
        sw_json = ps(
            "$paths=@('HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
            "'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',"
            "'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*');"
            "$paths | ForEach-Object {Get-ItemProperty $_ -EA SilentlyContinue} | "
            "Where-Object {$_.DisplayName} | Sort-Object DisplayName | "
            "Select-Object -First 200 DisplayName,DisplayVersion,Publisher | ConvertTo-Json"
        )
        try:
            sl = json.loads(sw_json)
            if isinstance(sl, dict): sl = [sl]
            for s in sl:
                data["software"].append({
                    "nombre":   s.get("DisplayName",""),
                    "version":  s.get("DisplayVersion",""),
                    "origen":   s.get("Publisher","")
                })
        except Exception:
            pass

        # Eventos
        ev_raw = ps(
            "try{Get-WinEvent -FilterHashtable @{LogName='System';Level=@(1,2);"
            "StartTime=(Get-Date).AddDays(-1)} -MaxEvents 30 -EA Stop | "
            "Select-Object TimeCreated,Id,Message | ConvertTo-Json}catch{'[]'}"
        )
        try:
            el = json.loads(ev_raw)
            if isinstance(el, dict): el = [el]
            for e in el:
                msg = str(e.get("Message","")).split("\n")[0][:120]
                data["eventos"].append({
                    "fecha": str(e.get("TimeCreated","")),
                    "id":    str(e.get("Id","")),
                    "msg":   msg
                })
        except Exception:
            pass

    cprint(f"  Datos recopilados: hardware, {len(data['discos'])} discos, "
           f"{len(data['usuarios'])} usuarios, {len(data['puertos'])} puertos, "
           f"{len(data['software'])} programas, {len(data['eventos'])} eventos.", C.GREEN)
    return data


# ── Exportadores individuales ────────────────────────────────

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
                tag = re.sub(r'[^a-zA-Z0-9_]', '_', str(k))
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
    """Exporta cada sección como un CSV separado."""
    import csv
    archivos = []
    secciones = {
        "hardware":  [data["hardware"]],
        "discos":    data["discos"],
        "usuarios":  data["usuarios"],
        "puertos":   data["puertos"],
        "software":  data["software"],
        "eventos":   data["eventos"],
    }
    for nombre, filas in secciones.items():
        if not filas:
            continue
        filepath = base_path.replace(".csv", f"_{nombre}.csv")
        keys = list(filas[0].keys()) if filas else []
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(filas)
        archivos.append(filepath)
    return archivos

def export_pdf(data, path):
    """Genera PDF profesional con reportlab."""
    import sys as _sys
    import os as _os

    # Forzar que reportlab use PIL del venv y no del sistema
    _script_dir = _os.path.dirname(_os.path.abspath(__file__))
    _venv_site  = _os.path.join(_script_dir, ".venv", "lib")
    if _os.path.exists(_venv_site):
        for _d in _os.listdir(_venv_site):
            _sp = _os.path.join(_venv_site, _d, "site-packages")
            if _os.path.exists(_sp) and _sp not in _sys.path:
                _sys.path.insert(0, _sp)

    # Eliminar PIL del sistema del cache de modulos para forzar recarga desde venv
    for _mod in list(_sys.modules.keys()):
        if _mod == "PIL" or _mod.startswith("PIL."):
            del _sys.modules[_mod]

    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable, PageBreak)

    doc  = SimpleDocTemplate(path, pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Estilos personalizados mejorados
    titulo_style = ParagraphStyle("titulo",
        fontSize=36, textColor=colors.HexColor("#00ff88"),
        spaceBefore=30, spaceAfter=8,
        fontName="Helvetica-Bold", alignment=1,
        leading=42)
    sub_style = ParagraphStyle("sub",
        fontSize=11, textColor=colors.HexColor("#58a6ff"),
        spaceBefore=6, spaceAfter=16,
        alignment=1, leading=16)
    autor_style = ParagraphStyle("autor",
        fontSize=9, textColor=colors.HexColor("#8b949e"),
        spaceAfter=20, alignment=1)
    h2_style = ParagraphStyle("h2",
        fontSize=12, textColor=colors.HexColor("#00ff88"),
        spaceBefore=16, spaceAfter=8,
        fontName="Helvetica-Bold", leading=16)
    body_style = ParagraphStyle("body",
        fontSize=8.5, textColor=colors.HexColor("#c9d1d9"),
        spaceAfter=4, fontName="Helvetica", leading=12)
    label_style = ParagraphStyle("label",
        fontSize=8, textColor=colors.HexColor("#8b949e"),
        fontName="Helvetica-Bold")

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
        for i, row in enumerate(rows):
            table_data.append([
                Paragraph(str(cell)[:120], ParagraphStyle("td",
                    fontSize=7.5, textColor=COLOR_TEXT, fontName="Helvetica"))
                for cell in row
            ])
        if col_widths is None:
            avail = 17*cm
            col_widths = [avail / len(headers)] * len(headers)
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        style = TableStyle([
            ("BACKGROUND",  (0,0), (-1,0),  COLOR_HEADER),
            ("BACKGROUND",  (0,1), (-1,-1), COLOR_BG),
            ("GRID",        (0,0), (-1,-1), 0.4, COLOR_BORDER),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [COLOR_BG, COLOR_ROW_ALT]),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
        ])
        t.setStyle(style)
        return t

    story = []

    # ── Portada ──────────────────────────────────────────────
    story.append(Spacer(1, 3.5*cm))

    # Linea decorativa superior
    story.append(HRFlowable(width="80%", color=colors.HexColor("#00ff88"),
                            thickness=2, hAlign="CENTER", spaceAfter=20))

    # Titulo principal
    story.append(Paragraph("NEUROAUDIT", titulo_style))

    # Subtitulo
    story.append(Spacer(1, 0.4*cm))
    story.append(Paragraph(
        f"System Audit Report &nbsp;&nbsp;|&nbsp;&nbsp; v{VERSION} &nbsp;&nbsp;|&nbsp;&nbsp; {data['meta']['sistema']}",
        sub_style))

    # Fecha y autor
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"{data['meta']['fecha']} &nbsp;&nbsp;{data['meta']['hora']} &nbsp;&nbsp;|&nbsp;&nbsp; {data['meta']['autor']}",
        autor_style))

    story.append(Spacer(1, 0.8*cm))

    # Linea decorativa inferior
    story.append(HRFlowable(width="80%", color=colors.HexColor("#00ff88"),
                            thickness=2, hAlign="CENTER", spaceAfter=30))

    story.append(Spacer(1, 0.6*cm))

    meta_rows = [
        ["Fecha",      data["meta"]["fecha"]],
        ["Hora",       data["meta"]["hora"]],
        ["Sistema",    data["meta"]["sistema"]],
        ["Plataforma", data["meta"]["plataforma"]],
        ["Autor",      data["meta"]["autor"]],
        ["Version",    data["meta"]["version"]],
    ]
    story.append(make_table(["Campo", "Valor"], meta_rows, [5*cm, 12*cm]))
    story.append(PageBreak())

    # ── Hardware ─────────────────────────────────────────────
    story.append(Paragraph("Hardware e Infraestructura", h2_style))
    hw = data["hardware"]
    hw_rows = [[k.replace("_"," ").title(), str(v)] for k, v in hw.items()]
    story.append(make_table(["Componente", "Valor"], hw_rows, [5*cm, 12*cm]))
    story.append(Spacer(1, 0.4*cm))

    # ── Discos ───────────────────────────────────────────────
    if data["discos"]:
        story.append(Paragraph("Discos y Particiones", h2_style))
        keys = list(data["discos"][0].keys())
        rows = [[str(d.get(k,"")) for k in keys] for d in data["discos"]]
        story.append(make_table([k.replace("_"," ").title() for k in keys], rows))
        story.append(Spacer(1, 0.4*cm))

    # ── Usuarios ─────────────────────────────────────────────
    if data["usuarios"]:
        story.append(Paragraph("Usuarios del Sistema", h2_style))
        keys = list(data["usuarios"][0].keys())
        rows = [[str(u.get(k,"")) for k in keys] for u in data["usuarios"]]
        story.append(make_table([k.replace("_"," ").title() for k in keys], rows))
        story.append(Spacer(1, 0.4*cm))

    # ── Puertos ──────────────────────────────────────────────
    if data["puertos"]:
        story.append(Paragraph("Puertos y Conexiones", h2_style))
        keys = list(data["puertos"][0].keys())
        rows = [[str(p.get(k,"")) for k in keys] for p in data["puertos"]]
        story.append(make_table([k.replace("_"," ").title() for k in keys], rows))
        story.append(PageBreak())

    # ── Software ─────────────────────────────────────────────
    if data["software"]:
        story.append(Paragraph(f"Software Instalado ({len(data['software'])} programas)", h2_style))
        keys = list(data["software"][0].keys())
        rows = [[str(s.get(k,""))[:80] for k in keys] for s in data["software"][:150]]
        story.append(make_table([k.replace("_"," ").title() for k in keys], rows))
        story.append(PageBreak())

    # ── Eventos ──────────────────────────────────────────────
    if data["eventos"]:
        story.append(Paragraph("Eventos del Sistema", h2_style))
        keys = list(data["eventos"][0].keys())
        rows = [[str(e.get(k,""))[:100] for k in keys] for e in data["eventos"]]
        story.append(make_table([k.replace("_"," ").title() for k in keys], rows))

    # ── Footer via canvas ────────────────────────────────────
    def add_footer(canvas_obj, doc_obj):
        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(colors.HexColor("#484f58"))
        canvas_obj.setFillColorRGB(0.28, 0.31, 0.34)
        footer_txt = (f"NEUROAUDIT v{VERSION}  |  {DEVELOPER}  |  "
                      f"Generado: {data['meta']['fecha']} {data['meta']['hora']}  |  "
                      f"Pagina {doc_obj.page}")
        canvas_obj.drawCentredString(A4[0]/2, 1.2*cm, footer_txt)
        canvas_obj.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

def export_html_full(data, path):
    """Versión mejorada del reporte HTML usando datos estructurados."""
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

    hw = data["hardware"]
    hw_cards = "".join(
        f'<div class="info-item"><div class="label">{k.replace("_"," ").upper()}</div>'
        f'<div class="value">{html_escape(str(v))}</div></div>'
        for k, v in hw.items()
    )

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>NEUROAUDIT Report - {data['meta']['fecha']}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0d1117;color:#c9d1d9;font-family:Consolas,monospace;padding:24px}}
  h1{{color:#00ff88;text-align:center;font-size:2.2em;letter-spacing:5px;padding:24px 0 6px}}
  .subtitle{{text-align:center;color:#58a6ff;margin-bottom:24px;font-size:.9em}}
  .badge{{display:inline-block;background:#161b22;border:1px solid #30363d;border-radius:6px;
          padding:4px 14px;margin:4px;font-size:.8em;color:#8b949e}}
  .card{{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:22px;margin:22px 0}}
  .card h2{{color:#00ff88;border-bottom:1px solid #30363d;padding-bottom:8px;
            margin-bottom:16px;font-size:1em;letter-spacing:2px}}
  table{{width:100%;border-collapse:collapse;font-size:.82em}}
  th{{background:#21262d;color:#58a6ff;padding:9px;text-align:left;border-bottom:2px solid #30363d}}
  td{{padding:6px 9px;border-bottom:1px solid #21262d;word-break:break-word}}
  tr:nth-child(even) td{{background:#1c2128}}
  tr:hover td{{background:#21262d}}
  .info-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}}
  .info-item{{background:#21262d;border-radius:8px;padding:14px}}
  .info-item .label{{color:#8b949e;font-size:.72em;text-transform:uppercase;letter-spacing:1px}}
  .info-item .value{{color:#e6edf3;font-size:.92em;margin-top:5px}}
  .footer{{text-align:center;color:#484f58;font-size:.75em;margin-top:32px;
           padding-top:16px;border-top:1px solid #21262d}}
  .tag{{font-weight:bold}}
  .tag-linux{{color:#2ecc71}}.tag-win{{color:#58a6ff}}
</style>
</head>
<body>
<h1>NEUROAUDIT</h1>
<div class="subtitle">
  System Audit Report &nbsp;|&nbsp; v{VERSION} &nbsp;|&nbsp;
  <span class="tag {'tag-linux' if data['meta']['sistema']=='Linux' else 'tag-win'}">{data['meta']['sistema'].upper()}</span>
  &nbsp;|&nbsp; {data['meta']['fecha']} {data['meta']['hora']}
</div>
<div style="text-align:center;margin-bottom:22px">
  <span class="badge">Plataforma: {html_escape(data['meta']['plataforma'])}</span>
  <span class="badge">Autor: {DEVELOPER}</span>
</div>

<div class="card">
  <h2>HARDWARE E INFRAESTRUCTURA</h2>
  <div class="info-grid">{hw_cards}</div>
</div>

<div class="card">
  <h2>DISCOS Y PARTICIONES ({len(data['discos'])} unidades)</h2>
  <table><thead>{thead(data['discos'])}</thead><tbody>{rows_html(data['discos'])}</tbody></table>
</div>

<div class="card">
  <h2>USUARIOS DEL SISTEMA ({len(data['usuarios'])} usuarios)</h2>
  <table><thead>{thead(data['usuarios'])}</thead><tbody>{rows_html(data['usuarios'])}</tbody></table>
</div>

<div class="card">
  <h2>PUERTOS EN ESCUCHA ({len(data['puertos'])} puertos)</h2>
  <table><thead>{thead(data['puertos'])}</thead><tbody>{rows_html(data['puertos'])}</tbody></table>
</div>

<div class="card">
  <h2>SOFTWARE INSTALADO ({len(data['software'])} programas)</h2>
  <table><thead>{thead(data['software'])}</thead><tbody>{rows_html(data['software'])}</tbody></table>
</div>

<div class="card">
  <h2>EVENTOS DEL SISTEMA ({len(data['eventos'])} eventos)</h2>
  <table><thead>{thead(data['eventos'])}</thead><tbody>{rows_html(data['eventos'])}</tbody></table>
</div>

<div class="footer">
  NEUROAUDIT v{VERSION} &nbsp;|&nbsp; {DEVELOPER} &nbsp;|&nbsp;
  Generado: {data['meta']['fecha']} {data['meta']['hora']}
</div>
</body></html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def run_export():
    """Menú interactivo de exportación multi-formato."""
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
    data = collect_report_data()

    now    = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    so_tag = "linux" if SO == "Linux" else "windows"

    # Ruta de guardado clara y correcta por plataforma
    if SO == "Windows":
        default_dir = os.path.join(os.environ.get("USERPROFILE", os.path.expanduser("~")), "Desktop", "NEUROAUDIT_Reportes")
    else:
        default_dir = os.path.join(_get_real_home(), "NEUROAUDIT_Reportes")

    cprint(f"\n  Carpeta de destino: {C.CYAN}{default_dir}{C.RESET}")
    resp = input(f"  {C.CYAN}Usar esta carpeta? (S/N - N para elegir otra): {C.RESET}").strip().lower()
    if resp == "n":
        nueva = input(f"  {C.CYAN}Ingresa la ruta completa de la carpeta: {C.RESET}").strip()
        if nueva and os.path.isabs(nueva):
            rep_dir = nueva
        else:
            cprint("  Ruta invalida, usando carpeta por defecto.", C.YELLOW)
            rep_dir = default_dir
    else:
        rep_dir = default_dir

    try:
        os.makedirs(rep_dir, exist_ok=True)
    except Exception as e:
        cprint(f"  Error creando carpeta: {e}", C.RED)
        rep_dir = os.path.expanduser("~")
        cprint(f"  Usando carpeta home: {rep_dir}", C.YELLOW)

    base = os.path.join(rep_dir, f"reporte_{so_tag}_{now}")
    cprint(f"  Guardando en: {C.CYAN}{rep_dir}{C.RESET}\n")

    seleccion = list(formatos.keys())[:-1] if opcion == "7" else [opcion]
    generados = []

    for sel in seleccion:
        nombre = formatos[sel][0]
        cprint(f"\n  Generando {nombre}...", C.YELLOW)
        try:
            if sel == "1":
                p = base + ".json";  export_json(data, p);      generados.append(p)
            elif sel == "2":
                p = base + ".yaml";  export_yaml(data, p);      generados.append(p)
            elif sel == "3":
                p = base + ".xml";   export_xml(data, p);       generados.append(p)
            elif sel == "4":
                ps = export_csv(data, base + ".csv");            generados.extend(ps)
            elif sel == "5":
                p = base + ".pdf";   export_pdf(data, p);       generados.append(p)
            elif sel == "6":
                p = base + ".html";  export_html_full(data, p); generados.append(p)
            cprint(f"  {nombre} OK", C.GREEN)
        except Exception as e:
            cprint(f"  Error generando {nombre}: {e}", C.RED)

    print()
    cprint("  ─── Archivos generados ───────────────────────────────", C.CYAN)
    if generados:
        for g in generados:
            cprint(f"  ✓  {g}", C.GREEN)
        print()
        cprint(f"  Carpeta: {rep_dir}", C.CYAN)
    else:
        cprint("  No se genero ningun archivo.", C.RED)
        cprint(f"\n  Tip: instalar dependencias manualmente:", C.YELLOW)
        cprint(f"  sudo pip install reportlab pyyaml --break-system-packages", C.GRAY)

    # Abrir carpeta de reportes
    try:
        if SO == "Windows":
            os.startfile(rep_dir)
        else:
            # Abrir como usuario real (no root) para evitar errores de D-Bus
            sudo_user = os.environ.get("SUDO_USER")
            if sudo_user and sudo_user != "root":
                subprocess.Popen(["sudo", "-u", sudo_user, "xdg-open", rep_dir],
                                 env={**os.environ, "DISPLAY": os.environ.get("DISPLAY", ":0"),
                                      "DBUS_SESSION_BUS_ADDRESS": os.environ.get("DBUS_SESSION_BUS_ADDRESS", "")})
            else:
                subprocess.Popen(["xdg-open", rep_dir])
    except Exception:
        pass


# ── Reemplaza export_html en ambas clases ────────────────────
Linux.export_html   = staticmethod(lambda: run_export())
Windows.export_html = staticmethod(lambda: run_export())


# ════════════════════════════════════════════════════════════
#  MODULO 10: AUDITORIA DE PERMISOS Y USUARIOS
# ════════════════════════════════════════════════════════════

def perm_alert(msg):
    cprint(f"  ⚠  RIESGO  : {msg}", C.RED)

def perm_ok(msg):
    cprint(f"  OK         : {msg}", C.GREEN)

def perm_info(msg):
    cprint(f"  INFO       : {msg}", C.YELLOW)


def audit_permissions_linux():
    section("AUDITORIA DE PERMISOS Y USUARIOS [LINUX]")

    # ── 1: Usuario actual y privilegios ──────────────────────
    cprint("\n  [ Usuario Actual ]", C.YELLOW)
    whoami    = run("whoami").strip()
    uid       = run("id -u").strip()
    groups    = run("id -Gn").strip()
    is_root   = (uid == "0")

    print(f"  Usuario  : {C.CYAN}{whoami}{C.RESET}")
    print(f"  UID      : {uid}")
    print(f"  Grupos   : {groups}")

    if is_root:
        perm_alert("Corriendo como ROOT. Evitar uso cotidiano con root.")
    else:
        perm_ok("No es root — usuario con privilegios normales.")

    if "sudo" in groups or "wheel" in groups:
        perm_alert(f"{whoami} tiene acceso SUDO — puede escalar privilegios.")
    else:
        perm_ok(f"{whoami} no tiene acceso sudo directo.")

    # ── 2: Usuarios con privilegios elevados ─────────────────
    cprint("\n  [ Usuarios con Privilegios Elevados ]", C.YELLOW)

    # Usuarios en sudo/wheel/admin
    for grp in ["sudo", "wheel", "admin"]:
        members = run(f"getent group {grp} 2>/dev/null | cut -d: -f4").strip()
        if members:
            cprint(f"  Grupo {grp:<8}: {members}", C.RESET)
            count = len([m for m in members.split(",") if m.strip()])
            if count > 2:
                perm_alert(f"El grupo '{grp}' tiene {count} miembros. Revisar si todos son necesarios.")
        else:
            cprint(f"  Grupo {grp:<8}: (vacio o no existe)", C.GRAY)

    # Usuarios UID 0 (equivalentes a root)
    uid0 = run("awk -F: '$3==0{print $1}' /etc/passwd").strip()
    if uid0:
        users_uid0 = [u for u in uid0.splitlines() if u.strip()]
        if len(users_uid0) > 1:
            perm_alert(f"Multiples usuarios con UID 0: {', '.join(users_uid0)}")
        else:
            perm_ok(f"Solo un usuario con UID 0: {users_uid0[0]}")

    # ── 3: Listado completo de usuarios y grupos ─────────────
    cprint("\n  [ Listado de Usuarios del Sistema ]", C.YELLOW)
    cprint(f"  {'USUARIO':<20} {'UID':<8} {'GID':<8} {'SHELL':<20} {'HOME'}", C.CYAN)
    cprint(f"  {'-'*75}", C.GRAY)

    passwd_lines = run("getent passwd | sort -t: -k3 -n").splitlines()
    for line in passwd_lines:
        p = line.split(":")
        if len(p) < 7:
            continue
        user, uid_v, gid, _, home, shell = p[0], p[2], p[3], p[4], p[5], p[6].strip()
        uid_int = int(uid_v) if uid_v.isdigit() else 9999

        # Filtrar solo usuarios reales (UID >= 1000) o root
        if uid_int == 0 or uid_int >= 1000:
            color = C.GREEN if uid_int >= 1000 else C.RED
            cprint(f"  {user:<20} {uid_v:<8} {gid:<8} {shell:<20} {home}", color)

            # Alertas por shell
            if shell in ["/bin/bash", "/bin/sh", "/bin/zsh"] and uid_int > 0:
                grps = run(f"groups {user} 2>/dev/null").replace(f"{user} : ", "")
                if "sudo" in grps or "wheel" in grps:
                    perm_alert(f"'{user}' tiene shell interactiva Y permisos sudo.")

    # ── 4: Permisos en carpetas criticas ─────────────────────
    cprint("\n  [ Permisos en Carpetas Criticas ]", C.YELLOW)
    cprint(f"  {'RUTA':<35} {'PERMISOS':<12} {'PROPIETARIO':<15} {'ESTADO'}", C.CYAN)
    cprint(f"  {'-'*75}", C.GRAY)

    rutas_criticas = [
        ("/etc/passwd",       "644", False),
        ("/etc/shadow",       "640", False),
        ("/etc/sudoers",      "440", False),
        ("/etc/ssh/sshd_config", "600", False),
        ("/tmp",              "1777", True),
        ("/var/log",          "755", True),
        ("/root",             "700", True),
        ("/home",             "755", True),
        ("/etc/cron.d",       "755", True),
        ("/usr/bin/passwd",   "4755", False),
    ]

    for ruta, perm_esperado, es_dir in rutas_criticas:
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
                    perm_alert(f"{ruta} tiene permisos incorrectos — riesgo de seguridad alto.")

    # ── 5: Archivos SUID/SGID sospechosos ────────────────────
    cprint("\n  [ Archivos SUID/SGID (fuera de /usr y /bin) ]", C.YELLOW)
    suid = run("find / -perm /6000 -type f 2>/dev/null | grep -Ev '^/usr|^/bin|^/sbin|^/lib' | head -20")
    if suid.strip():
        for line in suid.splitlines():
            perm_alert(f"SUID/SGID inusual: {line.strip()}")
    else:
        perm_ok("No se encontraron archivos SUID/SGID fuera de rutas estandar.")

    # ── 6: Politica de contraseñas ───────────────────────────
    cprint("\n  [ Politica de Contrasenas ]", C.YELLOW)

    # /etc/login.defs
    pass_max = run("grep '^PASS_MAX_DAYS' /etc/login.defs 2>/dev/null | awk '{print $2}'").strip()
    pass_min = run("grep '^PASS_MIN_DAYS' /etc/login.defs 2>/dev/null | awk '{print $2}'").strip()
    pass_len = run("grep '^PASS_MIN_LEN'  /etc/login.defs 2>/dev/null | awk '{print $2}'").strip()
    pass_warn= run("grep '^PASS_WARN_AGE' /etc/login.defs 2>/dev/null | awk '{print $2}'").strip()

    print(f"  PASS_MAX_DAYS  : {pass_max or 'No definido'}")
    print(f"  PASS_MIN_DAYS  : {pass_min or 'No definido'}")
    print(f"  PASS_MIN_LEN   : {pass_len or 'No definido'}")
    print(f"  PASS_WARN_AGE  : {pass_warn or 'No definido'}")

    try:
        if int(pass_max or 99999) > 90:
            perm_alert("PASS_MAX_DAYS > 90 dias. Se recomienda maximo 90.")
        else:
            perm_ok(f"PASS_MAX_DAYS = {pass_max} dias (correcto).")
        if int(pass_len or 0) < 8:
            perm_alert("PASS_MIN_LEN < 8. Se recomienda minimo 8 caracteres.")
        else:
            perm_ok(f"PASS_MIN_LEN = {pass_len} (correcto).")
    except ValueError:
        pass

    # Usuarios sin contraseña
    cprint("\n  [ Usuarios sin Contrasena ]", C.YELLOW)
    no_pass = run("sudo awk -F: '($2==\"\" || $2==\"!\"){print $1}' /etc/shadow 2>/dev/null")
    if no_pass.strip():
        for u in no_pass.splitlines():
            perm_alert(f"Usuario sin contrasena: {u.strip()}")
    else:
        perm_ok("Todos los usuarios tienen contrasena configurada.")

    # Usuarios con contrasena expirada
    cprint("\n  [ Contrasenas Expiradas ]", C.YELLOW)
    expired = run("sudo awk -F: 'NR>1 && $5!=\"\" && $5<(systime()/86400){print $1}' /etc/shadow 2>/dev/null | head -10")
    if expired.strip():
        for u in expired.splitlines():
            perm_alert(f"Contrasena expirada: {u.strip()}")
    else:
        perm_ok("No se detectaron contrasenas expiradas.")

    # ── 7: Limpiador de temporales ───────────────────────────
    cprint("\n  [ Limpiador de Temporales ]", C.YELLOW)
    tmp_paths = ["/tmp", "/var/tmp"]
    total_size = 0
    for p in tmp_paths:
        if os.path.exists(p):
            size_raw = run(f"du -sb {p} 2>/dev/null | cut -f1").strip()
            try:
                size = int(size_raw)
                total_size += size
                size_mb = size / 1024 / 1024
                color = C.RED if size_mb > 500 else C.YELLOW if size_mb > 100 else C.GREEN
                cprint(f"  {p:<20} {size_mb:.1f} MB", color)
                if size_mb > 500:
                    perm_alert(f"{p} supera 500 MB — considerar limpieza.")
            except ValueError:
                pass

    total_mb = total_size / 1024 / 1024
    print(f"\n  Total temporales: {C.CYAN}{total_mb:.1f} MB{C.RESET}")
    if total_mb > 100:
        resp = input(f"\n  {C.CYAN}Limpiar archivos temporales de mas de 2 dias? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            for p in tmp_paths:
                os.system(f"find {p} -type f -atime +2 -delete 2>/dev/null")
                os.system(f"find {p} -type d -empty -delete 2>/dev/null")
            perm_ok("Temporales limpiados correctamente.")
    else:
        perm_ok("Temporales dentro de limites normales.")


def audit_permissions_windows():
    section("AUDITORIA DE PERMISOS Y USUARIOS [WINDOWS]")

    def ps(cmd):
        return Windows._ps(cmd)

    # ── 1: Usuario actual ────────────────────────────────────
    cprint("\n  [ Usuario Actual ]", C.YELLOW)
    whoami   = run("whoami").strip()
    is_admin = check_privileges()

    print(f"  Usuario  : {C.CYAN}{whoami}{C.RESET}")
    if is_admin:
        perm_alert("Corriendo como Administrador. Usar cuenta estandar para tareas cotidianas.")
    else:
        perm_ok("Usuario estandar — sin privilegios elevados activos.")

    # ── 2: Usuarios locales y grupos ─────────────────────────
    cprint("\n  [ Usuarios Locales ]", C.YELLOW)
    users = ps(
        "Get-LocalUser | Select-Object Name,Enabled,LastLogon,PasswordLastSet,"
        "PasswordNeverExpires,PasswordRequired | Format-Table -AutoSize | Out-String"
    )
    print(users)

    # Usuarios con password que nunca expira
    never_exp = ps(
        "Get-LocalUser | Where-Object {$_.PasswordNeverExpires -eq $true -and $_.Enabled} | "
        "Select-Object -ExpandProperty Name"
    )
    if never_exp.strip():
        for u in never_exp.strip().splitlines():
            if u.strip():
                perm_alert(f"'{u.strip()}' tiene contrasena que NUNCA expira.")
    else:
        perm_ok("Ningun usuario activo con contrasena que nunca expira.")

    # Usuarios sin password
    no_pass = ps(
        "Get-LocalUser | Where-Object {$_.PasswordRequired -eq $false -and $_.Enabled} | "
        "Select-Object -ExpandProperty Name"
    )
    if no_pass.strip():
        for u in no_pass.strip().splitlines():
            if u.strip():
                perm_alert(f"'{u.strip()}' NO requiere contrasena.")
    else:
        perm_ok("Todos los usuarios activos requieren contrasena.")

    # ── 3: Miembros del grupo Administradores ────────────────
    cprint("\n  [ Miembros del Grupo Administradores ]", C.YELLOW)
    admins = ps(
        "Get-LocalGroupMember -Group 'Administrators' -EA SilentlyContinue | "
        "Select-Object Name,PrincipalSource | Format-Table -AutoSize | Out-String"
    )
    print(admins)
    admin_count = len([l for l in admins.splitlines() if l.strip() and "---" not in l and "Name" not in l])
    if admin_count > 2:
        perm_alert(f"Hay {admin_count} administradores locales. Revisar si todos son necesarios.")
    else:
        perm_ok(f"Cantidad de administradores: {admin_count} (aceptable).")

    # ── 4: Permisos en carpetas criticas ─────────────────────
    cprint("\n  [ Permisos en Carpetas Criticas ]", C.YELLOW)
    rutas = [
        r"C:\Windows\System32",
        r"C:\Windows\SysWOW64",
        r"C:\Program Files",
        r"C:\Users",
        os.environ.get("TEMP", r"C:\Temp"),
        r"C:\Windows\Temp",
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            acl = ps(
                f"try{{(Get-Acl '{ruta}').Access | "
                f"Where-Object {{$_.IdentityReference -notlike '*SYSTEM*' -and "
                f"$_.IdentityReference -notlike '*Administrators*' -and "
                f"$_.FileSystemRights -like '*Write*'}} | "
                f"Select-Object IdentityReference,FileSystemRights | "
                f"Format-Table -AutoSize | Out-String}}catch{{'N/A'}}"
            )
            if acl.strip() and acl.strip() != "N/A" and len(acl.strip()) > 10:
                perm_alert(f"Escritura no estandar en {ruta}")
                print(f"  {acl.strip()[:200]}")
            else:
                perm_ok(f"Permisos correctos: {ruta}")
        else:
            cprint(f"  {ruta:<40} No existe", C.GRAY)

    # ── 5: Politica de contrasenas ───────────────────────────
    cprint("\n  [ Politica de Contrasenas ]", C.YELLOW)
    policy = ps("net accounts 2>&1 | Out-String")
    print(policy)

    max_age = re.search(r"Maximum password age.*?(\d+)", policy)
    min_len = re.search(r"Minimum password length.*?(\d+)", policy)
    if max_age:
        days = int(max_age.group(1))
        if days > 90 or days == 0:
            perm_alert(f"Contrasena maxima: {days} dias. Recomendado: 90 o menos.")
        else:
            perm_ok(f"Expiracion de contrasena: {days} dias (correcto).")
    if min_len:
        length = int(min_len.group(1))
        if length < 8:
            perm_alert(f"Longitud minima de contrasena: {length}. Recomendado: 8 o mas.")
        else:
            perm_ok(f"Longitud minima: {length} caracteres (correcto).")

    # ── 6: Limpiador de temporales ───────────────────────────
    cprint("\n  [ Limpiador de Temporales ]", C.YELLOW)
    tmp_paths = [
        os.environ.get("TEMP", ""),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Temp"),
        os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "Prefetch"),
    ]
    total = 0
    for p in tmp_paths:
        if p and os.path.exists(p):
            size = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, _, files in os.walk(p)
                for f in files
                if os.path.exists(os.path.join(dp, f))
            )
            total += size
            size_mb = size / 1024 / 1024
            color = C.RED if size_mb > 500 else C.YELLOW if size_mb > 100 else C.GREEN
            cprint(f"  {p:<50} {size_mb:.1f} MB", color)
            if size_mb > 500:
                perm_alert(f"Carpeta supera 500 MB: {p}")

    total_mb = total / 1024 / 1024
    print(f"\n  Total temporales: {C.CYAN}{total_mb:.1f} MB{C.RESET}")
    if total_mb > 100:
        resp = input(f"\n  {C.CYAN}Limpiar archivos temporales ahora? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            limpiado = 0
            for p in tmp_paths:
                if p and os.path.exists(p):
                    for dp, dirs, files in os.walk(p):
                        for f in files:
                            try:
                                fp = os.path.join(dp, f)
                                limpiado += os.path.getsize(fp)
                                os.remove(fp)
                            except Exception:
                                pass
            perm_ok(f"Limpiados {limpiado/1024/1024:.1f} MB de temporales.")
    else:
        perm_ok("Temporales dentro de limites normales.")


def run_permission_audit():
    if SO == "Linux":
        audit_permissions_linux()
    else:
        audit_permissions_windows()





def html_escape(text):
    return str(text).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def check_privileges():
    """Verifica si el script corre con privilegios de administrador/root."""
    if SO == "Linux":
        return os.geteuid() == 0
    else:
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

# ════════════════════════════════════════════════════════════
#  MENU PRINCIPAL
# ════════════════════════════════════════════════════════════

def analizar_pasta_termica(temp_cpu, temp_gpu, uptime_segundos, es_notebook):
    """Analiza temperaturas y recomienda cambio de pasta termica."""
    section_ok = True

    cprint("\n  [ Diagnostico de Pasta Termica ]", C.YELLOW)

    # Detectar tipo de equipo
    tipo = "NOTEBOOK" if es_notebook else "DESKTOP"
    cprint(f"  Tipo de equipo : {C.CYAN}{tipo}{C.RESET}", )

    # Umbrales segun tipo de equipo
    if es_notebook:
        umbral_ok     = 75
        umbral_alto   = 85
        umbral_critico= 95
    else:
        umbral_ok     = 70
        umbral_alto   = 80
        umbral_critico= 90

    # ── Temperatura CPU ──────────────────────────────────────
    cprint("\n  Temperatura CPU:", C.GRAY)
    if temp_cpu is not None:
        if temp_cpu < umbral_ok:
            cprint(f"  {temp_cpu}°C   NORMAL — pasta termica en buen estado", C.GREEN)
        elif temp_cpu < umbral_alto:
            cprint(f"  {temp_cpu}°C   ELEVADA — monitorear, considerar limpieza de ventiladores", C.YELLOW)
        elif temp_cpu < umbral_critico:
            cprint(f"  {temp_cpu}°C   ALTA — se recomienda cambio de pasta termica", C.RED)
            section_ok = False
        else:
            cprint(f"  {temp_cpu}°C   CRITICA — cambio de pasta URGENTE, riesgo de dano", C.RED)
            cprint(f"  El equipo puede apagarse automaticamente para protegerse.", C.RED)
            section_ok = False
    else:
        cprint("  No se pudo leer la temperatura CPU.", C.YELLOW)

    # ── Temperatura GPU ──────────────────────────────────────
    cprint("\n  Temperatura GPU:", C.GRAY)
    if temp_gpu is not None:
        gpu_umbral_ok  = 80 if es_notebook else 75
        gpu_umbral_alt = 90 if es_notebook else 85
        if temp_gpu < gpu_umbral_ok:
            cprint(f"  {temp_gpu}°C   NORMAL", C.GREEN)
        elif temp_gpu < gpu_umbral_alt:
            cprint(f"  {temp_gpu}°C   ELEVADA — verificar ventilacion", C.YELLOW)
        else:
            cprint(f"  {temp_gpu}°C   ALTA — revisar pasta termica GPU", C.RED)
            section_ok = False
    else:
        cprint("  No se pudo leer la temperatura GPU.", C.YELLOW)

    # ── Uptime como indicador ────────────────────────────────
    cprint("\n  Tiempo de uso en esta sesion:", C.GRAY)
    if uptime_segundos:
        horas = uptime_segundos // 3600
        mins  = (uptime_segundos % 3600) // 60
        cprint(f"  {horas}h {mins}m", C.CYAN)
        if temp_cpu and horas >= 2 and temp_cpu > umbral_alto:
            cprint("  Temperatura alta despues de 2+ horas de uso — indica problema de disipacion.", C.RED)

    # ── Historial de temperaturas (muestreo 3 lecturas) ──────
    cprint("\n  Historial de temperatura CPU (3 lecturas / 5 seg):", C.GRAY)
    import time
    lecturas = []
    for i in range(3):
        if SO == "Linux":
            s_out = run("sensors 2>/dev/null")
            m = re.search(r"(?:Package id 0|temp1|Core 0|temp2):\s+[+\-]?(\d+\.\d+)", s_out)
            t = float(m.group(1)) if m else None
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
            color = C.GREEN if t < umbral_ok else C.YELLOW if t < umbral_alto else C.RED
            cprint(f"  Lectura {i+1}: {t}°C", color)
        else:
            cprint(f"  Lectura {i+1}: N/A", C.YELLOW)

        if i < 2:
            time.sleep(5)

    if len(lecturas) >= 2:
        variacion = max(lecturas) - min(lecturas)
        if variacion > 10:
            cprint(f"\n  Variacion: {variacion:.1f}°C — temperatura inestable, revisar ventilacion.", C.RED)
        else:
            cprint(f"\n  Variacion: {variacion:.1f}°C — temperatura estable.", C.GREEN)

    # ── Recomendacion final ──────────────────────────────────
    cprint("\n  [ Recomendacion ]", C.CYAN)
    if temp_cpu is None:
        cprint("  Instalar sensor de temperatura para diagnostico completo.", C.YELLOW)
    elif temp_cpu < umbral_ok:
        cprint("  Pasta termica en buen estado. No requiere accion.", C.GREEN)
        if es_notebook:
            cprint("  Tip: limpiar ventiladores cada 6-12 meses.", C.GRAY)
    elif temp_cpu < umbral_alto:
        cprint("  Limpiar ventiladores y rejillas de ventilacion.", C.YELLOW)
        cprint("  Si persiste, considerar cambio de pasta termica.", C.YELLOW)
        if es_notebook:
            cprint("  Usar el notebook en superficie dura y plana.", C.GRAY)
    else:
        cprint("  CAMBIO DE PASTA TERMICA RECOMENDADO.", C.RED)
        cprint("  Pasos sugeridos:", C.YELLOW)
        cprint("  1. Apagar y desconectar el equipo", C.GRAY)
        cprint("  2. Limpiar pasta vieja con alcohol isopropilico 90%+", C.GRAY)
        cprint("  3. Aplicar pasta nueva (Arctic MX-4, Thermal Grizzly, etc.)", C.GRAY)
        cprint("  4. Limpiar ventiladores y disipador", C.GRAY)
        if es_notebook:
            cprint("  5. Considerar servicio tecnico si no tenes experiencia", C.GRAY)


def show_menu():
    tag = f"{C.GREEN}[LINUX]{C.RESET}" if SO == "Linux" else f"{C.CYAN}[WINDOWS]{C.RESET}"
    print(f"  {tag} Seleccione un modulo:\n")
    cprint("  [1]  Hardware e Identidad Termica",           C.RESET)
    cprint("  [2]  Mantenimiento del Sistema",              C.RESET)
    cprint("  [3]  Salud: Discos y S.M.A.R.T.",            C.RESET)
    cprint("  [4]  Auditoria de Seguridad (Puertos)",       C.RESET)
    cprint("  [5]  Reporte de Eventos del Sistema",         C.RESET)
    cprint("  [6]  Inventario de Software Instalado",       C.RESET)
    cprint("  [7]  Exportar Reporte (JSON/YAML/XML/CSV/PDF/HTML)", C.CYAN)
    cprint("  [8]  Ping / Test de Conectividad",            C.RESET)
    cprint("  [9]  Escaneo de Red Local",                   C.RESET)
    cprint("  [10] Auditoria de Permisos y Usuarios",       C.YELLOW)
    cprint("  [0]  Salir\n",                                C.RED)

def run_setup():
    """Instalador de dependencias del sistema -- modo --setup"""
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
        if SO == "Linux":
            cprint("  Uso: sudo python3 neuroaudit.py --setup\n", C.YELLOW)
        else:
            cprint("  Ejecutar como Administrador.\n", C.YELLOW)
        sys.exit(1)

    # ── Dependencias del sistema (Linux) ─────────────────────
    if SO == "Linux":
        distro_raw = run("grep '^ID_LIKE=' /etc/os-release | cut -d= -f2 | tr -d '\"'").lower()
        distro_id  = run("grep '^ID=' /etc/os-release | cut -d= -f2 | tr -d '\"'").lower()
        combined   = distro_raw + " " + distro_id

        if any(x in combined for x in ["debian","ubuntu","mint","pop","kali","elementary"]):
            pkg_mgr  = "apt"
            pkg_cmd  = "apt install -y"
            pkg_deps = {
                "lm-sensors":    "lm-sensors",
                "smartctl":      "smartmontools",
                "nmap":          "nmap",
                "ufw":           "ufw",
            }
        elif any(x in combined for x in ["fedora","rhel","centos","rocky","alma","oracle"]):
            pkg_mgr  = "dnf"
            pkg_cmd  = "dnf install -y"
            pkg_deps = {
                "sensors":   "lm_sensors",
                "smartctl":  "smartmontools",
                "nmap":      "nmap",
                "ufw":       "ufw",
            }
        elif any(x in combined for x in ["arch","manjaro","endeavour","garuda"]):
            pkg_mgr  = "pacman"
            pkg_cmd  = "pacman -S --noconfirm"
            pkg_deps = {
                "sensors":   "lm_sensors",
                "smartctl":  "smartmontools",
                "nmap":      "nmap",
                "ufw":       "ufw",
            }
        elif any(x in combined for x in ["opensuse","suse"]):
            pkg_mgr  = "zypper"
            pkg_cmd  = "zypper install -y"
            pkg_deps = {
                "sensors":   "sensors",
                "smartctl":  "smartmontools",
                "nmap":      "nmap",
                "ufw":       "ufw",
            }
        else:
            pkg_mgr  = None
            pkg_cmd  = None
            pkg_deps = {}

        section("DEPENDENCIAS DEL SISTEMA")
        print()

        if not pkg_mgr:
            cprint("  Gestor de paquetes no reconocido automaticamente.", C.YELLOW)
            cprint("  Instalar manualmente: lm-sensors smartmontools nmap ufw\n", C.GRAY)
        else:
            cprint(f"  Gestor detectado: {C.CYAN}{pkg_mgr}{C.RESET}\n")
            faltantes = {}
            for cmd, pkg in pkg_deps.items():
                if shutil.which(cmd):
                    cprint(f"  {'OK':<6} {cmd:<16} ya instalado", C.GREEN)
                else:
                    cprint(f"  {'FALTA':<6} {cmd:<16} ({pkg})", C.YELLOW)
                    faltantes[cmd] = pkg

            if faltantes:
                print()
                resp = input(f"  {C.CYAN}Instalar {len(faltantes)} dependencia(s) faltante(s)? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    # Actualizar repos primero
                    if pkg_mgr == "apt":
                        cprint("\n  Actualizando repositorios...", C.GRAY)
                        os.system("apt update -qq")
                    for cmd, pkg in faltantes.items():
                        cprint(f"\n  Instalando {pkg}...", C.YELLOW)
                        ret = os.system(f"sudo {pkg_cmd} {pkg}")
                        if ret == 0:
                            cprint(f"  {pkg} instalado correctamente.", C.GREEN)
                        else:
                            cprint(f"  Error instalando {pkg}.", C.RED)
                else:
                    cprint("  Instalacion omitida.", C.GRAY)
            else:
                cprint("\n  Todas las dependencias del sistema estan instaladas.", C.GREEN)

        # lm-sensors: configuracion inicial
        if shutil.which("sensors-detect") and not os.path.exists("/etc/sensors3.conf"):
            print()
            resp = input(f"  {C.CYAN}Ejecutar sensors-detect para configurar temperatura? (S/N): {C.RESET}").strip().lower()
            if resp == "s":
                os.system("sudo sensors-detect --auto")
                cprint("  sensors-detect completado.", C.GREEN)

        # ufw: activar si esta instalado
        if shutil.which("ufw"):
            ufw_status = run("ufw status | head -1")
            print()
            cprint(f"  UFW estado actual: {ufw_status}", C.GRAY)
            if "inactive" in ufw_status.lower():
                resp = input(f"  {C.CYAN}Activar UFW (firewall)? (S/N): {C.RESET}").strip().lower()
                if resp == "s":
                    os.system("sudo ufw --force enable")
                    cprint("  UFW activado.", C.GREEN)

    # ── Dependencias Python (ambas plataformas) ───────────────
    section("DEPENDENCIAS PYTHON")
    print()

    py_deps = {
        "yaml":       ("pyyaml",    "Exportacion YAML"),
        "reportlab":  ("reportlab", "Exportacion PDF"),
    }

    py_faltantes = {}
    for mod, (pkg, desc) in py_deps.items():
        try:
            __import__(mod)
            cprint(f"  {'OK':<6} {pkg:<16} {desc}", C.GREEN)
        except ImportError:
            cprint(f"  {'FALTA':<6} {pkg:<16} {desc}", C.YELLOW)
            py_faltantes[mod] = (pkg, desc)

    if py_faltantes:
        print()
        resp = input(f"  {C.CYAN}Instalar {len(py_faltantes)} modulo(s) Python faltante(s)? (S/N): {C.RESET}").strip().lower()
        if resp == "s":
            for mod, (pkg, desc) in py_faltantes.items():
                cprint(f"\n  Instalando {pkg}...", C.YELLOW)
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg],
                    capture_output=True, text=True
                )
                if result.returncode == 0:
                    cprint(f"  {pkg} instalado correctamente.", C.GREEN)
                else:
                    # Intentar con --break-system-packages en Linux
                    result2 = subprocess.run(
                        [sys.executable, "-m", "pip", "install", pkg, "--break-system-packages"],
                        capture_output=True, text=True
                    )
                    if result2.returncode == 0:
                        cprint(f"  {pkg} instalado correctamente.", C.GREEN)
                    else:
                        cprint(f"  Error instalando {pkg}: {result2.stderr[:100]}", C.RED)
    else:
        cprint("\n  Todos los modulos Python estan instalados.", C.GREEN)

    # ── Symlink / acceso directo ──────────────────────────────
    if SO == "Linux":
        section("ACCESO DIRECTO (OPCIONAL)")
        print()
        script_path = os.path.abspath(__file__)
        link_path   = "/usr/local/bin/neuroaudit"

        if os.path.exists(link_path):
            cprint(f"  Symlink ya existe: {link_path}", C.GREEN)
            cprint(f"  Podras ejecutar el script con: sudo neuroaudit", C.GRAY)
        else:
            cprint(f"  Script ubicado en: {script_path}", C.GRAY)
            resp = input(f"  {C.CYAN}Crear symlink en /usr/local/bin para ejecutar con 'sudo neuroaudit'? (S/N): {C.RESET}").strip().lower()
            if resp == "s":
                try:
                    os.chmod(script_path, 0o755)
                    os.symlink(script_path, link_path)
                    cprint(f"  Symlink creado: {link_path}", C.GREEN)
                    cprint(f"  Ahora podes ejecutar: sudo neuroaudit", C.CYAN)
                except Exception as e:
                    cprint(f"  Error creando symlink: {e}", C.RED)
                    cprint(f"  Crear manualmente: sudo ln -s {script_path} {link_path}", C.GRAY)

    # ── Resumen final ─────────────────────────────────────────
    section("RESUMEN DEL SETUP")
    print()
    cprint("  Setup completado. Estado final:\n", C.GREEN)

    if SO == "Linux":
        checks = {
            "lm-sensors / sensors": shutil.which("sensors") or shutil.which("lm-sensors"),
            "smartmontools":         shutil.which("smartctl"),
            "nmap":                  shutil.which("nmap"),
            "ufw":                   shutil.which("ufw"),
        }
        for nombre, found in checks.items():
            estado = f"{C.GREEN}OK{C.RESET}" if found else f"{C.RED}NO INSTALADO{C.RESET}"
            print(f"  {nombre:<25} {estado}")

    print()
    for mod, (pkg, desc) in py_deps.items():
        try:
            __import__(mod)
            print(f"  {pkg:<25} {C.GREEN}OK{C.RESET}  ({desc})")
        except ImportError:
            print(f"  {pkg:<25} {C.RED}NO INSTALADO{C.RESET}  ({desc})")

    print()
    cprint("  Para iniciar NEUROAUDIT:", C.CYAN)
    if SO == "Linux":
        cprint("    sudo python3 neuroaudit.py", C.GRAY)
        if os.path.exists("/usr/local/bin/neuroaudit"):
            cprint("    sudo neuroaudit  (via symlink)", C.GRAY)
    else:
        cprint("    python neuroaudit.py  (como Administrador)", C.GRAY)
    print()
    input(f"  {C.CYAN}Presione Enter para salir...{C.RESET}")


def main():
    C.enable_windows_ansi()

    # ── Modo --setup ──────────────────────────────────────────
    if "--setup" in sys.argv:
        run_setup()
        sys.exit(0)

    # ── Verificar venv en Linux ───────────────────────────────
    if SO == "Linux":
        in_venv, venv_python, script_dir = _check_venv()
        launcher = os.path.join(script_dir, "neuroaudit")
        if not in_venv and os.path.exists(venv_python):
            cprint("\n  Detectado entorno virtual (venv) sin usar.", C.YELLOW)
            cprint("  Para mejores resultados usa el lanzador:", C.YELLOW)
            cprint(f"  {launcher}", C.CYAN)
            print()
            resp = input(f"  {C.CYAN}Continuar de todas formas? (S/N): {C.RESET}").strip().lower()
            if resp != "s":
                cprint(f"\n  Ejecuta: {launcher}\n", C.GREEN)
                sys.exit(0)

    if not check_privileges():
        cprint(f"\n  ERROR: Ejecutar como root (Linux) o Administrador (Windows).\n", C.RED)
        if SO == "Linux":
            _, venv_python, script_dir = _check_venv()
            launcher = os.path.join(script_dir, "neuroaudit")
            if os.path.exists(launcher):
                cprint(f"  Uso: {launcher}\n", C.CYAN)
            else:
                cprint("  Uso       : sudo python3 neuroaudit.py\n", C.YELLOW)
                cprint("  Primer uso: bash instalar_neuroaudit.sh\n", C.CYAN)
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

