#!/usr/bin/env python3
# ===========================================================
# NEUROAUDIT v6.7.0 - Security & IT Suite
# Developed by: Felipe Soluciones IT
# ===========================================================
# - NEW: Módulo 1 — Diagnóstico de pasta térmica con stress test
#         Umbrales por tipo CPU (Intel/AMD Tctl), delta idle→carga,
#         instalación automática de stress si no está presente.
# - PREV: Módulo 1 — Detección de temperatura multi-plataforma
#         Submenú con 5 checks: Firewall, SUID/SGID, Accesos
#         fallidos, Procesos anómalos, Conexiones sospechosas.
#         Export JSON consolidado al finalizar.
# - PREV: Módulo 11 — CVE scan via OSV.dev batch API.
# - FIX: Módulo 8 — tubería rota suprimida con subprocess.
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
VERSION      = "6.7.3"
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

def subsection(title):
    print()
    cprint(f"  ┌{'─'*54}┐", C.YELLOW)
    cprint(f"  │  {title:<52}│", C.YELLOW)
    cprint(f"  └{'─'*54}┘", C.YELLOW)

def run(cmd, shell=True, timeout=10):
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
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
        # Detección de temperatura multi-plataforma por orden de prioridad
        sensors_out = run("sensors 2>/dev/null")
        temp_cpu = None
        sensor_nombre = "N/A"
        sensor_tipo = "desconocido"

        SENSORES = [
            # (regex, nombre display, tipo hardware)
            (r"Tctl:\s+[+\-]?(\d+\.\d+)",          "Tctl",          "AMD Ryzen (k10temp)"),
            (r"Tccd1:\s+[+\-]?(\d+\.\d+)",          "Tccd1",         "AMD Ryzen CCD1"),
            (r"Package id 0:\s+[+\-]?(\d+\.\d+)",   "Package id 0",  "Intel (coretemp)"),
            (r"Core 0:\s+[+\-]?(\d+\.\d+)",         "Core 0",        "Intel Core"),
            (r"temp1:\s+[+\-]?(\d+\.\d+)",          "temp1",         "Genérico"),
            (r"CPU:\s+[+\-]?(\d+\.\d+)",            "CPU",           "Genérico ARM/otro"),
        ]

        if not sensors_out:
            # Fallback: leer directo desde sysfs (sin lm-sensors)
            for path in [
                "/sys/class/thermal/thermal_zone0/temp",
                "/sys/class/hwmon/hwmon0/temp1_input",
            ]:
                val = run(f"cat {path} 2>/dev/null")
                if val and val.isdigit():
                    temp_cpu = float(val) / 1000
                    sensor_nombre = path.split("/")[-1]
                    sensor_tipo = "sysfs (sin lm-sensors)"
                    break
        else:
            for patron, nombre, tipo in SENSORES:
                m = re.search(patron, sensors_out)
                if m:
                    temp_cpu = float(m.group(1))
                    sensor_nombre = nombre
                    sensor_tipo = tipo
                    break

        print(f"  SERIAL : {serial if serial else 'No detectable'}")
        print(f"  CPU    : {cpu}")
        if temp_cpu:
            print(f"  TEMP   : {temp_cpu}°C  [sensor: {sensor_nombre} — {sensor_tipo}]")
        else:
            print(f"  TEMP   : N/A  (instalá lm-sensors: sudo apt install lm-sensors)")
        print(f"  RAM    : {ram} en uso")
        print(f"  UPTIME : {uptime}")

        if temp_cpu:
            # Determinar umbrales según tipo de sensor
            es_amd_tctl = sensor_nombre == "Tctl"
            umbral_elevado = 70 if es_amd_tctl else 60
            umbral_critico = 95 if es_amd_tctl else 85

            cprint("\n  [ Diagnóstico de Pasta Térmica ]", C.YELLOW)
            cprint(f"  Temperatura idle  : {temp_cpu}°C", C.CYAN)

            # Verificar si stress está disponible
            stress_ok = bool(shutil.which("stress"))

            if not stress_ok:
                cprint("\n  [!] 'stress' no está instalado.", C.YELLOW)
                instalar = input("  ¿Instalarlo ahora para diagnóstico completo? [s/N]: ").strip().lower()
                if instalar == "s":
                    ret = os.system("sudo apt install stress -y > /dev/null 2>&1")
                    stress_ok = (ret == 0)
                    if stress_ok:
                        cprint("  ✓ stress instalado correctamente.", C.GREEN)
                    else:
                        cprint("  ✗ No se pudo instalar stress.", C.RED)

            if stress_ok:
                nucleos = run("nproc").strip() or "2"
                cprint(f"\n  [*] Estresando CPU {nucleos} núcleos por 10 segundos...", C.CYAN)
                os.system(f"stress --cpu {nucleos} --timeout 10 > /dev/null 2>&1")
                time.sleep(1)  # pequeña pausa para que sensors se actualice

                # Leer temperatura bajo carga
                temp_carga = None
                sensors_carga = run("sensors 2>/dev/null")
                if sensors_carga:
                    for patron, nombre, tipo in SENSORES:
                        m2 = re.search(patron, sensors_carga)
                        if m2:
                            temp_carga = float(m2.group(1))
                            break
                else:
                    for path in ["/sys/class/thermal/thermal_zone0/temp",
                                 "/sys/class/hwmon/hwmon0/temp1_input"]:
                        val = run(f"cat {path} 2>/dev/null")
                        if val and val.isdigit():
                            temp_carga = float(val) / 1000
                            break

                if temp_carga:
                    delta = round(temp_carga - temp_cpu, 1)
                    cprint(f"  Temperatura carga : {temp_carga}°C", C.CYAN)
                    cprint(f"  Delta (Δ)         : {delta}°C", C.CYAN)
                    print()

                    # Diagnóstico por delta
                    if delta < 20:
                        cprint("  ✓ Pasta térmica en buen estado.", C.GREEN, bold=True)
                    elif delta < 35:
                        cprint("  ⚠ Pasta posiblemente degradada.", C.YELLOW, bold=True)
                        cprint("    → Considerá limpieza y reemplazo de pasta térmica.", C.YELLOW)
                    else:
                        cprint("  ✗ Delta elevado — Cambio de pasta recomendado.", C.RED, bold=True)
                        cprint("    → Temperatura sube demasiado rápido bajo carga.", C.RED)

                    # Diagnóstico por temperatura absoluta bajo carga
                    print()
                    if temp_carga < umbral_elevado:
                        cprint(f"  ✓ Temperatura bajo carga aceptable: {temp_carga}°C", C.GREEN)
                    elif temp_carga < umbral_critico:
                        cprint(f"  ⚠ Temperatura bajo carga elevada: {temp_carga}°C", C.YELLOW)
                        cprint(f"    → Revisá ventilación y limpieza de cooler.", C.YELLOW)
                    else:
                        cprint(f"  ✗ CRÍTICO: {temp_carga}°C — Riesgo de throttling o daño", C.RED, bold=True)
                        cprint(f"    → Apagá el equipo y revisá el sistema de refrigeración.", C.RED)
                else:
                    cprint("  ⚠ No se pudo leer temperatura bajo carga.", C.YELLOW)
            else:
                # Diagnóstico solo con temperatura idle
                print()
                if temp_cpu < umbral_elevado:
                    cprint(f"  ✓ Temperatura idle aceptable: {temp_cpu}°C", C.GREEN)
                elif temp_cpu < umbral_critico:
                    cprint(f"  ⚠ Temperatura idle elevada: {temp_cpu}°C", C.YELLOW)
                    cprint(f"    → Instalá stress para diagnóstico completo.", C.YELLOW)
                else:
                    cprint(f"  ✗ CRÍTICO en idle: {temp_cpu}°C", C.RED, bold=True)
                    cprint(f"    → Revisá refrigeración inmediatamente.", C.RED)

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
        output = run("dpkg -l | grep '^ii' | awk '{print $2, $3}' | head -n 30 2>/dev/null")
        print(output)
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

        CHUNK = 100
        findings = []
        errors = 0

        for i in range(0, total, CHUNK):
            chunk = packages[i:i + CHUNK]
            progress = min(i + CHUNK, total)
            print(f"\r  Analizando: {progress}/{total} paquetes...", end="", flush=True)

            queries = [
                {"package": {"name": pkg["name"], "ecosystem": "Debian"}, "version": pkg["version"]}
                for pkg in chunk
            ]
            payload = json.dumps({"queries": queries}).encode("utf-8")
            req = urllib.request.Request(
                OSV_BATCH_URL, data=payload,
                headers={"Content-Type": "application/json", "User-Agent": f"NeuroAudit/{VERSION}"}
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
                                sev = "UNKNOWN"
                                for sev_entry in v.get("severity", []):
                                    if sev_entry.get("type") == "CVSS_V3":
                                        score_val = sev_entry.get("score", "")
                                        if "AV:N" in score_val and "AC:L" in score_val:
                                            sev = "HIGH"
                                        elif score_val.count("/") > 3:
                                            sev = "MEDIUM"
                                        break
                                db_sev = v.get("database_specific", {}).get("severity", "")
                                if db_sev and sev == "UNKNOWN":
                                    sev = db_sev.upper()
                                findings.append({
                                    "package": pkg["name"], "version": pkg["version"],
                                    "cve_id": v.get("id", "N/A"),
                                    "aliases": [a for a in v.get("aliases", []) if a.startswith("CVE-")][:2],
                                    "severity": sev if sev in SEV_ORDER else "UNKNOWN",
                                    "summary": v.get("summary", "Sin descripción")[:80]
                                })
            except urllib.error.URLError:
                errors += 1
                continue
            except Exception:
                errors += 1
                continue

        print()

        if not findings:
            if errors > 0:
                cprint(f"\n  ✗ No se pudo conectar a OSV.dev ({errors} errores). Verificá tu conexión.", C.RED)
            else:
                cprint("\n  ✓ Sin vulnerabilidades conocidas detectadas en los paquetes instalados.", C.GREEN)
            return

        findings.sort(key=lambda x: SEV_ORDER.get(x["severity"], 4))
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
        for f in findings:
            counts[f["severity"]] = counts.get(f["severity"], 0) + 1

        cprint(f"\n  {'─'*58}", C.CYAN)
        cprint(f"  RESUMEN: {len(findings)} vulnerabilidades en {len(set(f['package'] for f in findings))} paquetes", C.BOLD)
        cprint(f"  {'─'*58}", C.CYAN)
        for sev, cnt in counts.items():
            if cnt > 0:
                cprint(f"  {sev:<10}: {cnt}", SEV_COLOR.get(sev, C.RESET))

        cprint(f"\n  [ Paquetes Vulnerables — CRITICAL / HIGH ]", C.YELLOW)
        shown = 0
        for f in findings:
            if f["severity"] not in ("CRITICAL", "HIGH"):
                continue
            cve_display = ", ".join(f["aliases"]) if f["aliases"] else f["cve_id"]
            cprint(f"  ✗ [{f['severity']:<8}] {f['package']} {f['version']}", SEV_COLOR.get(f["severity"], C.RESET), bold=True)
            print(f"         CVE  : {cve_display}")
            print(f"         ID   : {f['cve_id']}")
            print(f"         Info : {f['summary']}")
            print()
            shown += 1

        if shown == 0:
            cprint("  ✓ Sin paquetes CRITICAL o HIGH detectados.", C.GREEN)

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

        export_path = os.path.join(
            _get_real_home(),
            f"neuroaudit_cve_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        try:
            with open(export_path, "w") as fp:
                json.dump({
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "host": platform.node(), "total_paquetes": total,
                    "total_vulns": len(findings), "resumen": counts,
                    "vulnerabilidades": findings
                }, fp, indent=4, ensure_ascii=False)
            cprint(f"\n  ✓ Reporte exportado: {export_path}", C.GREEN)
        except Exception as e:
            cprint(f"\n  ⚠ No se pudo exportar el reporte: {e}", C.YELLOW)

    # ── Módulo 12: Auditoría de Servidor ──────────────────
    @staticmethod
    def _srv_firewall():
        subsection("FIREWALL — ESTADO Y REGLAS ACTIVAS")
        resultado = {"firewall": "desconocido", "estado": "", "reglas": []}

        # Detectar ufw o iptables
        ufw_status = run("sudo ufw status verbose 2>/dev/null")
        if ufw_status:
            resultado["firewall"] = "ufw"
            if "Status: active" in ufw_status:
                cprint("  ✓ UFW: ACTIVO", C.GREEN, bold=True)
                resultado["estado"] = "activo"
            else:
                cprint("  ✗ UFW: INACTIVO", C.RED, bold=True)
                resultado["estado"] = "inactivo"
            print()
            # Mostrar reglas relevantes
            for line in ufw_status.splitlines():
                if any(k in line for k in ["ALLOW", "DENY", "REJECT", "LIMIT", "To", "From", "---"]):
                    print(f"  {line}")
                    resultado["reglas"].append(line.strip())
        else:
            # Fallback a iptables
            iptables = run("sudo iptables -L INPUT --line-numbers -n 2>/dev/null | head -30")
            if iptables:
                resultado["firewall"] = "iptables"
                resultado["estado"] = "activo"
                cprint("  ✓ iptables detectado (sin UFW)", C.YELLOW)
                print()
                print(iptables)
                resultado["reglas"] = iptables.splitlines()
            else:
                cprint("  ✗ Sin firewall detectado (UFW ni iptables)", C.RED, bold=True)
                resultado["estado"] = "sin firewall"

        # Puertos expuestos al exterior
        cprint("\n  [ Puertos en Escucha — Exposición Externa ]", C.YELLOW)
        puertos = run("sudo ss -tulpn 2>/dev/null | grep LISTEN")
        if puertos:
            for line in puertos.splitlines():
                # Marcar puertos en 0.0.0.0 o :: como expuestos
                if "0.0.0.0" in line or "[::]" in line or "*:" in line:
                    cprint(f"  ⚠ {line}", C.YELLOW)
                else:
                    print(f"     {line}")
        resultado["puertos_escucha"] = puertos.splitlines() if puertos else []
        return resultado

    @staticmethod
    def _srv_suid():
        subsection("ARCHIVOS SUID / SGID SOSPECHOSOS")
        resultado = {"suid_total": 0, "sgid_total": 0, "sospechosos": [], "conocidos_ok": []}

        # Binarios SUID/SGID conocidos y legítimos en Debian/Ubuntu
        WHITELIST = {
            "/usr/bin/sudo", "/usr/bin/su", "/usr/bin/passwd", "/usr/bin/chsh",
            "/usr/bin/chfn", "/usr/bin/newgrp", "/usr/bin/gpasswd", "/usr/bin/mount",
            "/usr/bin/umount", "/usr/bin/pkexec", "/usr/bin/fusermount3",
            "/usr/lib/openssh/ssh-keysign", "/usr/lib/dbus-1.0/dbus-daemon-launch-helper",
            "/usr/lib/policykit-1/polkit-agent-helper-1", "/usr/sbin/pppd",
            "/usr/bin/wall", "/usr/bin/write", "/usr/bin/ping", "/usr/bin/traceroute6.iputils",
            "/usr/lib/xorg/Xorg.wrap", "/usr/bin/at", "/usr/bin/crontab",
            "/usr/bin/ssh-agent", "/usr/lib/snapd/snap-confine"
        }

        cprint("\n  [*] Buscando archivos SUID...", C.CYAN)
        suid_raw = run("sudo find / -xdev -perm -4000 -type f 2>/dev/null", timeout=30)
        suid_list = suid_raw.splitlines() if suid_raw else []
        resultado["suid_total"] = len(suid_list)

        cprint("  [*] Buscando archivos SGID...", C.CYAN)
        sgid_raw = run("sudo find / -xdev -perm -2000 -type f 2>/dev/null", timeout=30)
        sgid_list = sgid_raw.splitlines() if sgid_raw else []
        resultado["sgid_total"] = len(sgid_list)

        print()
        cprint(f"  SUID encontrados : {len(suid_list)}", C.CYAN)
        cprint(f"  SGID encontrados : {len(sgid_list)}", C.CYAN)

        # Clasificar
        sospechosos = []
        for f in suid_list + sgid_list:
            f = f.strip()
            if not f:
                continue
            if f in WHITELIST:
                resultado["conocidos_ok"].append(f)
            else:
                sospechosos.append(f)

        resultado["sospechosos"] = sospechosos

        if sospechosos:
            cprint(f"\n  ✗ SUID/SGID FUERA DE WHITELIST ({len(sospechosos)}):", C.RED, bold=True)
            for s in sospechosos:
                perms = run(f"stat -c '%A %U %G' {s} 2>/dev/null") or "N/A"
                cprint(f"  ⚠ {s}", C.YELLOW)
                print(f"       Permisos: {perms}")
        else:
            cprint("\n  ✓ Todos los SUID/SGID son binarios conocidos y legítimos.", C.GREEN)

        return resultado

    @staticmethod
    def _srv_accesos():
        subsection("ACCESOS FALLIDOS Y ÚLTIMOS LOGINS")
        resultado = {"fallos_ssh": [], "fallos_sistema": [], "ultimos_logins": [], "ips_top": []}

        # Intentos fallidos SSH desde auth.log o journald
        cprint("\n  [ Intentos de Acceso Fallidos — SSH ]", C.YELLOW)
        fallos_ssh = run(
            "sudo grep -i 'failed password\\|invalid user\\|authentication failure' "
            "/var/log/auth.log 2>/dev/null | tail -20"
        )
        if not fallos_ssh:
            # Fallback a journald (sistemas sin auth.log)
            fallos_ssh = run(
                "sudo journalctl -u ssh --since '24 hours ago' 2>/dev/null | "
                "grep -i 'failed\\|invalid' | tail -20"
            )

        if fallos_ssh:
            for line in fallos_ssh.splitlines():
                print(f"  {line}")
            resultado["fallos_ssh"] = fallos_ssh.splitlines()

            # Top IPs atacantes
            ips = run(
                "sudo grep -oE '([0-9]{1,3}\\.){3}[0-9]{1,3}' /var/log/auth.log 2>/dev/null | "
                "sort | uniq -c | sort -rn | head -10"
            )
            if ips:
                cprint("\n  [ Top IPs con Fallos ]", C.YELLOW)
                for line in ips.splitlines():
                    count_str = line.strip().split()[0] if line.strip() else "0"
                    try:
                        count = int(count_str)
                        color = C.RED if count > 10 else C.YELLOW if count > 3 else C.RESET
                    except ValueError:
                        color = C.RESET
                    cprint(f"  {line}", color)
                resultado["ips_top"] = ips.splitlines()
        else:
            cprint("  ✓ Sin intentos fallidos recientes detectados.", C.GREEN)

        # Faillog del sistema
        cprint("\n  [ Cuentas con Fallos de Login (faillog) ]", C.YELLOW)
        faillog = run("sudo faillog -a 2>/dev/null | grep -v '00:00:00' | grep -v '^Login' | head -15")
        if faillog:
            print(faillog)
            resultado["fallos_sistema"] = faillog.splitlines()
        else:
            cprint("  Sin datos de faillog disponibles.", C.GRAY)

        # Últimos logins exitosos
        cprint("\n  [ Últimos Logins Exitosos ]", C.YELLOW)
        last_logins = run("last -n 15 -F 2>/dev/null | grep -v 'reboot\\|wtmp'")
        if last_logins:
            for line in last_logins.splitlines():
                if line.strip():
                    print(f"  {line}")
            resultado["ultimos_logins"] = last_logins.splitlines()
        else:
            cprint("  Sin datos disponibles.", C.GRAY)

        # Cuentas sin password o expiradas
        cprint("\n  [ Cuentas Sin Password / Expiradas ]", C.YELLOW)
        no_pass = run("sudo awk -F: '($2 == \"\" || $2 == \"!\") {print $1}' /etc/shadow 2>/dev/null")
        if no_pass:
            cprint(f"  ✗ Cuentas sin password activa: {no_pass}", C.RED)
            resultado["sin_password"] = no_pass.splitlines()
        else:
            cprint("  ✓ Todas las cuentas tienen password configurado.", C.GREEN)

        return resultado

    @staticmethod
    def _srv_procesos():
        subsection("PROCESOS ANÓMALOS — TOP CONSUMIDORES")
        resultado = {"top_cpu": [], "top_ram": [], "sospechosos": []}

        # Top 10 por CPU
        cprint("\n  [ Top 10 Procesos por CPU ]", C.YELLOW)
        top_cpu = run("ps aux --sort=-%cpu | head -11 | awk 'NR>1 {printf \"  %-8s %-6s %-6s %s\\n\", $1, $3, $4, $11}'")
        if top_cpu:
            cprint(f"  {'USUARIO':<8} {'%CPU':<6} {'%MEM':<6} PROCESO", C.CYAN)
            cprint(f"  {'─'*50}", C.CYAN)
            for line in top_cpu.splitlines():
                parts = line.strip().split()
                if parts:
                    try:
                        cpu_val = float(parts[1]) if len(parts) > 1 else 0
                        color = C.RED if cpu_val > 80 else C.YELLOW if cpu_val > 40 else C.RESET
                    except ValueError:
                        color = C.RESET
                    cprint(line, color)
            resultado["top_cpu"] = top_cpu.splitlines()

        # Top 10 por RAM
        cprint("\n  [ Top 10 Procesos por RAM ]", C.YELLOW)
        top_ram = run("ps aux --sort=-%mem | head -11 | awk 'NR>1 {printf \"  %-8s %-6s %-6s %s\\n\", $1, $3, $4, $11}'")
        if top_ram:
            cprint(f"  {'USUARIO':<8} {'%CPU':<6} {'%MEM':<6} PROCESO", C.CYAN)
            cprint(f"  {'─'*50}", C.CYAN)
            print(top_ram)
            resultado["top_ram"] = top_ram.splitlines()

        # Detectar procesos sospechosos: ocultos, corriendo desde /tmp, /dev/shm
        cprint("\n  [ Procesos Sospechosos (rutas anómalas) ]", C.YELLOW)
        sospechosos = run(
            "sudo ls -la /proc/*/exe 2>/dev/null | grep -E '/tmp/|/dev/shm/|/var/tmp/|deleted' | "
            "awk '{print $NF}' | sort -u | head -20"
        )
        if sospechosos:
            cprint("  ✗ PROCESOS EN RUTAS SOSPECHOSAS DETECTADOS:", C.RED, bold=True)
            for line in sospechosos.splitlines():
                cprint(f"  ⚠ {line}", C.RED)
            resultado["sospechosos"] = sospechosos.splitlines()
        else:
            cprint("  ✓ Sin procesos corriendo desde rutas sospechosas.", C.GREEN)

        # Procesos escuchando sin nombre de proceso visible
        cprint("\n  [ Procesos Zombie ]", C.YELLOW)
        zombies = run("ps aux | awk '$8 == \"Z\" {print $0}' | head -10")
        if zombies:
            cprint(f"  ⚠ Procesos zombie detectados:", C.YELLOW)
            print(zombies)
            resultado["zombies"] = zombies.splitlines()
        else:
            cprint("  ✓ Sin procesos zombie.", C.GREEN)

        return resultado

    @staticmethod
    def _srv_conexiones():
        subsection("CONEXIONES ACTIVAS — DETECCIÓN DE ANOMALÍAS")
        resultado = {"conexiones_establecidas": [], "sospechosas": [], "escuchando_externo": []}

        # Conexiones establecidas al exterior
        cprint("\n  [ Conexiones Establecidas al Exterior ]", C.YELLOW)
        conexiones = run(
            "sudo ss -tunp state established 2>/dev/null | "
            "grep -v '127.0.0.1\\|::1\\|10\\.' | head -30"
        )
        if conexiones:
            cprint(f"  {'PROTO':<6} {'LOCAL':<25} {'REMOTO':<25} PROCESO", C.CYAN)
            cprint(f"  {'─'*70}", C.CYAN)
            for line in conexiones.splitlines():
                # Marcar puertos conocidos como sospechosos si no son web
                sospechoso = any(p in line for p in [":4444", ":1234", ":31337", ":6666", ":9999", ":8888"])
                if sospechoso:
                    cprint(f"  ✗ {line}", C.RED)
                    resultado["sospechosas"].append(line.strip())
                else:
                    print(f"     {line}")
                resultado["conexiones_establecidas"].append(line.strip())
        else:
            cprint("  ✓ Sin conexiones externas activas.", C.GREEN)

        # Conexiones en estado TIME_WAIT / CLOSE_WAIT excesivas (posible DoS)
        cprint("\n  [ Estados de Conexión — Resumen ]", C.YELLOW)
        estados = run("sudo ss -tan 2>/dev/null | awk 'NR>1{print $1}' | sort | uniq -c | sort -rn | head -10")
        if estados:
            for line in estados.splitlines():
                parts = line.strip().split()
                try:
                    count = int(parts[0]) if parts else 0
                    estado = parts[1] if len(parts) > 1 else ""
                    color = C.RED if count > 100 and estado in ("TIME-WAIT", "CLOSE-WAIT") else C.RESET
                    cprint(f"  {line}", color)
                except (ValueError, IndexError):
                    print(f"  {line}")

        # Netstat resumen por IP remota (top conversaciones)
        cprint("\n  [ Top IPs Remotas con más Conexiones ]", C.YELLOW)
        top_ips = run(
            "sudo ss -tn state established 2>/dev/null | "
            "awk 'NR>1{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn | head -10"
        )
        if top_ips:
            for line in top_ips.splitlines():
                if line.strip():
                    parts = line.strip().split()
                    try:
                        count = int(parts[0]) if parts else 0
                        color = C.YELLOW if count > 5 else C.RESET
                        cprint(f"  {line}", color)
                    except ValueError:
                        print(f"  {line}")
        else:
            cprint("  Sin conexiones establecidas.", C.GRAY)

        if resultado["sospechosas"]:
            cprint(f"\n  ✗ {len(resultado['sospechosas'])} conexión(es) en puertos sospechosos detectadas.", C.RED, bold=True)
        else:
            cprint("\n  ✓ Sin conexiones en puertos asociados a C2 o backdoors.", C.GREEN)

        return resultado

    @staticmethod
    def server_audit():
        resultados = {}
        while True:
            section("AUDITORÍA DE SERVIDOR — MÓDULO 12")
            cprint("\n  [1]  Firewall — Estado y Reglas Activas", C.CYAN)
            cprint("  [2]  Archivos SUID / SGID Sospechosos", C.CYAN)
            cprint("  [3]  Accesos Fallidos y Últimos Logins", C.CYAN)
            cprint("  [4]  Procesos Anómalos (CPU / RAM / Rutas)", C.CYAN)
            cprint("  [5]  Conexiones Activas Sospechosas", C.CYAN)
            cprint("  [6]  Ejecutar Auditoría Completa (1→5)", C.YELLOW)
            cprint("  [7]  Exportar Resultados a JSON", C.GREEN)
            cprint("  [0]  Volver al Menú Principal\n", C.RED)

            op = input("  Seleccione: ").strip()

            if op == "0":
                break
            elif op == "1":
                resultados["firewall"] = Linux._srv_firewall()
                pause()
            elif op == "2":
                resultados["suid_sgid"] = Linux._srv_suid()
                pause()
            elif op == "3":
                resultados["accesos"] = Linux._srv_accesos()
                pause()
            elif op == "4":
                resultados["procesos"] = Linux._srv_procesos()
                pause()
            elif op == "5":
                resultados["conexiones"] = Linux._srv_conexiones()
                pause()
            elif op == "6":
                cprint("\n  [*] Iniciando auditoría completa de servidor...", C.CYAN)
                resultados["firewall"]   = Linux._srv_firewall()
                resultados["suid_sgid"] = Linux._srv_suid()
                resultados["accesos"]   = Linux._srv_accesos()
                resultados["procesos"]  = Linux._srv_procesos()
                resultados["conexiones"] = Linux._srv_conexiones()
                cprint("\n  ✓ Auditoría completa finalizada.", C.GREEN, bold=True)
                # Ofrecer export automático
                exportar = input("\n  ¿Exportar resultados a JSON? [s/N]: ").strip().lower()
                if exportar == "s":
                    Linux._srv_export(resultados)
                pause()
            elif op == "7":
                if not resultados:
                    cprint("\n  ⚠ No hay resultados aún. Ejecutá al menos un módulo primero.", C.YELLOW)
                else:
                    Linux._srv_export(resultados)
                pause()

    @staticmethod
    def _srv_export(resultados):
        export_path = os.path.join(
            _get_real_home(),
            f"neuroaudit_servidor_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.json"
        )
        try:
            with open(export_path, "w") as fp:
                json.dump({
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "host": platform.node(),
                    "kernel": platform.release(),
                    "resultados": resultados
                }, fp, indent=4, ensure_ascii=False)
            cprint(f"\n  ✓ Reporte exportado: {export_path}", C.GREEN)
        except Exception as e:
            cprint(f"\n  ⚠ Error al exportar: {e}", C.YELLOW)


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

def auto_update_neuroaudit():
    section("ACTUALIZAR SUITE NEUROAUDIT")
    cprint(f"\n  Versión actual : v{VERSION}", C.CYAN)
    cprint(f"  Fuente         : {GITHUB_RAW_URL}\n", C.GRAY)
    cprint("  [*] Descargando última versión desde GitHub...", C.CYAN)
    try:
        req = urllib.request.Request(
            GITHUB_RAW_URL,
            headers={"User-Agent": f"NeuroAudit/{VERSION}", "Cache-Control": "no-cache"}
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            nueva = r.read()

        # Validar que la descarga es un script Python válido de NeuroAudit
        if b"def main" not in nueva or b"NEUROAUDIT" not in nueva:
            cprint("  ✗ Descarga inválida o corrupta. Abortando sin cambios.", C.RED)
            return

        # Extraer versión nueva para mostrarla
        version_nueva = "desconocida"
        for line in nueva.decode("utf-8", errors="ignore").splitlines():
            if line.strip().startswith("VERSION"):
                try:
                    version_nueva = line.split('"')[1]
                except IndexError:
                    pass
                break

        if version_nueva == VERSION:
            cprint(f"  ✓ Ya tenés la última versión (v{VERSION}). No hay nada que actualizar.", C.GREEN)
            return

        cprint(f"  ✓ Nueva versión disponible: v{version_nueva}", C.GREEN)
        confirmar = input(f"\n  ¿Actualizar de v{VERSION} → v{version_nueva}? [s/N]: ").strip().lower()
        if confirmar != "s":
            cprint("  Actualización cancelada.", C.YELLOW)
            return

        # Escribir el nuevo script
        script_path = os.path.abspath(__file__)
        with open(script_path, "wb") as f:
            f.write(nueva)

        cprint(f"\n  ✓ NeuroAudit actualizado a v{version_nueva} correctamente.", C.GREEN, bold=True)
        cprint("  → Reiniciá NeuroAudit para usar la nueva versión.", C.CYAN)
        sys.exit(0)

    except urllib.error.URLError as e:
        cprint(f"  ✗ Sin conexión a GitHub: {e.reason}", C.RED)
    except PermissionError:
        cprint("  ✗ Sin permisos para escribir el archivo. Ejecutá con sudo.", C.RED)
    except Exception as e:
        cprint(f"  ✗ Error inesperado: {e}", C.RED)

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
    cprint("  [12] Auditoría de Servidor", C.RED)
    cprint("  [0]  Salir\n", C.RED)

def main():
    C.enable_windows_ansi()
    M = Linux
    acciones = {
        "1": M.sys_info, "2": M.maintenance, "3": M.vulnerability_audit, "4": M.disk_health,
        "5": lambda: (M.network_scan(), M.security_audit()), "6": M.event_report, "7": run_export,
        "8": M.software_inventory, "9": auto_update_neuroaudit, "10": M.permission_audit,
        "11": M.cve_scan, "12": M.server_audit
    }
    while True:
        show_banner(); show_menu()
        op = input(f"  Seleccione: ").strip()
        if op == "0": break
        if op in acciones: acciones[op](); pause()

if __name__ == "__main__":
    main()
