"""
Module pour interagir avec l'API Google Generative AI (Gemini).
Fournit des fonctions pour appeler le modèle Gemini avec différents prompts.
"""

import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

# Récupération de la clé API et du modèle
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash-latest")

# Configuration de l'API Gemini
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY non définie dans les variables d'environnement.")
    genai_configured = False
else:
    genai.configure(api_key=GOOGLE_API_KEY)
    genai_configured = True
    logger.info("API Gemini configurée avec succès.")


def call_llm(prompt, model_name=None):
    """
    Appelle le modèle Gemini avec un prompt donné.
    
    Args:
        prompt (str): Le prompt à envoyer au modèle
        model_name (str): Le nom du modèle Gemini à utiliser
        
    Returns:
        str: La réponse du modèle ou un message d'erreur
    """
    if not genai_configured:
        logger.error("Impossible d'appeler le LLM: API Gemini non configurée.")
        return "Erreur: API LLM non configurée."
    
    # Utiliser le modèle spécifié ou celui par défaut dans les variables d'environnement
    model_to_use = model_name if model_name else DEFAULT_MODEL
    
    logger.info(f"Appel LLM avec modèle {model_to_use}")
    logger.debug(f"Prompt (début): {prompt[:100]}...")
    
    try:
        model = genai.GenerativeModel(model_to_use)
        response = model.generate_content(prompt)
        
        # Extraction du texte de la réponse
        if response and response.parts:
            text_response = "".join(part.text for part in response.parts)
            logger.info(f"Réponse LLM reçue (longueur: {len(text_response)})")
            logger.debug(f"Réponse (début): {text_response[:100]}...")
            return text_response
        else:
            logger.warning("Réponse LLM vide ou sans parties.")
            return "Réponse LLM vide."
            
    except Exception as e:
        logger.error(f"Erreur lors de l'appel à Gemini: {e}")
        # Tentative de récupération des détails d'erreur
        error_details = str(e)
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            error_details += f"\nDétails: {e.response.text}"
        return f"Erreur d'appel LLM: {error_details}"


if __name__ == "__main__":
    # Test simple de l'API
    test_prompt = "Explique en une phrase ce qu'est un agent de recherche."
    print(f"Test de l'API Gemini avec le prompt: '{test_prompt}'")
    response = call_llm(test_prompt)
    print(f"Réponse: {response}")
