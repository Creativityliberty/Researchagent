"""
Module définissant les nœuds du workflow Pocket Flow pour l'agent de recherche.
Chaque nœud représente une étape du processus de recherche et d'extraction d'informations.
"""

import logging
from pocketflow import Node, BatchNode
from utils.call_llm import call_llm
from utils.llm_parsing import parse_yaml_queries, extract_markdown_content
from utils.search_web import search_web
from utils.selenium_scraper import scrape_with_selenium
from utils.save_text_file import save_text_file

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PrepareSearchQueryNode(Node):
    """
    Nœud qui prépare les termes de recherche basés sur le thème d'entrée en utilisant Gemini.
    Transforme un thème général en requêtes de recherche optimisées.
    """
    
    def prep(self, shared):
        """Récupère le thème depuis le shared store."""
        theme = shared.get("theme")
        if not theme:
            logger.error("Thème manquant dans le shared store.")
        return theme
    
    def exec(self, theme):
        """Génère des requêtes de recherche à partir du thème en utilisant Gemini."""
        if not theme:
            return None
        
        logger.info(f"Génération de requêtes de recherche pour le thème: {theme}")
        
        # Construction du prompt pour Gemini
        prompt = f"""
        Génère une liste de 3 à 5 requêtes de recherche pertinentes pour trouver des blogs et articles en ligne sur le thème:
        "{theme}"
        
        Retourne les requêtes sous forme de liste YAML.
        Exemple de format attendu:
        
        ```yaml
        queries:
          - requête 1 très spécifique et pertinente
          - requête 2 avec des termes techniques précis
          - requête 3 orientée vers des études de cas
        ```
        
        Les requêtes doivent être précises, spécifiques et optimisées pour trouver du contenu de qualité.
        """
        
        # Appel à Gemini
        response = call_llm(prompt)
        
        # Parsing des requêtes
        queries = parse_yaml_queries(response)
        
        if queries:
            logger.info(f"Requêtes générées: {queries}")
            # Pour cet exemple simple, on utilise la première requête
            # Pour un agent plus avancé, on pourrait utiliser plusieurs requêtes en parallèle
            return queries[0]
        else:
            logger.warning(f"Aucune requête générée. Utilisation du thème original: {theme}")
            return theme
    
    def post(self, shared, prep_res, exec_res):
        """Stocke la requête de recherche générée dans le shared store."""
        if exec_res:
            shared["search_query"] = exec_res
            logger.info(f"Requête de recherche stockée: {shared['search_query']}")
        else:
            shared["search_query"] = shared.get("theme", "")
            logger.warning(f"Utilisation du thème comme requête: {shared['search_query']}")
        
        return "default"  # Passe au nœud suivant


class PerformSearchNode(Node):
    """
    Nœud qui exécute la recherche web en utilisant la requête générée.
    Utilise SerpAPI pour obtenir des résultats de recherche pertinents.
    """
    
    def prep(self, shared):
        """Récupère la requête de recherche depuis le shared store."""
        return shared.get("search_query")
    
    def exec(self, search_query):
        """Exécute la recherche web avec la requête fournie."""
        if not search_query:
            logger.error("Requête de recherche manquante.")
            return []
        
        logger.info(f"Recherche web avec la requête: {search_query}")
        
        # Appel à l'utilitaire de recherche web
        results = search_web(search_query, num_results=7)
        
        return results
    
    def post(self, shared, prep_res, exec_res):
        """Stocke les résultats bruts de la recherche dans le shared store."""
        shared["search_results_raw"] = exec_res
        logger.info(f"Stockage de {len(shared['search_results_raw'])} résultats de recherche.")
        
        return "default"  # Passe au nœud suivant


class ExtractUrlsNode(Node):
    """
    Nœud qui extrait les URLs des résultats bruts de la recherche.
    Peut filtrer les URLs non pertinentes si nécessaire.
    """
    
    def prep(self, shared):
        """Récupère les résultats bruts de la recherche depuis le shared store."""
        return shared.get("search_results_raw", [])
    
    def exec(self, search_results):
        """Extrait les URLs des résultats de recherche."""
        if not search_results:
            logger.warning("Aucun résultat de recherche à traiter.")
            return []
        
        # Extraction simple des URLs
        urls = [result.get("url") for result in search_results if result.get("url")]
        
        # Suppression des doublons
        urls = list(set(urls))
        
        logger.info(f"Extraction de {len(urls)} URLs uniques.")
        
        # NOTE: On pourrait utiliser Gemini ici pour filtrer les URLs
        # Par exemple, pour déterminer si une URL pointe vers un blog, un article, etc.
        
        return urls
    
    def post(self, shared, prep_res, exec_res):
        """Stocke la liste des URLs à scraper dans le shared store."""
        shared["extracted_urls"] = exec_res
        logger.info(f"Stockage de {len(shared['extracted_urls'])} URLs pour scraping.")
        
        if not shared["extracted_urls"]:
            logger.warning("Aucune URL extraite, arrêt du flow.")
            return "no_urls"  # Action pour arrêter le flow si aucune URL
        
        return "default"  # Passe au nœud suivant


class ScrapeContentNode(BatchNode):
    """
    Nœud qui scrape le contenu de chaque URL extraite.
    Utilise BatchNode pour traiter les URLs en lots (séquentiellement par défaut).
    """
    
    def prep(self, shared):
        """Récupère la liste des URLs à scraper depuis le shared store."""
        urls = shared.get("extracted_urls", [])
        logger.info(f"Préparation du scraping de {len(urls)} URLs.")
        
        # Retourne la liste d'URLs, chaque URL sera passée à exec()
        return urls
    
    def exec(self, url):
        """Scrape le contenu d'une URL spécifique."""
        logger.info(f"Scraping du contenu pour: {url}")
        
        # Appel à l'utilitaire de scraping
        content = scrape_with_selenium(url)
        
        # Retourne un dictionnaire avec l'URL et son contenu
        return {"url": url, "content": content}
    
    def post(self, shared, prep_res, exec_res_list):
        """Traite les résultats du scraping et les stocke dans le shared store."""
        # Filtrage des résultats valides (non vides et sans erreur)
        valid_results = []
        for item in exec_res_list:
            if item and item.get("content"):
                content = item["content"]
                # Vérification que le contenu n'est pas un message d'erreur
                if not content.startswith("Erreur:"):
                    valid_results.append(item)
                else:
                    logger.warning(f"Contenu ignoré pour {item['url']}: {content[:50]}...")
        
        shared["scraped_content"] = valid_results
        logger.info(f"Stockage de {len(shared['scraped_content'])} contenus scrapés avec succès.")
        
        if not shared["scraped_content"]:
            logger.warning("Aucun contenu scrapé avec succès, arrêt du flow.")
            return "no_content"  # Action pour arrêter le flow
        
        return "default"  # Passe au nœud suivant


class FormatMarkdownNode(Node):
    """
    Nœud qui formate les contenus scrapés dans un format Markdown lisible.
    Peut utiliser Gemini pour résumer ou organiser le contenu.
    """
    
    def prep(self, shared):
        """Récupère les contenus scrapés et le thème depuis le shared store."""
        return {
            "scraped_content": shared.get("scraped_content", []),
            "theme": shared.get("theme", "Recherche")
        }
    
    def exec(self, inputs):
        """Formate les contenus en Markdown structuré."""
        scraped_content = inputs["scraped_content"]
        theme = inputs["theme"]
        
        if not scraped_content:
            logger.warning("Aucun contenu à formater.")
            return "# Aucun résultat trouvé\n\nAucun contenu pertinent n'a pu être extrait pour ce thème."
        
        logger.info(f"Formatage de {len(scraped_content)} contenus en Markdown.")
        
        # Option 1: Formatage simple avec titre et contenu
        markdown_output = f"# Résultats de recherche: {theme}\n\n"
        markdown_output += f"_Recherche effectuée le {__import__('datetime').datetime.now().strftime('%Y-%m-%d à %H:%M')}_\n\n"
        markdown_output += f"## Sommaire\n\n"
        
        # Génération du sommaire
        for i, item in enumerate(scraped_content, 1):
            url = item["url"]
            domain = __import__('urllib.parse').parse.urlparse(url).netloc
            markdown_output += f"{i}. [{domain}]({url})\n"
        
        markdown_output += "\n---\n\n"
        
        # Ajout des contenus détaillés
        for i, item in enumerate(scraped_content, 1):
            url = item["url"]
            content = item["content"]
            domain = __import__('urllib.parse').parse.urlparse(url).netloc
            
            markdown_output += f"## {i}. Contenu de [{domain}]({url})\n\n"
            markdown_output += content + "\n\n---\n\n"
        
        # Option 2 (plus avancée): Utiliser Gemini pour résumer chaque contenu
        # Cette option pourrait être implémentée dans une version future
        
        return markdown_output
    
    def post(self, shared, prep_res, exec_res):
        """Stocke le contenu Markdown formaté dans le shared store."""
        shared["final_markdown"] = exec_res
        logger.info(f"Markdown formaté (longueur: {len(shared['final_markdown'])} caractères).")
        
        return "default"  # Passe au nœud suivant


class SaveToFileNode(Node):
    """
    Nœud qui sauvegarde le contenu Markdown final dans un fichier.
    """
    
    def prep(self, shared):
        """Récupère le contenu Markdown et le chemin du fichier de sortie."""
        markdown_content = shared.get("final_markdown")
        filepath = shared.get("output_filepath")
        
        if not filepath:
            # Génération d'un nom de fichier par défaut basé sur le thème
            theme = shared.get("theme", "recherche")
            safe_theme = "".join(c if c.isalnum() else "_" for c in theme)
            timestamp = __import__('datetime').datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"resultats_{safe_theme}_{timestamp}.md"
            shared["output_filepath"] = filepath
            logger.info(f"Nom de fichier généré: {filepath}")
        
        return markdown_content, filepath
    
    def exec(self, inputs):
        """Sauvegarde le contenu Markdown dans un fichier."""
        markdown_content, filepath = inputs
        
        if not markdown_content:
            logger.error("Contenu Markdown manquant.")
            return False
        
        logger.info(f"Sauvegarde du contenu Markdown dans: {filepath}")
        
        # Appel à l'utilitaire de sauvegarde
        success = save_text_file(filepath, markdown_content)
        
        return success
    
    def post(self, shared, prep_res, exec_res):
        """Détermine l'action suivante basée sur le succès de la sauvegarde."""
        if exec_res:
            logger.info(f"Fichier Markdown sauvegardé avec succès: {shared['output_filepath']}")
            return "success"  # Action pour indiquer le succès
        else:
            logger.error(f"Échec de la sauvegarde du fichier Markdown: {shared.get('output_filepath')}")
            return "failure"  # Action pour indiquer l'échec


class EndNode(Node):
    """
    Nœud terminal pour indiquer la fin du workflow avec succès.
    """
    
    def prep(self, shared):
        """Prépare les données nécessaires pour l'exécution."""
        return shared.get("output_filepath", "fichier inconnu")
    
    def exec(self, filepath):
        """Affiche un message de succès."""
        print(f"\n✅ Agent terminé avec succès!")
        print(f"📄 Résultats sauvegardés dans: {filepath}")
        return None
    
    def post(self, shared, prep_res, exec_res):
        """Termine le flow."""
        return None  # Termine le flow


class NoResultNode(Node):
    """
    Nœud terminal pour gérer les cas où aucune URL ou contenu n'est trouvé.
    """
    
    def exec(self, _):
        """Affiche un message d'information sur l'absence de résultats."""
        theme = self.shared.get("theme", "recherche")
        print(f"\n⚠️ Agent terminé: Aucun résultat pertinent trouvé pour '{theme}'.")
        
        # Détermination de la raison de l'échec
        if not self.shared.get("extracted_urls"):
            print("Aucune URL n'a été trouvée lors de la recherche.")
        elif not self.shared.get("scraped_content"):
            print("Des URLs ont été trouvées, mais aucun contenu n'a pu être extrait.")
        else:
            print("Une erreur s'est produite lors du traitement des résultats.")
        
        return None
    
    def post(self, shared, prep_res, exec_res):
        """Termine le flow."""
        return None  # Termine le flow
