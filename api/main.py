"""
Point d'entrée principal de l'API REST du Research Agent.
Configure FastAPI et inclut tous les routers.
"""

import os
import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html

from api.routers import research

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Création de l'application FastAPI
app = FastAPI(
    title="Research Agent API",
    description="API pour l'agent de recherche basé sur Pocket Flow et Gemini",
    version="1.0.0",
    docs_url=None,  # Désactivation de la documentation Swagger par défaut
    redoc_url=None  # Désactivation de la documentation ReDoc par défaut
)

# Configuration des CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Répertoire pour les templates HTML
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
os.makedirs(templates_dir, exist_ok=True)
templates = Jinja2Templates(directory=templates_dir)

# Répertoire pour les fichiers statiques
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Inclusion des routers
app.include_router(research.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root(request: Request):
    """Page d'accueil de l'API."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": "Research Agent API"}
    )


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Documentation Swagger UI personnalisée."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """Documentation ReDoc personnalisée."""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Gestionnaire personnalisé pour les erreurs 404."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": f"La ressource demandée '{request.url.path}' n'existe pas."}
    )


@app.exception_handler(500)
async def custom_500_handler(request: Request, exc):
    """Gestionnaire personnalisé pour les erreurs 500."""
    logger.error(f"Erreur interne du serveur: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Erreur interne du serveur. Veuillez réessayer plus tard."}
    )


if __name__ == "__main__":
    """
    Point d'entrée pour le lancement direct de l'API.
    En production, utilisez plutôt Uvicorn ou Gunicorn.
    """
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
