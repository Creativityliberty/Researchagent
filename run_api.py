"""
Script pour lancer l'API REST du Research Agent.
"""

import os
import logging
import uvicorn
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()


def main():
    """
    Fonction principale pour lancer l'API.
    """
    # Vérification des clés API
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.warning("GOOGLE_API_KEY non définie. L'agent utilisera des fonctionnalités limitées.")
    
    if not os.environ.get("SERPAPI_API_KEY"):
        logger.warning("SERPAPI_API_KEY non définie. L'agent utilisera des résultats de recherche simulés.")
    
    # Port de l'API (modifiable en cas de conflit)
    port = 8080
    
    # Affichage des informations de démarrage
    print("\n" + "="*50)
    print("🚀 Démarrage de l'API Research Agent")
    print("="*50)
    print("📚 Documentation disponible sur:")
    print(f"   - http://localhost:{port}/docs (Swagger UI)")
    print(f"   - http://localhost:{port}/redoc (ReDoc)")
    print("-"*50)
    
    # Lancement de l'API
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
