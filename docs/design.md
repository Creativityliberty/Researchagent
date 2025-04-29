# Design Doc: Research Agent

## Objectif
Créer un agent de recherche qui prend un thème en entrée, recherche des informations pertinentes sur le web, extrait le contenu des pages trouvées, et compile les résultats dans un document Markdown structuré.

## Architecture

### Workflow Pocket Flow
Le projet utilise le framework Pocket Flow pour créer un workflow modulaire avec les nœuds suivants:

1. **PrepareSearchQueryNode**: Génère des requêtes de recherche optimisées à partir du thème
2. **PerformSearchNode**: Exécute la recherche web via SerpAPI
3. **ExtractUrlsNode**: Extrait les URLs pertinentes des résultats
4. **ScrapeContentNode**: Scrape le contenu des URLs (BatchNode)
5. **FormatMarkdownNode**: Formate les contenus en document Markdown
6. **SaveToFileNode**: Sauvegarde le résultat dans un fichier
7. **EndNode/NoResultNode**: Nœuds terminaux pour la gestion des résultats

```mermaid
flowchart TD
    start[Start] --> PrepareSearchQueryNode
    PrepareSearchQueryNode --> PerformSearchNode
    PerformSearchNode --> ExtractUrlsNode
    ExtractUrlsNode -- "default (URLs found)" --> ScrapeContentNode
    ExtractUrlsNode -- "no_urls" --> NoResultNode
    ScrapeContentNode -- "default (Content scraped)" --> FormatMarkdownNode
    ScrapeContentNode -- "no_content" --> NoResultNode
    FormatMarkdownNode --> SaveToFileNode
    SaveToFileNode -- "success" --> EndNode
    SaveToFileNode -- "failure" --> NoResultNode
    EndNode -- "terminates" --> end
    NoResultNode -- "terminates" --> end
```

### Utilitaires
- **call_llm.py**: Interface avec l'API Gemini pour les tâches d'IA
- **llm_parsing.py**: Analyse des réponses du LLM
- **search_web.py**: Recherche web via SerpAPI
- **selenium_scraper.py**: Scraping robuste avec Selenium
- **save_text_file.py**: Sauvegarde de fichiers

## Intégration LLM
L'agent utilise Gemini 2.5 Flash pour:
- Générer des requêtes de recherche pertinentes
- Potentiellement résumer ou structurer le contenu

## Défis techniques
1. **Scraping robuste**: Les sites web ont des structures variées
2. **Limites des API**: Gestion des quotas et coûts
3. **Performance**: Optimisation du traitement par lots

## Évolutions futures
1. **API REST**: Exposer le workflow via des endpoints
2. **Frontend**: Interface utilisateur React/Next.js
3. **Fonctionnalités avancées**: Résumés LLM, filtrage intelligent
