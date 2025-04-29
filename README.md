# Research Agent

Un agent intelligent basé sur Pocket Flow qui recherche, extrait et compile des informations sur un thème donné. Disponible en ligne de commande et via une API REST.

## 🔍 Fonctionnalités

- **Génération de requêtes optimisées** avec Gemini 2.5 Flash
- **Recherche web** via SerpAPI (ou simulation pour les tests)
- **Extraction de contenu** avec Selenium et BeautifulSoup
- **Compilation en Markdown** structuré et lisible
- **Architecture modulaire** basée sur Pocket Flow
- **API REST** avec FastAPI pour l'intégration dans d'autres applications

## 📋 Prérequis

- Python 3.8+
- Chrome/Chromium (pour Selenium)
- Clés API:
  - Google Generative AI (Gemini)
  - SerpAPI (optionnel, mode simulation disponible)

## 🚀 Installation

1. Clonez ce dépôt:
   ```bash
   git clone <url-du-repo>
   cd research_agent
   ```

2. Installez les dépendances:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurez les variables d'environnement:
   Créez un fichier `.env` à la racine du projet:
   ```
   GOOGLE_API_KEY=votre_clé_api_gemini
   SERPAPI_API_KEY=votre_clé_api_serpapi
   ```

## 💻 Utilisation

### Ligne de commande

```bash
python main.py --theme "Impact de l'IA sur l'emploi" --output "resultats.md"
```

Arguments disponibles:
- `--theme`, `-t`: Thème de recherche
- `--output`, `-o`: Chemin du fichier de sortie
- `--verbose`, `-v`: Mode verbeux (debug)

Si vous ne spécifiez pas de thème, il vous sera demandé interactivement.

### API REST

```bash
python run_api.py
```

L'API sera accessible sur http://localhost:8080 avec:
- Documentation Swagger: http://localhost:8080/docs
- Documentation ReDoc: http://localhost:8080/redoc

Endpoints disponibles:
- `POST /research/` - Lancer une nouvelle recherche
- `GET /research/{research_id}/status` - Vérifier le statut
- `GET /research/{research_id}/results` - Récupérer les résultats
- `GET /research/` - Lister toutes les recherches

### Comme module

```python
from flow import research_flow

# Configuration des données d'entrée
shared = {
    "theme": "Intelligence artificielle et éducation",
    "output_filepath": "resultats_ia_education.md"
}

# Exécution du flux
research_flow.run(shared)
```

## 🧩 Architecture

Le projet utilise le framework Pocket Flow pour créer un workflow modulaire:

1. **PrepareSearchQueryNode**: Génère des requêtes optimisées
2. **PerformSearchNode**: Exécute la recherche web
3. **ExtractUrlsNode**: Extrait les URLs pertinentes
4. **ScrapeContentNode**: Scrape le contenu des URLs
5. **FormatMarkdownNode**: Formate en Markdown
6. **SaveToFileNode**: Sauvegarde les résultats

## 🛠️ Personnalisation

### Modifier le scraping

Le module `selenium_scraper.py` contient des extracteurs spécifiques pour certains sites populaires. Vous pouvez ajouter vos propres extracteurs en suivant le modèle:

```python
def _extract_custom_site_content(driver):
    """Extrait le contenu spécifique à votre site."""
    # Votre logique d'extraction ici
    return content
```

### Améliorer le formatage Markdown

Le nœud `FormatMarkdownNode` peut être amélioré pour utiliser Gemini afin de résumer ou restructurer le contenu extrait:

```python
# Dans FormatMarkdownNode.exec()
# Utiliser Gemini pour générer un résumé
summary_prompt = f"Résume les informations suivantes sur '{theme}':\n\n{all_content}"
summary = call_llm(summary_prompt)
markdown_output = f"# Résumé: {theme}\n\n{summary}\n\n---\n\n"
```

## 📊 Roadmap

- [x] Implémentation de l'agent de recherche de base
- [x] API REST avec FastAPI
- [ ] Interface utilisateur web (frontend React/Next.js)
- [ ] Implémentation d'AsyncParallelBatchNode pour le scraping parallèle
- [ ] Ajout de filtres de pertinence basés sur LLM
- [ ] Amélioration des extracteurs spécifiques par site
- [ ] Génération de résumés et d'analyses avec Gemini

## 📄 Licence

MIT

---

Développé avec ❤️ en utilisant Pocket Flow et Gemini
