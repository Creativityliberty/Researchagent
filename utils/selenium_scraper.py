"""
Module pour scraper le contenu des pages web avec Selenium.
Fournit des fonctions robustes pour extraire le contenu textuel des URLs.
"""

import logging
import time
from urllib.parse import urlparse

# Tentative d'importation de Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, WebDriverException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Tentative d'importation de BeautifulSoup (fallback)
try:
    import requests
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def scrape_with_selenium(url, max_content_length=2000, timeout=10):
    """
    Scrape le contenu d'une page web en utilisant Selenium.
    
    Args:
        url (str): L'URL de la page à scraper
        max_content_length (int): Longueur maximale du contenu à retourner
        timeout (int): Délai d'attente maximum en secondes
        
    Returns:
        str: Le contenu textuel extrait de la page
    """
    if not SELENIUM_AVAILABLE:
        logger.warning("Selenium non disponible. Utilisation du fallback BeautifulSoup.")
        return scrape_with_beautifulsoup(url, max_content_length)
    
    logger.info(f"Scraping de l'URL avec Selenium: {url}")
    
    # Configuration des options Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    try:
        # Initialisation du driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(timeout)
        
        # Accès à l'URL
        driver.get(url)
        
        # Attente du chargement de la page
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Extraction du contenu selon le type de site
        domain = urlparse(url).netloc
        content = ""
        
        # Stratégies d'extraction spécifiques par domaine
        if "medium.com" in domain:
            content = _extract_medium_content(driver)
        elif "wikipedia.org" in domain:
            content = _extract_wikipedia_content(driver)
        elif "github.com" in domain:
            content = _extract_github_content(driver)
        else:
            # Stratégie générique
            content = _extract_generic_content(driver)
        
        # Nettoyage et limitation de la taille
        content = content.strip()
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        logger.info(f"Contenu extrait avec succès ({len(content)} caractères)")
        return content
        
    except TimeoutException:
        logger.error(f"Timeout lors du chargement de {url}")
        return f"Erreur: Timeout lors du chargement de la page {url}"
    except WebDriverException as e:
        logger.error(f"Erreur Selenium: {e}")
        # Fallback à BeautifulSoup en cas d'erreur Selenium
        return scrape_with_beautifulsoup(url, max_content_length)
    except Exception as e:
        logger.error(f"Erreur inattendue lors du scraping: {e}")
        return f"Erreur de scraping: {e}"
    finally:
        # Fermeture du driver
        try:
            if 'driver' in locals():
                driver.quit()
        except Exception:
            pass


def _extract_generic_content(driver):
    """Extrait le contenu d'une page web générique."""
    # Tentative d'extraction du contenu principal
    main_selectors = [
        "article", "main", ".content", "#content", ".post-content",
        ".article-content", ".entry-content", ".post-body"
    ]
    
    # Essai des sélecteurs principaux
    for selector in main_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return " ".join([el.text for el in elements])
        except Exception:
            continue
    
    # Si aucun sélecteur principal ne fonctionne, extraction des paragraphes
    try:
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        return " ".join([p.text for p in paragraphs if p.text.strip()])
    except Exception:
        pass
    
    # Dernier recours: tout le texte du body
    try:
        return driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return ""


def _extract_medium_content(driver):
    """Extrait le contenu spécifique aux articles Medium."""
    try:
        # Titre
        title = ""
        title_element = driver.find_elements(By.TAG_NAME, "h1")
        if title_element:
            title = title_element[0].text
        
        # Contenu
        paragraphs = driver.find_elements(By.TAG_NAME, "p")
        content = " ".join([p.text for p in paragraphs if p.text.strip()])
        
        return f"{title}\n\n{content}"
    except Exception as e:
        logger.warning(f"Erreur lors de l'extraction Medium: {e}")
        return _extract_generic_content(driver)


def _extract_wikipedia_content(driver):
    """Extrait le contenu spécifique aux articles Wikipedia."""
    try:
        # Titre
        title = driver.find_element(By.ID, "firstHeading").text
        
        # Contenu
        content_div = driver.find_element(By.ID, "mw-content-text")
        paragraphs = content_div.find_elements(By.TAG_NAME, "p")
        content = " ".join([p.text for p in paragraphs if p.text.strip()])
        
        return f"{title}\n\n{content}"
    except Exception as e:
        logger.warning(f"Erreur lors de l'extraction Wikipedia: {e}")
        return _extract_generic_content(driver)


def _extract_github_content(driver):
    """Extrait le contenu spécifique aux pages GitHub."""
    try:
        # README ou autre contenu de repo
        readme = driver.find_elements(By.CSS_SELECTOR, ".markdown-body")
        if readme:
            return readme[0].text
        
        # Page de profil
        profile = driver.find_elements(By.CSS_SELECTOR, ".js-profile-editable-area")
        if profile:
            return profile[0].text
        
        return _extract_generic_content(driver)
    except Exception as e:
        logger.warning(f"Erreur lors de l'extraction GitHub: {e}")
        return _extract_generic_content(driver)


def scrape_with_beautifulsoup(url, max_content_length=2000):
    """
    Méthode de fallback utilisant BeautifulSoup pour scraper le contenu.
    
    Args:
        url (str): L'URL de la page à scraper
        max_content_length (int): Longueur maximale du contenu à retourner
        
    Returns:
        str: Le contenu textuel extrait de la page
    """
    if not BEAUTIFULSOUP_AVAILABLE:
        logger.error("BeautifulSoup non disponible. Impossible de scraper.")
        return "Erreur: Modules de scraping non disponibles."
    
    logger.info(f"Fallback: Scraping de l'URL avec BeautifulSoup: {url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
    }
    
    try:
        # Récupération de la page
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parsing avec BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Suppression des éléments non pertinents
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # Extraction du contenu
        paragraphs = soup.find_all('p')
        content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        # Limitation de la taille
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        logger.info(f"Contenu extrait avec BeautifulSoup ({len(content)} caractères)")
        return content
        
    except Exception as e:
        logger.error(f"Erreur lors du scraping avec BeautifulSoup: {e}")
        return f"Erreur de scraping: {e}"


if __name__ == "__main__":
    # Test du scraper
    test_url = "https://en.wikipedia.org/wiki/Artificial_intelligence"
    print(f"Test de scraping pour: {test_url}")
    
    content = scrape_with_selenium(test_url)
    print(f"Contenu extrait ({len(content)} caractères):")
    print(content[:500] + "..." if len(content) > 500 else content)
