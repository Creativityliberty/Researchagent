"""
Modèles de données pour l'API du Research Agent.
Définit les schémas Pydantic pour la validation des entrées/sorties.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ResearchStatus(str, Enum):
    """Statuts possibles d'une recherche."""
    PENDING = "pending"
    GENERATING_QUERY = "generating_query"
    SEARCHING = "searching"
    EXTRACTING_URLS = "extracting_urls"
    SCRAPING = "scraping"
    FORMATTING = "formatting"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_RESULTS = "no_results"


class ResearchRequest(BaseModel):
    """Modèle pour une demande de recherche."""
    theme: str = Field(..., description="Thème de recherche", min_length=3, max_length=200)
    output_filename: Optional[str] = Field(None, description="Nom du fichier de sortie (optionnel)")
    max_results: Optional[int] = Field(5, description="Nombre maximum de résultats à retourner", ge=1, le=20)
    
    class Config:
        json_schema_extra = {
            "example": {
                "theme": "Impact de l'IA sur l'emploi",
                "output_filename": "resultats_ia_emploi.md",
                "max_results": 5
            }
        }


class ResearchResponse(BaseModel):
    """Modèle pour la réponse à une demande de recherche."""
    research_id: str = Field(..., description="Identifiant unique de la recherche")
    theme: str = Field(..., description="Thème de la recherche")
    status: ResearchStatus = Field(..., description="Statut actuel de la recherche")
    created_at: datetime = Field(..., description="Date et heure de création de la recherche")
    
    class Config:
        json_schema_extra = {
            "example": {
                "research_id": "f8e7d6c5-b4a3-2c1d-0e9f-8g7h6i5j4k3l",
                "theme": "Impact de l'IA sur l'emploi",
                "status": "pending",
                "created_at": "2025-04-29T15:30:00Z"
            }
        }


class ResearchStatusResponse(ResearchResponse):
    """Modèle pour la réponse détaillée sur le statut d'une recherche."""
    updated_at: datetime = Field(..., description="Date et heure de la dernière mise à jour")
    progress: float = Field(..., description="Progression de la recherche (0-100%)", ge=0, le=100)
    current_step: str = Field(..., description="Étape actuelle du processus")
    output_filename: Optional[str] = Field(None, description="Nom du fichier de sortie")
    error_message: Optional[str] = Field(None, description="Message d'erreur en cas d'échec")
    
    class Config:
        json_schema_extra = {
            "example": {
                "research_id": "f8e7d6c5-b4a3-2c1d-0e9f-8g7h6i5j4k3l",
                "theme": "Impact de l'IA sur l'emploi",
                "status": "scraping",
                "created_at": "2025-04-29T15:30:00Z",
                "updated_at": "2025-04-29T15:32:15Z",
                "progress": 60.0,
                "current_step": "Extraction du contenu des URLs 3/5",
                "output_filename": "resultats_ia_emploi.md",
                "error_message": None
            }
        }


class ResearchResult(BaseModel):
    """Modèle pour les résultats d'une recherche."""
    research_id: str = Field(..., description="Identifiant unique de la recherche")
    theme: str = Field(..., description="Thème de la recherche")
    status: ResearchStatus = Field(..., description="Statut final de la recherche")
    created_at: datetime = Field(..., description="Date et heure de création de la recherche")
    completed_at: datetime = Field(..., description="Date et heure de fin de la recherche")
    output_filename: str = Field(..., description="Nom du fichier de sortie")
    markdown_content: str = Field(..., description="Contenu Markdown des résultats")
    sources: List[Dict[str, Any]] = Field(..., description="Sources utilisées pour la recherche")
    
    class Config:
        json_schema_extra = {
            "example": {
                "research_id": "f8e7d6c5-b4a3-2c1d-0e9f-8g7h6i5j4k3l",
                "theme": "Impact de l'IA sur l'emploi",
                "status": "completed",
                "created_at": "2025-04-29T15:30:00Z",
                "completed_at": "2025-04-29T15:35:42Z",
                "output_filename": "resultats_ia_emploi.md",
                "markdown_content": "# Résultats de recherche: Impact de l'IA sur l'emploi\n\n...",
                "sources": [
                    {"url": "https://example.com/article1", "title": "L'IA et l'emploi"},
                    {"url": "https://example.org/article2", "title": "Futur du travail"}
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Modèle pour les réponses d'erreur."""
    detail: str = Field(..., description="Description de l'erreur")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Recherche non trouvée avec l'ID spécifié"
            }
        }
