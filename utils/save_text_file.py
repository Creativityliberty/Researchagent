"""
Module pour sauvegarder du contenu textuel dans des fichiers.
Fournit des fonctions pour écrire dans des fichiers avec gestion d'erreurs.
"""

import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def save_text_file(filepath, content):
    """
    Sauvegarde du contenu textuel dans un fichier.
    
    Args:
        filepath (str): Chemin du fichier à créer/écraser
        content (str): Contenu à écrire dans le fichier
        
    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    try:
        # Création du répertoire parent si nécessaire
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Création du répertoire: {directory}")
        
        # Écriture du fichier
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        
        logger.info(f"Fichier sauvegardé avec succès: {filepath}")
        return True
        
    except IOError as e:
        logger.error(f"Erreur d'E/S lors de la sauvegarde du fichier {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la sauvegarde du fichier {filepath}: {e}")
        return False


def append_to_text_file(filepath, content):
    """
    Ajoute du contenu à la fin d'un fichier existant.
    
    Args:
        filepath (str): Chemin du fichier à modifier
        content (str): Contenu à ajouter au fichier
        
    Returns:
        bool: True si l'ajout a réussi, False sinon
    """
    try:
        # Création du répertoire parent si nécessaire
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Création du répertoire: {directory}")
        
        # Ajout au fichier
        with open(filepath, 'a', encoding='utf-8') as file:
            file.write(content)
        
        logger.info(f"Contenu ajouté avec succès au fichier: {filepath}")
        return True
        
    except IOError as e:
        logger.error(f"Erreur d'E/S lors de l'ajout au fichier {filepath}: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'ajout au fichier {filepath}: {e}")
        return False


if __name__ == "__main__":
    # Test de sauvegarde
    test_content = "Ceci est un test de sauvegarde.\nLigne 2 du test."
    test_file = "test_output.md"
    
    print(f"Test de sauvegarde dans {test_file}")
    result = save_text_file(test_file, test_content)
    
    if result:
        print(f"Sauvegarde réussie dans {test_file}")
    else:
        print(f"Échec de la sauvegarde dans {test_file}")
