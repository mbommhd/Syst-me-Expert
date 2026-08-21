# Dans ce fichier, nous allons tester notre moter d'inférence au fur et à mesure

# Gestion de compatibilté entre Experta et les versions récentes de python
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping

# Importons les faits necessaires et le moteur d'inférence
from moteur_expert import niveau_étudiant, scénario_adéquat, faits_métier, proposition_filière, y_n_éligible, moteur_inférence

# Test unitaire global du processus d'orientation : PROFIL BAC
##############################################################
def test_profil_bac():
    print("Nous testons dans un premier temps comment le système se comporte face à un profil BAC")
    # Cas où la matière pref est les maths
    print("Initialisation du moteur d'inférence")
    moteur1 = moteur_inférence()
    moteur1.reset()
    
    # déclarons directement nos faits pour la phase 1: L'orientation
    print("Déclaration des faits métiers")
    # niveau de l'étudiant
    moteur1.declare(niveau_étudiant(niveau = 'Bac'))
    
    # Phase 1: Orientation
    moteur1.declare(scénario_adéquat(scénario = 'Bac'))
    moteur1.declare(faits_métier(clé = "matière préférée", valeur = "Mathématique"))
    
    # Phase 2: La vérifiquation de l'éligibilité
    moteur1.declare(faits_métier(clé = 'filière choisie', valeur = 'Mathématique'))
    moteur1.declare(faits_métier(clé = 'série_bac', valeur = 'D'))
    moteur1.declare(faits_métier(clé = 'note_maths', valeur = 13))
    
    # Lançons le moteur d'inférence
    print("Lancement du moteur d'inférence")
    moteur1.run()
    
    # Résultat de l'orientation
    
    print("Résultat phase 1: Proposition de la filière")
    # Proposition de filière du système
    proposition = [filière for filière in moteur1.facts.values() if isinstance(filière, proposition_filière)]
    
    if proposition:
        a = proposition[0]
        print (f"[Phase 1 - OK] Filière Proposée : {a.get('filière')}")
        print (f"[Phase 1 - OK] Débouchés : {a.get('débouchés')}")
    else:
        print("[PHASE 1 - ATTENTION] Aucune filière proposée.")
        
    print("Résultat phase 2: Vérification de l'éligibilité")
    éligibilité = [f for f in moteur1.facts.values() if isinstance(f, y_n_éligible)]
    if éligibilité:
        b = éligibilité[0]
        statut_str = "Eligible" if b.get('éligible') else "Non éligible"
        print(f"[PHASE 2 - OK] Statut : {statut_str}")
        print(f"[PHASE 2 - OK] Filière : {b.get('filière')}")
        print(f"[PHASE 2 - OK] Motif : {b.get('motif')}")
    else:
        print("[PHASE 2 - ATTENTION] Aucune décision d'éligibilité générée.")
        
# Lancement du test
if __name__ == "__main__":
    test_profil_bac()