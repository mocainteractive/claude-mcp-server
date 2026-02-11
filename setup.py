#!/usr/bin/env python3
"""
Script di setup automatico per Claude Desktop MCP su macOS
Installa Node.js, crea il file di configurazione e configura il server MCP
"""

import os
import json
import subprocess
import sys
from pathlib import Path
import urllib.request
import shutil

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

def check_homebrew():
    """Controlla se Homebrew è installato"""
    stdout, stderr, returncode = run_command("which brew", check=False)
    return returncode == 0

def install_homebrew():
    """Installa Homebrew"""
    print("🍺 Installando Homebrew...")
    install_script = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
    
    # Esegui l'installazione di Homebrew
    result = subprocess.run(install_script, shell=True)
    
    if result.returncode != 0:
        print("❌ Errore durante l'installazione di Homebrew")
        return False
    
    # Aggiungi Homebrew al PATH per le sessioni future
    homebrew_paths = [
        '/opt/homebrew/bin/brew',  # Apple Silicon
        '/usr/local/bin/brew'      # Intel
    ]
    
    for brew_path in homebrew_paths:
        if os.path.exists(brew_path):
            # Aggiungi al PATH della sessione corrente
            current_path = os.environ.get('PATH', '')
            brew_bin_dir = os.path.dirname(brew_path)
            if brew_bin_dir not in current_path:
                os.environ['PATH'] = f"{brew_bin_dir}:{current_path}"
            break
    
    print("✅ Homebrew installato con successo!")
    return True

def check_python():
    """Controlla la versione di Python e se è aggiornata"""
    try:
        import sys
        current_version = sys.version_info
        python_version = f"{current_version.major}.{current_version.minor}.{current_version.micro}"
        print(f"🐍 Python corrente: {python_version}")
        
        # Controlla se Python è almeno 3.8
        if current_version >= (3, 8):
            print(f"✅ Python {python_version} è supportato")
            return True, python_version
        else:
            print(f"⚠️  Python {python_version} è troppo vecchio (minimo: 3.8)")
            return False, python_version
    except Exception as e:
        print(f"❌ Errore nel controllo Python: {e}")
        return False, "unknown"

def get_latest_python_version():
    """Ottiene l'ultima versione stabile di Python disponibile"""
    try:
        # Controlla la versione disponibile su Homebrew
        stdout, stderr, returncode = run_command("brew info python@3.12", check=False)
        if returncode == 0:
            return "3.12"
        
        # Fallback alle versioni precedenti
        for version in ["3.11", "3.10", "3.9"]:
            stdout, stderr, returncode = run_command(f"brew info python@{version}", check=False)
            if returncode == 0:
                return version
        
        return "3.11"  # Default fallback
    except:
        return "3.11"

def install_python():
    """Installa o aggiorna Python tramite Homebrew"""
    print("🐍 Installando/aggiornando Python...")
    
    if not check_homebrew():
        print("❌ Homebrew non trovato. Installando prima Homebrew...")
        if not install_homebrew():
            return False
    
    # Ottieni l'ultima versione disponibile
    latest_version = get_latest_python_version()
    print(f"📦 Installando Python {latest_version}...")
    
    # Installa Python
    stdout, stderr, returncode = run_command(f"brew install python@{latest_version}")
    
    if returncode != 0:
        print(f"❌ Errore durante l'installazione di Python: {stderr}")
        # Prova con python generico
        print("🔄 Tentativo con 'brew install python'...")
        stdout, stderr, returncode = run_command("brew install python")
        
        if returncode != 0:
            print(f"❌ Errore anche con python generico: {stderr}")
            return False
    
    # Aggiorna i link simbolici
    run_command("brew link --overwrite python@" + latest_version, check=False)
    
    print("✅ Python installato/aggiornato con successo!")
    return True

def check_nodejs():
    """Controlla se Node.js è installato"""
    stdout, stderr, returncode = run_command("node --version", check=False)
    if returncode == 0:
        print(f"✅ Node.js già installato: {stdout}")
        return True
    return False

def install_nodejs():
    """Installa Node.js tramite Homebrew"""
    print("📦 Installando Node.js...")
    
    if not check_homebrew():
        print("❌ Homebrew non trovato. Installando prima Homebrew...")
        if not install_homebrew():
            return False
    
    stdout, stderr, returncode = run_command("brew install node")
    
    if returncode != 0:
        print(f"❌ Errore durante l'installazione di Node.js: {stderr}")
        return False
    
    # Verifica l'installazione
    if check_nodejs():
        return True
    else:
        print("❌ Node.js non sembra essere stato installato correttamente")
        return False

def get_claude_config_path():
    """Ottiene il percorso del file di configurazione di Claude Desktop"""
    home = Path.home()
    config_dir = home / "Library" / "Application Support" / "Claude"
    config_file = config_dir / "claude_desktop_config.json"
    return config_dir, config_file

def create_claude_config():
    """Crea il file di configurazione Claude Desktop MCP con tutti i server"""
    config_dir, config_file = get_claude_config_path()
    
    # Configurazione MCP con TUTTI i server (5 in totale)
    mcp_config = {
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
                "https://mcp-ga4-remote-v2.daniele-pisciottano.workers.dev/mcp",
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
              "disabled": True
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
    """Controlla se Claude Desktop è installato"""
    claude_app_path = "/Applications/Claude.app"
    if os.path.exists(claude_app_path):
        print("✅ Claude Desktop trovato in /Applications/Claude.app")
        return True
    else:
        print("⚠️  Claude Desktop non trovato in /Applications/Claude.app")
        return False

def test_mcp_servers():
    """Testa se i server MCP sono raggiungibili"""
    print("🔍 Testando la connettività ai server MCP...")
    
    servers = {
        "Google Search Console": "https://7b886198-gsc-mcp-remote.daniele-pisciottano.workers.dev/mcp",
        "SEMRush": "https://semrush-mcp-server.daniele-pisciottano.workers.dev/mcp",
        "Google Analytics 4": "https://ga4-mcp-server.daniele-pisciottano.workers.dev/mcp",
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

def main():
    print("🚀 Setup automatico Claude Desktop MCP per macOS")
    print("=" * 50)
    
    success_steps = []
    
    # 0. Controlla e installa Python se necessario
    print("\n0️⃣ Controllo Python...")
    python_ok, current_python_version = check_python()
    if not python_ok:
        print("⚠️  Python non aggiornato o non trovato. Installando...")
        if install_python():
            success_steps.append("✅ Python installato/aggiornato")
            print("🔄 Riavvia il terminale dopo l'installazione per usare la nuova versione")
        else:
            print("❌ Fallimento nell'installazione di Python")
            print("ℹ️  Lo script continuerà con la versione corrente...")
            success_steps.append("⚠️  Python non aggiornato (continua comunque)")
    else:
        success_steps.append(f"✅ Python {current_python_version} ok")
    
    # 1. Controlla e installa Node.js
    print("\n1️⃣ Controllo Node.js...")
    if not check_nodejs():
        if install_nodejs():
            success_steps.append("✅ Node.js installato")
        else:
            print("❌ Fallimento nell'installazione di Node.js")
            return False
    else:
        success_steps.append("✅ Node.js già presente")
    
    # 2. Verifica npx
    print("\n2️⃣ Controllo npx...")
    stdout, stderr, returncode = run_command("npx --version", check=False)
    if returncode == 0:
        print(f"✅ npx disponibile: {stdout}")
        success_steps.append("✅ npx verificato")
    else:
        print("❌ npx non disponibile")
        return False
    
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
    print("• SEMRush (semrush-remote)")
    print("• Google Analytics 4 (mcp-ga4-remote)")
    print("• Reddit (mcp-reddit-remote)")
    print("• Google Ads (mcp-gads-remote)")
    
    print("\n📥 PROSSIMI PASSI:")
    print("1. Assicurati che Claude Desktop sia installato da: https://claude.ai/download")
    if any("Python installato/aggiornato" in step for step in success_steps):
        print("2. IMPORTANTE: Riavvia il terminale per usare la nuova versione di Python")
        print("3. Chiudi completamente Claude Desktop se è aperto")
        print("4. Riavvia Claude Desktop")
    else:
        print("2. Chiudi completamente Claude Desktop se è aperto")
        print("3. Riavvia Claude Desktop")
    print("5. I server MCP dovrebbero essere caricati automaticamente")
    print("6. Testa con questi comandi:")
    print("   • 'mostra le mie proprietà Google Search Console'")
    print("   • 'analizza il dominio example.com con SEMRush'")
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
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrotto dall'utente")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Errore imprevisto: {e}")
        sys.exit(1)
