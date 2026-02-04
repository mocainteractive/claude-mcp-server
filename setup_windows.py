#!/usr/bin/env python3
"""
Script di setup automatico per Claude Desktop MCP su Windows
Installa Node.js, crea il file di configurazione e configura il server MCP
"""

import os
import json
import subprocess
import sys
from pathlib import Path
import urllib.request
import shutil
import winreg
import ctypes

def is_admin():
    """Controlla se lo script è eseguito come amministratore"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(command, check=True, shell=True):
    """Esegue un comando shell e ritorna il risultato"""
    try:
        result = subprocess.run(
            command,
            shell=shell,
            check=check,
            capture_output=True,
            text=True
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode

def check_python():
    """Controlla la versione di Python e se è aggiornata"""
    try:
        current_version = sys.version_info
        python_version = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
        print(f"🐍 Python corrente: {python_version}")

        if current_version >= (3, 8):
            print(f"✅ Python {python_version} è supportato")
            return True, python_version
        else:
            print(f"⚠️  Python {python_version} è troppo vecchio (minimo: 3.8)")
            return False, python_version
    except Exception as e:
        print(f"❌ Errore nel controllo Python: {e}")
        return False, "unknown"

def check_winget():
    """Controlla se winget è disponibile"""
    stdout, stderr, returncode = run_command("winget --version", check=False)
    return returncode == 0

def check_nodejs():
    """Controlla se Node.js è installato"""
    stdout, stderr, returncode = run_command("node --version", check=False)
    if returncode == 0:
        print(f"✅ Node.js già installato: {stdout}")
        return True
    return False

def install_nodejs_winget():
    """Installa Node.js tramite winget"""
    print("📦 Installando Node.js tramite winget...")
    stdout, stderr, returncode = run_command(
        "winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements",
        check=False
    )

    if returncode == 0:
        print("✅ Node.js installato con successo!")
        print("⚠️  Potrebbe essere necessario riavviare il terminale per usare Node.js")
        return True
    else:
        print(f"❌ Errore durante l'installazione via winget: {stderr}")
        return False

def install_nodejs_direct():
    """Scarica e installa Node.js direttamente"""
    print("📦 Scaricando Node.js installer...")

    # URL del download di Node.js LTS per Windows
    nodejs_url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
    installer_path = Path.home() / "Downloads" / "nodejs_installer.msi"

    try:
        print(f"⬇️  Download in corso da {nodejs_url}...")
        urllib.request.urlretrieve(nodejs_url, installer_path)
        print(f"✅ Installer scaricato in: {installer_path}")

        print("🔧 Avviando l'installazione di Node.js...")
        print("ℹ️  Segui le istruzioni dell'installer che si aprirà")

        # Avvia l'installer MSI
        os.startfile(str(installer_path))

        print("\n⚠️  IMPORTANTE:")
        print("1. Completa l'installazione di Node.js")
        print("2. Riavvia questo script dopo l'installazione")

        return False  # L'utente deve completare manualmente

    except Exception as e:
        print(f"❌ Errore durante il download: {e}")
        return False

def install_nodejs():
    """Installa Node.js su Windows"""
    # Prima prova con winget
    if check_winget():
        print("📦 Winget trovato, uso winget per installare Node.js...")
        if install_nodejs_winget():
            return True

    # Se winget fallisce, prova il download diretto
    print("⚠️  Winget non disponibile o fallito, provo il download diretto...")
    return install_nodejs_direct()

def get_claude_config_path():
    """Ottiene il percorso del file di configurazione di Claude Desktop su Windows"""
    # Su Windows, il percorso è %APPDATA%\Claude
    appdata = os.environ.get('APPDATA')
    if not appdata:
        appdata = str(Path.home() / "AppData" / "Roaming")

    config_dir = Path(appdata) / "Claude"
    config_file = config_dir / "claude_desktop_config.json"
    return config_dir, config_file

def create_claude_config():
    """Crea il file di configurazione Claude Desktop MCP con tutti i server"""
    config_dir, config_file = get_claude_config_path()

    # Configurazione MCP con TUTTI i server (5 in totale)
    mcp_config = {
        {
          "mcpServers": {
            "apify": {
              "command": "npx",
              "args": [
                "-y",
                "@apify/actors-mcp-server",
                "--tools",
                "actors,docs,curious_coder/facebook-ads-library-scraper,apify/rag-web-browser,amernas/google-ads-transparency-scraper,xtech/google-ad-transparency-scraper,apify/web-scraper"
              ],
              "env": {
                "APIFY_TOKEN": "INSERISCI LA CHIAVE API DEL TUO APIFY"
              }
            },
            "mcp-gsc-server-remote": {
              "command": "npx",
              "args": [
                "-y",
                "mcp-remote",
                "https://mcp-gsc-remote-moca.daniele-pisciottano.workers.dev/mcp",
                "--transport",
                "http-only"
              ]
            },
            "mcp-ga4-remote": {
              "command": "npx",
              "args": [
                "-y",
                "mcp-remote",
                "https://ga4-mcp-server.daniele-pisciottano.workers.dev/mcp",
                "--transport",
                "http-only"
              ]
            },
              "mcp-meta": {
              "command": "npx",
              "args": [
                "-y",
                "mcp-remote",
                "https://meta-mcp-server.daniele-pisciottano.workers.dev/mcp",
                "--transport",
                "http-only"
              ]
            },
            "mcp-reddit-remote": {
              "command": "npx",
              "args": [
                "-y",
                "mcp-remote",
                "https://reddit-mcp-server.daniele-pisciottano.workers.dev/mcp",
                "--transport",
                "http-only"
              ]
            },
            "dataforseo": {
              "command": "npx",
              "args": [
                "-y",
                "dataforseo-mcp-server"
              ],
              "env": {
                "DATAFORSEO_USERNAME": "PLACEHOLDER",
                "DATAFORSEO_PASSWORD": "PLACEHOLDER"
              }
            },
            "seozoom": {
              "command": "npx",
              "args": [
                "mcp-remote",
                "https://sznew.seozoom.it/mcp/",
                "--header",
                "Authorization: Bearer AK-6af2b0d268e62afd11fd51859e5d3b02"
              ],
              "disabled": true
            }, 
             "mcp-gads-remote": {
              "command": "npx",
              "args": [
                "-y",
                "mcp-remote",
                "https://google-ads-mcp-server.daniele-pisciottano.workers.dev/mcp",
                "--transport",
                "http-only"
              ]
            }
          }
        }

    try:
        # Crea la directory se non esiste
        config_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directory creata/verificata: {config_dir}")

        # Scrivi il file di configurazione
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(mcp_config, f, indent=2, ensure_ascii=False)

        print(f"✅ File di configurazione creato: {config_file}")
        print("\n📄 Contenuto del file di configurazione:")
        print(json.dumps(mcp_config, indent=2, ensure_ascii=False))

        return True

    except Exception as e:
        print(f"❌ Errore durante la creazione del file di configurazione: {e}")
        return False

def check_claude_desktop():
    """Controlla se Claude Desktop è installato su Windows"""
    # Possibili percorsi di installazione su Windows
    possible_paths = [
        Path(os.environ.get('LOCALAPPDATA', '')) / "Programs" / "Claude" / "Claude.exe",
        Path(os.environ.get('PROGRAMFILES', '')) / "Claude" / "Claude.exe",
        Path(os.environ.get('PROGRAMFILES(X86)', '')) / "Claude" / "Claude.exe",
        Path.home() / "AppData" / "Local" / "Programs" / "Claude" / "Claude.exe"
    ]

    for path in possible_paths:
        if path.exists():
            print(f"✅ Claude Desktop trovato in: {path}")
            return True

    print("⚠️  Claude Desktop non trovato nei percorsi standard")
    return False

def test_mcp_servers():
    """Testa se i server MCP sono raggiungibili"""
    print("🔍 Testando la connettività ai server MCP...")

    servers = {
        "Google Search Console": "https://mcp-gsc-remote-moca.daniele-pisciottano.workers.dev/mcp",
        "Meta": "https://meta-mcp-server.daniele-pisciottano.workers.dev/mcp",
        "Google Analytics 4": "https://mcp-ga4-remote-v2.daniele-pisciottano.workers.dev/mcp",
        "Reddit": "https://reddit-mcp-server.daniele-pisciottano.workers.dev/mcp",
        "Google Ads": "https://google-ads-mcp-server.daniele-pisciottano.workers.dev/mcp"
    }

    results = []

    for name, url in servers.items():
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.getcode() == 200:
                    print(f"✅ Server {name} raggiungibile")
                    results.append(True)
                else:
                    print(f"⚠️  Server {name} risponde con codice: {response.getcode()}")
                    results.append(False)
        except Exception as e:
            print(f"⚠️  Impossibile raggiungere il server {name}: {e}")
            results.append(False)

    return all(results)

def refresh_path():
    """Tenta di aggiornare il PATH nella sessione corrente"""
    try:
        # Legge il PATH dal registro di sistema
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                          r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment") as key:
            system_path = winreg.QueryValueEx(key, "Path")[0]

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            user_path = winreg.QueryValueEx(key, "Path")[0]

        os.environ['PATH'] = system_path + ";" + user_path
        print("✅ PATH aggiornato")
    except Exception as e:
        print(f"⚠️  Impossibile aggiornare il PATH automaticamente: {e}")

def main():
    print("🚀 Setup automatico Claude Desktop MCP per Windows")
    print("=" * 50)

    success_steps = []

    # 0. Controlla Python
    print("\n0️⃣ Controllo Python...")
    python_ok, current_python_version = check_python()
    if not python_ok:
        print("⚠️  Python non supportato.")
        print("ℹ️  Scarica Python 3.8+ da: https://www.python.org/downloads/")
        success_steps.append("⚠️  Python non aggiornato")
    else:
        success_steps.append(f"✅ Python {current_python_version} ok")

    # 1. Controlla e installa Node.js
    print("\n1️⃣ Controllo Node.js...")
    if not check_nodejs():
        if install_nodejs():
            # Aggiorna il PATH
            refresh_path()
            success_steps.append("✅ Node.js installato")
        else:
            print("❌ Fallimento nell'installazione di Node.js")
            print("ℹ️  Scarica manualmente da: https://nodejs.org/")
            success_steps.append("⚠️  Node.js non installato")
    else:
        success_steps.append("✅ Node.js già presente")

    # 2. Verifica npx
    print("\n2️⃣ Controllo npx...")
    stdout, stderr, returncode = run_command("npx --version", check=False)
    if returncode == 0:
        print(f"✅ npx disponibile: {stdout}")
        success_steps.append("✅ npx verificato")
    else:
        print("⚠️  npx non disponibile - potrebbe essere necessario riavviare il terminale")
        success_steps.append("⚠️  npx da verificare dopo riavvio")

    # 3. Controlla Claude Desktop
    print("\n3️⃣ Controllo Claude Desktop...")
    check_claude_desktop()

    # 4. Crea configurazione MCP
    print("\n4️⃣ Creazione file di configurazione...")
    if create_claude_config():
        success_steps.append("✅ File di configurazione creato (5 server MCP)")
    else:
        print("❌ Fallimento nella creazione del file di configurazione")
        return False

    # 5. Testa server MCP
    print("\n5️⃣ Test connettività server MCP...")
    if test_mcp_servers():
        success_steps.append("✅ Tutti i server MCP raggiungibili")
    else:
        success_steps.append("⚠️  Alcuni server MCP non raggiungibili (potrebbero funzionare comunque)")

    # 6. Istruzioni finali
    print("\n" + "=" * 50)
    print("📋 RIEPILOGO SETUP:")
    for step in success_steps:
        print(f"  {step}")

    print("\n🎉 Setup completato!")
    print("\n📝 SERVER MCP CONFIGURATI:")
    print("• Google Search Console (mcp-gsc-server-remote)")
    print("• Meta (mcp-meta)")
    print("• Google Analytics 4 (mcp-ga4-remote)")
    print("• Reddit (mcp-reddit-remote)")
    print("• Google Ads (mcp-gads-remote)")

    print("\n📥 PROSSIMI PASSI:")
    print("1. Assicurati che Claude Desktop sia installato da: https://claude.ai/download")
    if any("Node.js installato" in step for step in success_steps):
        print("2. IMPORTANTE: Riavvia il terminale/prompt per usare Node.js")
    print("3. Chiudi completamente Claude Desktop se è aperto")
    print("4. Riavvia Claude Desktop")
    print("5. I server MCP dovrebbero essere caricati automaticamente")
    print("6. Testa con questi comandi:")
    print("   • 'mostra le mie proprietà Google Search Console'")
    print("   • 'analizza le metriche Meta'")
    print("   • 'ottieni le metriche GA4 per la mia proprietà'")
    print("   • 'cerca su Reddit informazioni su Python'")
    print("   • 'mostra le campagne Google Ads attive'")

    config_dir, config_file = get_claude_config_path()
    print(f"\n📁 File di configurazione salvato in:")
    print(f"   {config_file}")

    return True

if __name__ == "__main__":
    try:
        main()
        input("\nPremi INVIO per chiudere...")
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        input("\nPremi INVIO per chiudere...")
        sys.exit(1)
