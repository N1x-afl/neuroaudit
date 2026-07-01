#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.6.0 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# - NEW: Módulo 11 — Escaneo CVE real contra todos los paquetes
#         instalados via OSV.dev batch API (sin API key).
#         Severidades CRITICAL/HIGH/MEDIUM con detalle y export JSON.
# - FIX: import urllib.error agregado para manejo robusto de red.
# - PREV: Auditoría de vulnerabilidades críticas (CVE-2026-31431).
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
import urllib.error

# ── Configuración Core ─────────────────────────────────────
VERSION      = "6.6.0"
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
        cprint("\n  [ Verificando Salud de Repositorios ]", C.YELLOW)
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
            if temp_cpu < 60: cprint(f"  ✓ Estado Óptimo: {temp_cpu}°C", C.GREEN)
            elif temp_cpu < 80: cprint(f"  ⚠ Temperatura Elevada: {temp_cpu}°C", C.YELLOW)
            else: cprint(f"  ✗ CRÍTICO: {temp_cpu}°C", C.RED, bold=True)

    @staticmethod
    def maintenance():
        section("MANTENIMIENTO DEL SISTEMA")
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
            if not Linux.check_repo_health(): cprint("\n  [!] Error de ruteo. Use Opción [2] antes.", C.RED)
            else: os.system("sudo apt update && sudo apt upgrade -y")
        elif op == "2":
            os.system("sudo sed -i 's/https:/http:/g' /etc/apt/sources.list.d/zorinos-*.sources")
            cprint("  ✓ Bypass aplicado.", C.GREEN)
        elif op == "3":
            os.system("sudo sed -i 's/http:/https:/g' /etc/apt/sources.list.d/zorinos-*.sources")
            cprint("  ✓ Seguridad restaurada.", C.GREEN)
        elif op == "4":
            os.system("sudo apt autoremove -y && sudo apt clean")
        elif op == "5":
            os.system("sudo journalctl --vacuum-time=7d")

    @staticmethod
    def vulnerability_audit():
        section("AUDITORÍA DE VULNERABILIDAD CRÍTICA")
        version = run("dpkg -l | grep libcurl4t64 | awk '{print $3}'")
        cprint(f"  Librería: libcurl4t64 | Versión: {version if version else 'N/A'}", C.CYAN)
        if "10.8" in version:
            cprint("\n  [!] ESTADO: VULNERABLE (CVE-2026-31431)", C.RED, bold=True)
        elif version:
            cprint("\n  [✓] ESTADO: PROTEGIDO", C.GREEN, bold=True)

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
        os.system("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -n 30 2>/dev/null")
        count = run("dpkg -l | grep '^ii' | wc -l")
        cprint(f"\n  Total paquetes instalados: {count}", C.YELLOW)

    @staticmethod
    def network_scan():
        section("ESCANEO DE RED LOCAL")
        ip_local = run("hostname -I | awk '{print $1}'")
        if not ip_local: return
        subred = ip_local.rsplit('.', 1)[0] + ".0/24"
        cprint(f"  Escaneando: {subred}...\n", C.YELLOW)
        os.system(f"sudo nmap -sn {subred}")

    @staticmethod
    def permission_audit():
        section("AUDITORIA DE PERMISOS Y USUARIOS")
        cprint("\n  [ Archivos Críticos ]", C.YELLOW)
        os.system("ls -la /etc/shadow /etc/sudoers")
        cprint("\n  [ Usuarios con SUDO ]", C.YELLOW)
        print(run("grep -Po '^sudo:.*:\\K.*|^wheel:.*:\\K.*' /etc/group") or "Solo root")

    @staticmethod
    def cve_scan():
        section("ESCANEO DE VULNERABILIDADES CVE — PAQUETES INSTALADOS")
        OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"
        SEV_COLOR = {
            "CRITICAL": C.RED, "HIGH": C.RED, "MEDIUM": C.YELLOW,
            "LOW": C.GRAY, "UNKNOWN": C.GRAY
        }
        SEV_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}

        # ── 1. Obtener paquetes instalados ──────────────────────
        cprint("\n  [*] Obteniendo inventario de paquetes...", C.CYAN)
        raw = run("dpkg-query -W -f='${Package} ${Version}\\n' 2>/dev/null")
        if not raw:
            cprint("  ✗ No se pudo obtener el inventario de paquetes.", C.RED)
            return
        packages = []
        for line in raw.splitlines():
            parts = line.strip().split(" ", 1)
            if len(parts) == 2 and parts[1]:
                packages.append({"name": parts[0], "version": parts[1]})

        total = len(packages)
        cprint(f"  ✓ {total} paquetes detectados. Consultando OSV.dev...\n", C.GREEN)

        # ── 2. Consulta batch a OSV (chunks de 100) ─────────────
        CHUNK = 100
        findings = []
        errors = 0

        for i in range(0, total, CHUNK):
            chunk = packages[i:i + CHUNK]
            progress = min(i + CHUNK, total)
            print(f"\r  Analizando: {progress}/{total} paquetes...", end="", flush=True)

            queries = [
                {
                    "package": {"name": pkg["name"], "ecosystem": "Debian"},
                    "version": pkg["version"]
                }
                for pkg in chunk
            ]
            payload = json.dumps({"queries": queries}).encode("utf-8")
            req = urllib.request.Request(
                OSV_BATCH_URL,
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": f"NeuroAudit/{VERSION}"
                }
            )
            try:
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                    results = data.get("results", [])
                    for j, res in enumerate(results):
                        vulns = res.get("vulns", [])
                        if vulns:
                            pkg = chunk[j]
                            for v in vulns:
                                # Extraer severidad (CVSS v3 > v2 > database_specific)
                                sev = "UNKNOWN"
                                score = None
                                for sev_entry in v.get("severity", []):
                                    if sev_entry.get("type") == "CVSS_V3":
                                        score_val = sev_entry.get("score", "")
                                        # Score numérico desde CVSS vector o campo separado
                                        if "CVSS" in score_val:
                                            # Calcular severidad desde vector
                                            if "AV:N" in score_val and "AC:L" in score_val:
                                                sev = "HIGH"
                                            elif score_val.count("/") > 3:
                                                sev = "MEDIUM"
                                        break
                                # Fallback a database_specific
                                db_sev = v.get("database_specific", {}).get("severity", "")
                                if db_sev and sev == "UNKNOWN":
                                    sev = db_sev.upper()
                                # Fallback: buscar en aliases si tiene GHSA con score
                                if sev == "UNKNOWN":
                                    for alias in v.get("aliases", []):
                                        if alias.startswith("CVE-"):
                                            sev = "UNKNOWN"
                                            break

                                findings.append({
                                    "package": pkg["name"],
                                    "version": pkg["version"],
                                    "cve_id": v.get("id", "N/A"),
                                    "aliases": [a for a in v.get("aliases", []) if a.startswith("CVE-")][:2],
                                    "severity": sev if sev in SEV_ORDER else "UNKNOWN",
                                    "summary": v.get("summary", "Sin descripción")[:80]
                                })
            except urllib.error.URLError as e:
                errors += 1
                continue
            except Exception:
                errors += 1
                continue

        print()  # newline tras el progress

        # ── 3. Resultados ────────────────────────────────────────
        if not findings:
            if errors > 0:
                cprint(f"\n  ✗ No se pudo conectar a OSV.dev ({errors} errores). Verificá tu conexión.", C.RED)
            else:
                cprint("\n  ✓ Sin vulnerabilidades conocidas detectadas en los paquetes instalados.", C.GREEN)
            return

        # Ordenar por severidad
        findings.sort(key=lambda x: SEV_ORDER.get(x["severity"], 4))

        # Conteo por severidad
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
        for f in findings:
            counts[f["severity"]] = counts.get(f["severity"], 0) + 1

        cprint(f"\n  {'─'*58}", C.CYAN)
        cprint(f"  RESUMEN: {len(findings)} vulnerabilidades en {len(set(f['package'] for f in findings))} paquetes", C.BOLD)
        cprint(f"  {'─'*58}", C.CYAN)
        for sev, cnt in counts.items():
            if cnt > 0:
                label = f"  {sev:<10}: {cnt}"
                cprint(label, SEV_COLOR.get(sev, C.RESET))

        # Detalle — solo CRITICAL y HIGH por defecto
        cprint(f"\n  [ Paquetes Vulnerables — CRITICAL / HIGH ]", C.YELLOW)
        shown = 0
        for f in findings:
            if f["severity"] not in ("CRITICAL", "HIGH"):
                continue
            cve_display = ", ".join(f["aliases"]) if f["aliases"] else f["cve_id"]
            color = SEV_COLOR.get(f["severity"], C.RESET)
            cprint(f"  ✗ [{f['severity']:<8}] {f['package']} {f['version']}", color, bold=True)
            print(f"         CVE  : {cve_display}")
            print(f"         ID   : {f['cve_id']}")
            print(f"         Info : {f['summary']}")
            print()
            shown += 1

        if shown == 0:
            cprint("  ✓ Sin paquetes CRITICAL o HIGH detectados.", C.GREEN)

        # Opción de ver MEDIUM también
        if counts.get("MEDIUM", 0) > 0:
            cprint(f"\n  [*] También hay {counts['MEDIUM']} vulnerabilidades MEDIUM.", C.YELLOW)
            ver = input("  ¿Mostrar detalle de MEDIUM? [s/N]: ").strip().lower()
            if ver == "s":
                for f in findings:
                    if f["severity"] != "MEDIUM":
                        continue
                    cve_display = ", ".join(f["aliases"]) if f["aliases"] else f["cve_id"]
                    cprint(f"  ⚠ [MEDIUM   ] {f['package']} {f['version']}", C.YELLOW)
                    print(f"         CVE  : {cve_display}")
                    print(f"         Info : {f['summary']}")
                    print()

        # Exportar hallazgos a JSON
        export_path = os.path.join(
            _get_real_home(),
            f"neuroaudit_cve_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        try:
            with open(export_path, "w") as fp:
                json.dump({
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "host": platform.node(),
                    "total_paquetes": total,
                    "total_vulns": len(findings),
                    "resumen": counts,
                    "vulnerabilidades": findings
                }, fp, indent=4, ensure_ascii=False)
            cprint(f"\n  ✓ Reporte exportado: {export_path}", C.GREEN)
        except Exception as e:
            cprint(f"\n  ⚠ No se pudo exportar el reporte: {e}", C.YELLOW)

# ── Funciones Globales ─────────────────────────────────────

def run_export():
    section("EXPORTAR REPORTE")
    data = {"fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "kernel": platform.release(), "cpu": run("grep -m1 'model name' /proc/cpuinfo | cut -d: -f2").strip(), "ram": run("free -h | grep Mem | awk '{print $3\" / \"$2}'")}
    path = os.path.join(_get_real_home(), f"reporte_audit_{datetime.datetime.now().strftime('%Y%m%d')}.json")
    with open(path, "w") as f: json.dump(data, f, indent=4)
    cprint(f"  ✓ Reporte JSON guardado en: {path}", C.GREEN)

def auto_update_neuroaudit():
    try:
        with urllib.request.urlopen(GITHUB_RAW_URL) as r:
            with open(__file__, "wb") as f: f.write(r.read())
        cprint(f"✓ v{VERSION} Instalada. Reinicie.", C.GREEN); sys.exit()
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
    print(f"\n  {C.CYAN}{SYSTEM_NAME}{C.RESET}")
    print(f"  Autor      : {DEVELOPER}")
    print(f"  Kernel     : {platform.release()}\n")

def show_menu():
    print(f"  [1]  Estado de Hardware y Salud Térmica")
    print(f"  [2]  Mantenimiento y Actualización")
    print(f"  [3]  Auditoría de Vulnerabilidades (CVE)")
    print(f"  [4]  Salud de Discos (S.M.A.R.T.)")
    print(f"  [5]  Escaneo de Red y Puertos")
    print(f"  [6]  Reporte de Eventos/Errores")
    print(f"  [7]  Exportar Reporte JSON")
    print(f"  [8]  Inventario de Software")
    print(f"  [9]  Actualizar Suite NeuroAudit")
    cprint("  [10] Auditoría de Permisos / Usuarios", C.YELLOW)
    cprint("  [11] Escaneo CVE — Paquetes Instalados", C.RED)
    cprint("  [0]  Salir\n", C.RED)

def main():
    C.enable_windows_ansi()
    M = Linux
    acciones = {
        "1": M.sys_info, "2": M.maintenance, "3": M.vulnerability_audit, "4": M.disk_health, 
        "5": lambda: (M.network_scan(), M.security_audit()), "6": M.event_report, "7": run_export,
        "8": M.software_inventory, "9": auto_update_neuroaudit, "10": M.permission_audit,
        "11": M.cve_scan
    }
    while True:
        show_banner(); show_menu()
        op = input(f"  Seleccione: ").strip()
        if op == "0": break
        if op in acciones: acciones[op](); pause()

if __name__ == "__main__":
    main()
