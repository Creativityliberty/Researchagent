"""
Module pour analyser et extraire des informations structurées des réponses LLM.
Fournit des fonctions pour parser les formats YAML, JSON, et texte.
"""

import yaml
import logging
import re

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_yaml_queries(response_text):
    """
    Extrait une liste de requêtes depuis un bloc YAML dans la réponse du LLM.
    
    Args:
        response_text (str): Texte de la réponse du LLM
        
    Returns:
        list: Liste des requêtes extraites ou liste vide en cas d'erreur
    """
    try:
        # Extraction du bloc YAML
        yaml_pattern = r"```yaml\s*(.*?)\s*```"
        yaml_match = re.search(yaml_pattern, response_text, re.DOTALL)
        
        if yaml_match:
            yaml_str = yaml_match.group(1)
        else:
            # Tentative alternative sans délimiteurs de code
            yaml_str = response_text
        
        # Chargement du YAML
        data = yaml.safe_load(yaml_str)
        
        # Extraction des requêtes
        if isinstance(data, dict) and "queries" in data:
            queries = data["queries"]
            if isinstance(queries, list):
                logger.info(f"Extraction réussie de {len(queries)} requêtes")
                return queries
        
        logger.warning("Format YAML non reconnu, tentative d'extraction directe")
        # Tentative d'extraction directe si le format n'est pas celui attendu
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return list(data.values())
        
        logger.warning("Aucune requête extraite du YAML")
        return []
        
    except Exception as e:
        logger.error(f"Erreur lors du parsing YAML: {e}")
        # Tentative de fallback: extraction de lignes commençant par des tirets
        try:
            lines = response_text.split('\n')
            queries = [line.strip('- ').strip() for line in lines if line.strip().startswith('-')]
            if queries:
                logger.info(f"Extraction de secours: {len(queries)} requêtes trouvées")
                return queries
        except Exception:
            pass
        
        return []


def extract_markdown_content(response_text):
    """
    Extrait le contenu Markdown d'une réponse LLM.
    
    Args:
        response_text (str): Texte de la réponse du LLM
        
    Returns:
        str: Contenu Markdown extrait
    """
    # Recherche de blocs de code Markdown
    md_pattern = r"```markdown\s*(.*?)\s*```"
    md_match = re.search(md_pattern, response_text, re.DOTALL)
    
    if md_match:
        logger.info("Bloc Markdown extrait avec succès")
        return md_match.group(1)
    
    # Si pas de bloc spécifique, on retourne le texte tel quel
    logger.info("Pas de bloc Markdown spécifique, utilisation du texte complet")
    return response_text


if __name__ == "__main__":
    # Test de parsing YAML
    test_yaml = """
    Voici quelques requêtes pour votre recherche:
    
    ```yaml
    queries:
      - impact de l'IA sur l'emploi
      - automatisation et marché du travail
      - intelligence artificielle transformation métiers
    ```
    
    J'espère que ces requêtes vous aideront.
    """
    
    queries = parse_yaml_queries(test_yaml)
    print("Requêtes extraites:", queries)
