"""
Routes pour la gestion des recherches dans l'API du Research Agent.
"""

from typing import List
from fastapi import APIRouter, HTTPException, status, Query, Path
from api.models.schemas import (
    ResearchRequest,
    ResearchResponse,
    ResearchStatusResponse,
    ResearchResult,
    ResearchStatus
)
from api.services import research_service

# Création du router
router = APIRouter(
    prefix="/research",
    tags=["research"],
    responses={404: {"description": "Recherche non trouvée"}}
)


@router.post(
    "/",
    response_model=ResearchResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Lancer une nouvelle recherche",
    description="Crée et lance une nouvelle recherche basée sur le thème fourni."
)
async def create_research(request: ResearchRequest):
    """
    Lance une nouvelle recherche basée sur le thème fourni.
    
    La recherche s'exécute de manière asynchrone et retourne immédiatement un identifiant
    qui peut être utilisé pour suivre la progression et récupérer les résultats.
    """
    research_id = await research_service.create_research(request)
    
    # Récupération des informations initiales
    research = research_service.get_research_status(research_id)
    
    return {
        "research_id": research_id,
        "theme": research["theme"],
        "status": research["status"],
        "created_at": research["created_at"]
    }


@router.get(
    "/{research_id}/status",
    response_model=ResearchStatusResponse,
    summary="Vérifier le statut d'une recherche",
    description="Récupère le statut actuel d'une recherche en cours ou terminée."
)
async def get_research_status(
    research_id: str = Path(..., description="Identifiant de la recherche")
):
    """
    Récupère le statut actuel d'une recherche en cours ou terminée.
    
    Retourne des informations détaillées sur l'état d'avancement de la recherche,
    y compris l'étape actuelle et le pourcentage de progression.
    """
    research = research_service.get_research_status(research_id)
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recherche non trouvée avec l'ID: {research_id}"
        )
    
    return {
        "research_id": research["research_id"],
        "theme": research["theme"],
        "status": research["status"],
        "created_at": research["created_at"],
        "updated_at": research["updated_at"],
        "progress": research["progress"],
        "current_step": research["current_step"],
        "output_filename": research["output_filename"],
        "error_message": research["error_message"]
    }


@router.get(
    "/{research_id}/results",
    response_model=ResearchResult,
    summary="Récupérer les résultats d'une recherche",
    description="Récupère les résultats complets d'une recherche terminée."
)
async def get_research_results(
    research_id: str = Path(..., description="Identifiant de la recherche")
):
    """
    Récupère les résultats complets d'une recherche terminée.
    
    Cette endpoint ne retourne des résultats que si la recherche est terminée
    (statut 'completed', 'no_results' ou 'failed'). Sinon, une erreur 404 est retournée.
    """
    research = research_service.get_research_result(research_id)
    
    if not research:
        # Vérification si la recherche existe mais n'est pas terminée
        status_info = research_service.get_research_status(research_id)
        if status_info:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"La recherche {research_id} est en cours (statut: {status_info['status']}). Veuillez réessayer plus tard."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Recherche non trouvée avec l'ID: {research_id}"
            )
    
    return {
        "research_id": research["research_id"],
        "theme": research["theme"],
        "status": research["status"],
        "created_at": research["created_at"],
        "completed_at": research["completed_at"],
        "output_filename": research["output_filename"],
        "markdown_content": research["markdown_content"] or "",
        "sources": research["sources"]
    }


@router.get(
    "/",
    response_model=List[ResearchResponse],
    summary="Lister toutes les recherches",
    description="Récupère la liste de toutes les recherches avec leur statut."
)
async def list_researches(
    status: ResearchStatus = Query(None, description="Filtrer par statut")
):
    """
    Récupère la liste de toutes les recherches avec leur statut.
    
    Peut être filtré par statut en utilisant le paramètre de requête 'status'.
    """
    researches = research_service.list_researches()
    
    # Filtrage par statut si spécifié
    if status:
        researches = [r for r in researches if r["status"] == status]
    
    # Formatage de la réponse
    return [
        {
            "research_id": r["research_id"],
            "theme": r["theme"],
            "status": r["status"],
            "created_at": r["created_at"]
        }
        for r in researches
    ]
