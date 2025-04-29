"""
Module pour effectuer des recherches web via SerpAPI.
Fournit des fonctions pour rechercher des informations en ligne.
"""

import os
import logging
from dotenv import load_dotenv
import time

# Tentative d'importation de SerpAPI
try:
    from serpapi import GoogleSearch
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Récupération de la clé API
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

if not SERPAPI_API_KEY:
    logger.warning("SERPAPI_API_KEY non définie dans les variables d'environnement.")


def search_web(query, num_results=5):
    """
    Effectue une recherche web via SerpAPI.
    
    Args:
        query (str): La requête de recherche
        num_results (int): Nombre de résultats à retourner
        
    Returns:
        list: Liste de dictionnaires contenant les résultats
              [{'title': '...', 'url': '...', 'snippet': '...'}]
    """
    if not SERPAPI_API_KEY:
        logger.error("Impossible d'effectuer la recherche: SERPAPI_API_KEY non définie.")
        return _fallback_search(query, num_results)
    
    if not SERPAPI_AVAILABLE:
        logger.error("Module serpapi non disponible. Utilisez 'pip install serpapi'.")
        return _fallback_search(query, num_results)
    
    logger.info(f"Recherche web pour la requête: '{query}'")
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "num": num_results
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Extraction des résultats organiques
        organic_results = results.get("organic_results", [])
        
        # Formatage des résultats
        formatted_results = []
        for result in organic_results[:num_results]:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", "")
            })
        
        logger.info(f"Recherche réussie: {len(formatted_results)} résultats trouvés")
        return formatted_results
        
    except Exception as e:
        logger.error(f"Erreur lors de la recherche SerpAPI: {e}")
        return _fallback_search(query, num_results)


def _fallback_search(query, num_results=5):
    """
    Fonction de repli qui simule des résultats de recherche.
    À utiliser uniquement pour les tests ou en cas d'erreur avec l'API réelle.
    
    Args:
        query (str): La requête de recherche
        num_results (int): Nombre de résultats à retourner
        
    Returns:
        list: Liste de dictionnaires simulant des résultats de recherche
    """
    logger.warning(f"Utilisation de la recherche simulée pour: '{query}'")
    
    # Simulation d'un délai réseau
    time.sleep(1)
    
    # Résultats simulés pour certaines requêtes courantes
    simulated_results = []
    
    if "impact de l'IA" in query.lower() or "intelligence artificielle" in query.lower():
        simulated_results = [
            {
                "title": "L'impact de l'IA sur le monde du travail - Harvard Business Review",
                "url": "https://hbr.org/impact-ia-travail",
                "snippet": "Comment l'intelligence artificielle transforme les métiers et crée de nouvelles opportunités..."
            },
            {
                "title": "IA et emploi: mythes et réalités - MIT Technology Review",
                "url": "https://www.technologyreview.com/ia-emploi",
                "snippet": "Une analyse des effets réels de l'automatisation sur le marché du travail..."
            },
            {
                "title": "Les métiers qui résisteront à l'IA - Le Monde",
                "url": "https://www.lemonde.fr/metiers-ia",
                "snippet": "Quels sont les secteurs et compétences qui resteront essentiellement humains..."
            },
            {
                "title": "Comment l'IA redéfinit les compétences professionnelles - Forbes",
                "url": "https://www.forbes.fr/ia-competences",
                "snippet": "Les nouvelles compétences requises à l'ère de l'intelligence artificielle..."
            },
            {
                "title": "IA générative: révolution ou évolution du travail? - McKinsey",
                "url": "https://www.mckinsey.com/ia-generative-travail",
                "snippet": "Étude sur l'impact des modèles génératifs sur la productivité et l'emploi..."
            }
        ]
    else:
        # Génération de résultats génériques basés sur la requête
        for i in range(min(5, num_results)):
            simulated_results.append({
                "title": f"Résultat {i+1} pour {query}",
                "url": f"https://example.com/result-{i+1}",
                "snippet": f"Ceci est un extrait simulé pour le résultat {i+1} concernant {query}..."
            })
    
    return simulated_results[:num_results]


if __name__ == "__main__":
    # Test de la fonction de recherche
    test_query = "impact de l'IA sur l'emploi"
    results = search_web(test_query, 3)
    
    print(f"Résultats pour '{test_query}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Extrait: {result['snippet'][:100]}...")
        print()
