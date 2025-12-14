# =========================================================================
# AUTOMATION JUSTPLAY - GITHUB ACTIONS
# =========================================================================

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import time
import os
from datetime import datetime

# Configuration
URL_SITE = "https://justplay.cyou/"
TEMPS_LECTURE_VIDEO = 60
TEMPS_ATTENTE_GENERALE = 5
MAX_CYCLES = 1  # 1 cycle par exécution (GitHub Actions a une limite de temps)

# Créer dossier logs
os.makedirs('logs', exist_ok=True)

# Fichier de log
log_file = f"logs/execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log_message(message):
    """Écrit dans le fichier de log et affiche dans la console"""
    print(message)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(message + '\n')

# Configuration Chrome
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-gpu")

driver = None

log_message("="*70)
log_message(f"🚀 DÉMARRAGE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
log_message("="*70)

try:
    log_message("\n📦 Initialisation du navigateur Chrome...")
    driver = webdriver.Chrome(options=chrome_options)
    
    # Configuration stealth
    stealth(driver,
            languages=["fr-FR", "fr"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True)
    
    log_message("✅ Navigateur initialisé")
    
    for cycle in range(MAX_CYCLES):
        log_message(f"\n{'='*70}")
        log_message(f"CYCLE {cycle + 1}/{MAX_CYCLES}")
        log_message("="*70)
        
        # Navigation
        log_message(f"\n🌐 Navigation vers : {URL_SITE}")
        driver.get(URL_SITE)
        time.sleep(TEMPS_ATTENTE_GENERALE)
        
        # Récupération des liens
        all_links = driver.find_elements(By.XPATH, "//a[@href]")
        game_urls = set()
        
        for link in all_links:
            href = link.get_attribute('href')
            if href and href.startswith(URL_SITE + "game/"):
                game_urls.add(href)
        
        urls_to_visit = list(game_urls)
        log_message(f"✅ {len(urls_to_visit)} URLs de jeux trouvées")
        
        if not urls_to_visit:
            log_message("⚠️  Aucun jeu trouvé")
            continue
        
        # Traitement des jeux
        for i, game_url in enumerate(urls_to_visit):
            log_message(f"\n[Jeu {i + 1}/{len(urls_to_visit)}] 🎮 {game_url}")
            
            try:
                driver.get(game_url)
                time.sleep(TEMPS_ATTENTE_GENERALE)
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
                
                # Localiser la vidéo
                walkthrough_container = driver.find_element(By.CLASS_NAME, "game-walkthrough")
                video_element = walkthrough_container.find_element(By.XPATH, ".//iframe | .//video")
                
                log_message(f"   📹 Vidéo trouvée (Tag: <{video_element.tag_name}>)")
                
                # Lancer la lecture
                if video_element.tag_name == "video":
                    driver.execute_script("arguments[0].play();", video_element)
                elif video_element.tag_name == "iframe":
                    video_element.click()
                
                log_message(f"   ▶️  Lecture pendant {TEMPS_LECTURE_VIDEO}s...")
                time.sleep(TEMPS_LECTURE_VIDEO)
                log_message("   ✅ Terminé")
                
            except Exception as e:
                log_message(f"   ❌ Erreur: {str(e)[:100]}")
                continue
        
        log_message(f"\n✅ Cycle {cycle + 1} terminé - {len(urls_to_visit)} jeux traités")
    
    log_message(f"\n{'='*70}")
    log_message(f"🎉 EXÉCUTION TERMINÉE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("="*70)

except KeyboardInterrupt:
    log_message("\n⚠️  Interruption manuelle")

except Exception as e:
    log_message(f"\n❌ ERREUR FATALE: {e}")
    import traceback
    log_message(traceback.format_exc())

finally:
    if driver is not None:
        driver.quit()
        log_message("\n🔒 Navigateur fermé")
    
    log_message("\n✨ Script terminé")
    
print(f"\n📄 Log sauvegardé : {log_file}")
