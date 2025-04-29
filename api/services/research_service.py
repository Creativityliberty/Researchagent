"""
Service de recherche pour l'API du Research Agent.
Gère l'exécution asynchrone des recherches et le suivi de leur état.
"""

import os
import uuid
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from api.models.schemas import ResearchStatus, ResearchRequest
from flow import research_flow

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Stockage en mémoire des recherches (à remplacer par une base de données dans un environnement de production)
research_store: Dict[str, Dict[str, Any]] = {}

# Répertoire pour stocker les résultats
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "results")
os.makedirs(RESULTS_DIR, exist_ok=True)


class ResearchProgressCallback:
    """Callback pour suivre la progression d'une recherche."""
    
    def __init__(self, research_id: str):
        self.research_id = research_id
        self.current_node = None
        self.progress = 0.0
    
    def update_progress(self, node_name: str, progress: float, message: str = ""):
        """Met à jour la progression de la recherche."""
        self.current_node = node_name
        self.progress = progress
        
        # Mise à jour du statut dans le store
        if self.research_id in research_store:
            research = research_store[self.research_id]
            research["status"] = self._map_node_to_status(node_name)
            research["progress"] = progress
            research["current_step"] = message or node_name
            research["updated_at"] = datetime.now().isoformat()
    
    def _map_node_to_status(self, node_name: str) -> ResearchStatus:
        """Mappe le nom du nœud au statut de la recherche."""
        status_mapping = {
            "PrepareSearchQueryNode": ResearchStatus.GENERATING_QUERY,
            "PerformSearchNode": ResearchStatus.SEARCHING,
            "ExtractUrlsNode": ResearchStatus.EXTRACTING_URLS,
            "ScrapeContentNode": ResearchStatus.SCRAPING,
            "FormatMarkdownNode": ResearchStatus.FORMATTING,
            "SaveToFileNode": ResearchStatus.SAVING,
            "EndNode": ResearchStatus.COMPLETED,
            "NoResultNode": ResearchStatus.NO_RESULTS
        }
        return status_mapping.get(node_name, ResearchStatus.PENDING)


async def create_research(request: ResearchRequest) -> str:
    """
    Crée une nouvelle recherche et la lance de manière asynchrone.
    
    Args:
        request: Les paramètres de la recherche
        
    Returns:
        str: L'identifiant unique de la recherche
    """
    # Génération d'un ID unique
    research_id = str(uuid.uuid4())
    
    # Création du nom de fichier de sortie si non spécifié
    output_filename = request.output_filename
    if not output_filename:
        safe_theme = "".join(c if c.isalnum() else "_" for c in request.theme)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"resultats_{safe_theme}_{timestamp}.md"
    
    # Chemin complet du fichier de sortie
    output_filepath = os.path.join(RESULTS_DIR, output_filename)
    
    # Initialisation de l'entrée dans le store
    research_store[research_id] = {
        "research_id": research_id,
        "theme": request.theme,
        "status": ResearchStatus.PENDING,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "progress": 0.0,
        "current_step": "Initialisation de la recherche",
        "output_filename": output_filename,
        "output_filepath": output_filepath,
        "max_results": request.max_results,
        "error_message": None,
        "completed_at": None,
        "markdown_content": None,
        "sources": []
    }
    
    # Lancement de la recherche en arrière-plan
    asyncio.create_task(run_research(research_id, request.theme, output_filepath, request.max_results))
    
    return research_id


async def run_research(research_id: str, theme: str, output_filepath: str, max_results: int = 5):
    """
    Exécute une recherche de manière asynchrone.
    
    Args:
        research_id: L'identifiant de la recherche
        theme: Le thème de la recherche
        output_filepath: Le chemin du fichier de sortie
        max_results: Le nombre maximum de résultats à retourner
    """
    logger.info(f"Démarrage de la recherche {research_id} sur le thème '{theme}'")
    
    # Création du callback de progression
    progress_callback = ResearchProgressCallback(research_id)
    
    try:
        # Configuration du shared store pour le flow
        shared = {
            "theme": theme,
            "output_filepath": output_filepath,
            "max_results": max_results,
            "progress_callback": progress_callback
        }
        
        # Exécution du flow dans un thread séparé pour ne pas bloquer la boucle asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: research_flow.run(shared))
        
        # Lecture du contenu du fichier généré
        if os.path.exists(output_filepath):
            with open(output_filepath, "r", encoding="utf-8") as f:
                markdown_content = f.read()
            
            # Extraction des sources (URLs) depuis le contenu Markdown
            sources = extract_sources_from_markdown(markdown_content)
            
            # Mise à jour du store avec les résultats
            research_store[research_id].update({
                "status": ResearchStatus.COMPLETED,
                "progress": 100.0,
                "current_step": "Recherche terminée avec succès",
                "completed_at": datetime.now().isoformat(),
                "markdown_content": markdown_content,
                "sources": sources
            })
            
            logger.info(f"Recherche {research_id} terminée avec succès")
        else:
            # Si le fichier n'existe pas, la recherche a échoué
            research_store[research_id].update({
                "status": ResearchStatus.NO_RESULTS,
                "progress": 100.0,
                "current_step": "Aucun résultat trouvé",
                "completed_at": datetime.now().isoformat(),
                "error_message": "Aucun résultat n'a été trouvé pour cette recherche"
            })
            
            logger.warning(f"Recherche {research_id} terminée sans résultats")
    
    except Exception as e:
        # En cas d'erreur, mise à jour du statut
        error_message = str(e)
        logger.error(f"Erreur lors de la recherche {research_id}: {error_message}")
        
        research_store[research_id].update({
            "status": ResearchStatus.FAILED,
            "progress": 100.0,
            "current_step": "Erreur lors de la recherche",
            "completed_at": datetime.now().isoformat(),
            "error_message": error_message
        })


def get_research_status(research_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère le statut d'une recherche.
    
    Args:
        research_id: L'identifiant de la recherche
        
    Returns:
        Dict ou None: Les informations sur la recherche ou None si non trouvée
    """
    return research_store.get(research_id)


def get_research_result(research_id: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les résultats d'une recherche terminée.
    
    Args:
        research_id: L'identifiant de la recherche
        
    Returns:
        Dict ou None: Les résultats de la recherche ou None si non trouvée/non terminée
    """
    research = research_store.get(research_id)
    
    if not research:
        return None
    
    # Vérification que la recherche est terminée
    if research["status"] not in [ResearchStatus.COMPLETED, ResearchStatus.NO_RESULTS, ResearchStatus.FAILED]:
        return None
    
    return research


def list_researches() -> List[Dict[str, Any]]:
    """
    Liste toutes les recherches.
    
    Returns:
        List: Liste des recherches
    """
    return list(research_store.values())


def extract_sources_from_markdown(markdown_content: str) -> List[Dict[str, str]]:
    """
    Extrait les sources (URLs) depuis le contenu Markdown.
    
    Args:
        markdown_content: Le contenu Markdown
        
    Returns:
        List: Liste des sources extraites
    """
    import re
    
    sources = []
    # Recherche des liens Markdown [texte](url)
    link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    
    for match in re.finditer(link_pattern, markdown_content):
        title, url = match.groups()
        # Éviter les doublons
        if url not in [s["url"] for s in sources]:
            sources.append({"url": url, "title": title})
    
    return sources
