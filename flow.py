"""
Module définissant le flux de travail (workflow) de l'agent de recherche.
Connecte les nœuds dans l'ordre souhaité pour créer le pipeline complet.
"""

import logging
from pocketflow import Flow
from nodes import (
    PrepareSearchQueryNode,
    PerformSearchNode,
    ExtractUrlsNode,
    ScrapeContentNode,
    FormatMarkdownNode,
    SaveToFileNode,
    EndNode,
    NoResultNode
)

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_research_flow():
    """
    Crée et retourne le flux de travail de l'agent de recherche.
    
    Returns:
        Flow: L'instance du flux de travail configuré
    """
    logger.info("Création du flux de travail de l'agent de recherche")
    
    # Création des nœuds
    prepare_query_node = PrepareSearchQueryNode()
    search_node = PerformSearchNode()
    extract_urls_node = ExtractUrlsNode()
    scrape_content_node = ScrapeContentNode()  # BatchNode
    format_markdown_node = FormatMarkdownNode()
    save_file_node = SaveToFileNode()
    end_node = EndNode()  # Nœud de fin succès
    no_result_node = NoResultNode()  # Nœud de fin sans résultat
    
    # Connexion des nœuds en séquence
    prepare_query_node >> search_node
    search_node >> extract_urls_node
    
    # Gestion du cas où aucune URL n'est extraite
    extract_urls_node - "default" >> scrape_content_node  # Si URLs extraites, on continue
    extract_urls_node - "no_urls" >> no_result_node  # Si pas d'URLs, on va au nœud de fin sans résultat
    
    # Gestion du cas où aucun contenu n'est scrapé
    scrape_content_node - "default" >> format_markdown_node  # Si contenu scrapé, on continue
    scrape_content_node - "no_content" >> no_result_node  # Si pas de contenu, on va au nœud de fin sans résultat
    
    # Suite du flux normal
    format_markdown_node >> save_file_node
    
    # Gestion de la fin du flux après la sauvegarde
    save_file_node - "success" >> end_node  # Si sauvegarde réussie
    save_file_node - "failure" >> no_result_node  # Si échec de sauvegarde
    
    # Création du flux complet
    flow = Flow(start=prepare_query_node)
    
    logger.info("Flux de travail créé avec succès")
    return flow


# Création de l'instance du flux
research_flow = create_research_flow()


if __name__ == "__main__":
    # Test simple du flux
    print("Test du flux de travail de l'agent de recherche")
    
    # Configuration du shared store pour le test
    shared = {
        "theme": "Impact de l'IA sur l'emploi",
        "output_filepath": "test_resultats.md"
    }
    
    # Exécution du flux
    research_flow.run(shared)
    
    print("Test terminé")
