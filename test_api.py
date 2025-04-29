"""
Script de test pour l'API Research Agent.
Effectue des appels aux différents endpoints pour vérifier leur fonctionnement.
"""

import requests
import json
import time
import sys

# Configuration
API_BASE_URL = "http://localhost:8080"
THEME = "Impact de l'IA sur la créativité artistique"

def test_api():
    """Teste les différentes fonctionnalités de l'API."""
    print("\n" + "="*50)
    print("🧪 Test de l'API Research Agent")
    print("="*50)
    
    # 1. Lancement d'une recherche
    print("\n1️⃣ Test de lancement d'une recherche")
    research_id = launch_research()
    
    if not research_id:
        print("❌ Échec du test: Impossible de lancer une recherche")
        return False
    
    # 2. Suivi de la progression
    print("\n2️⃣ Test de suivi de progression")
    success = monitor_progress(research_id)
    
    if not success:
        print("❌ Échec du test: Problème lors du suivi de progression")
        return False
    
    # 3. Récupération des résultats
    print("\n3️⃣ Test de récupération des résultats")
    success = get_results(research_id)
    
    if not success:
        print("❌ Échec du test: Problème lors de la récupération des résultats")
        return False
    
    # 4. Listage des recherches
    print("\n4️⃣ Test de listage des recherches")
    success = list_researches()
    
    if not success:
        print("❌ Échec du test: Problème lors du listage des recherches")
        return False
    
    print("\n" + "="*50)
    print("✅ Tous les tests ont réussi!")
    print("="*50)
    return True


def launch_research():
    """Lance une nouvelle recherche et retourne son ID."""
    try:
        payload = {
            "theme": THEME,
            "max_results": 3
        }
        
        response = requests.post(f"{API_BASE_URL}/research/", json=payload)
        
        if response.status_code != 202:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return None
        
        data = response.json()
        research_id = data.get("research_id")
        
        print(f"✅ Recherche lancée avec succès")
        print(f"📝 ID: {research_id}")
        print(f"📝 Thème: {data.get('theme')}")
        print(f"📝 Statut initial: {data.get('status')}")
        
        return research_id
    
    except Exception as e:
        print(f"❌ Exception lors du lancement de la recherche: {e}")
        return None


def monitor_progress(research_id):
    """Suit la progression d'une recherche jusqu'à sa complétion."""
    try:
        max_attempts = 30  # Maximum 5 minutes (10 secondes * 30)
        attempts = 0
        completed = False
        
        print(f"⏳ Suivi de la progression de la recherche {research_id}")
        print(f"   (Vérification toutes les 10 secondes, maximum {max_attempts} tentatives)")
        
        while attempts < max_attempts and not completed:
            response = requests.get(f"{API_BASE_URL}/research/{research_id}/status")
            
            if response.status_code != 200:
                print(f"❌ Erreur {response.status_code}: {response.text}")
                return False
            
            data = response.json()
            status = data.get("status")
            progress = data.get("progress")
            current_step = data.get("current_step")
            
            print(f"📊 Progression: {progress:.1f}% - Statut: {status} - Étape: {current_step}")
            
            if status in ["completed", "failed", "no_results"]:
                completed = True
                print(f"✅ Recherche terminée avec statut: {status}")
                if status != "completed":
                    print(f"⚠️ Message: {data.get('error_message')}")
                break
            
            attempts += 1
            time.sleep(10)  # Attente de 10 secondes entre les vérifications
        
        if not completed:
            print("⚠️ Délai d'attente dépassé, la recherche est toujours en cours")
        
        return True
    
    except Exception as e:
        print(f"❌ Exception lors du suivi de progression: {e}")
        return False


def get_results(research_id):
    """Récupère les résultats d'une recherche terminée."""
    try:
        response = requests.get(f"{API_BASE_URL}/research/{research_id}/results")
        
        if response.status_code != 200:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        data = response.json()
        
        print(f"✅ Résultats récupérés avec succès")
        print(f"📝 Fichier de sortie: {data.get('output_filename')}")
        print(f"📝 Nombre de sources: {len(data.get('sources', []))}")
        
        # Affichage d'un extrait du contenu Markdown
        markdown_content = data.get("markdown_content", "")
        preview_length = min(500, len(markdown_content))
        print(f"\n📄 Aperçu du contenu Markdown ({preview_length} caractères sur {len(markdown_content)}):")
        print("-" * 50)
        print(markdown_content[:preview_length] + "..." if len(markdown_content) > preview_length else markdown_content)
        print("-" * 50)
        
        return True
    
    except Exception as e:
        print(f"❌ Exception lors de la récupération des résultats: {e}")
        return False


def list_researches():
    """Liste toutes les recherches."""
    try:
        response = requests.get(f"{API_BASE_URL}/research/")
        
        if response.status_code != 200:
            print(f"❌ Erreur {response.status_code}: {response.text}")
            return False
        
        researches = response.json()
        
        print(f"✅ Liste des recherches récupérée avec succès")
        print(f"📝 Nombre de recherches: {len(researches)}")
        
        for i, research in enumerate(researches, 1):
            print(f"\n📌 Recherche {i}:")
            print(f"   ID: {research.get('research_id')}")
            print(f"   Thème: {research.get('theme')}")
            print(f"   Statut: {research.get('status')}")
        
        return True
    
    except Exception as e:
        print(f"❌ Exception lors du listage des recherches: {e}")
        return False


if __name__ == "__main__":
    # Vérification que l'API est en cours d'exécution
    try:
        requests.get(f"{API_BASE_URL}")
        test_api()
    except requests.exceptions.ConnectionError:
        print(f"❌ Impossible de se connecter à l'API sur {API_BASE_URL}")
        print("   Assurez-vous que l'API est en cours d'exécution (python run_api.py)")
        sys.exit(1)
