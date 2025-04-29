"""
Point d'entrée principal de l'agent de recherche.
Configure les données d'entrée et exécute le flux de travail.
"""

import os
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
from flow import research_flow

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('research_agent.log')
    ]
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()


def main():
    """
    Fonction principale qui configure et exécute l'agent de recherche.
    Gère les arguments en ligne de commande et initialise le flux.
    """
    # Configuration des arguments en ligne de commande
    parser = argparse.ArgumentParser(description='Agent de recherche basé sur Pocket Flow')
    parser.add_argument('--theme', '-t', type=str, help='Thème de recherche')
    parser.add_argument('--output', '-o', type=str, help='Chemin du fichier de sortie')
    parser.add_argument('--verbose', '-v', action='store_true', help='Mode verbeux (debug)')
    args = parser.parse_args()
    
    # Configuration du niveau de logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Mode verbeux activé")
    
    # Vérification des clés API
    if not os.environ.get("GOOGLE_API_KEY"):
        logger.warning("GOOGLE_API_KEY non définie. L'agent utilisera des fonctionnalités limitées.")
    
    if not os.environ.get("SERPAPI_API_KEY"):
        logger.warning("SERPAPI_API_KEY non définie. L'agent utilisera des résultats de recherche simulés.")
    
    # Demande interactive du thème si non fourni
    theme = args.theme
    if not theme:
        theme = input("Entrez le thème de recherche: ")
    
    # Génération du nom de fichier de sortie si non fourni
    output_filepath = args.output
    if not output_filepath:
        safe_theme = "".join(c if c.isalnum() else "_" for c in theme)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filepath = f"resultats_{safe_theme}_{timestamp}.md"
    
    # Configuration du shared store
    shared = {
        "theme": theme,
        "output_filepath": output_filepath
    }
    
    # Affichage des informations de démarrage
    print("\n" + "="*50)
    print(f"🔍 Agent de recherche - Démarrage")
    print("="*50)
    print(f"📚 Thème: {theme}")
    print(f"📄 Fichier de sortie: {output_filepath}")
    print("-"*50)
    
    # Exécution du flux de travail
    logger.info(f"Démarrage du flux avec thème: '{theme}'")
    research_flow.run(shared)
    
    # Affichage du résultat
    if os.path.exists(output_filepath):
        print("\n" + "="*50)
        print(f"✅ Recherche terminée avec succès!")
        print(f"📄 Résultats sauvegardés dans: {output_filepath}")
        print("="*50)
    else:
        print("\n" + "="*50)
        print(f"⚠️ La recherche n'a pas produit de résultats.")
        print("="*50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interruption utilisateur. Arrêt de l'agent.")
    except Exception as e:
        logger.exception(f"Erreur non gérée: {e}")
        print(f"\n\n❌ Une erreur s'est produite: {e}")
    finally:
        print("\n👋 Fin de l'exécution de l'agent de recherche.")
