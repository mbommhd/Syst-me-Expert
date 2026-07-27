# C'est ici que nous allons coder nos faits, le moteur d'inférence et les règles métier que celui-ci appliquera.

# Importons nos classes depuis la bibliothèque Experta
from experta import Fact, Field, KnowledgeEngine, Rule, TEST, MATCH

# Déclarons nos faits

# D'abord le niveau de l'étudiant
class niveau_étudiant(Fact):
    """Il faut savoir qu'actuellement, le système ne couvre que deux types de profil étudiant: BAC et BAC+2. La façon d'orienter diffère
    donc selon le profil de l'étudiant."""
    niveau = Field(str)
    
class scénario_adéquat(Fact):
    """Voilà pourquoi identifier le profil est nécessaire d'entrer de jeux. Cela permet au système de déclancher les bonnes règles
    métier."""
    scénario = Field(str)
    
    
class faits_métier(Fact):
    """On utilise les variables 'clé' et 'valeur' pour capter les faits de l'utilisateur. En effet,les faits sont transmis au
    système sous forme de dictionnaire python. Capter les données de l'utilisateur avec ces deux variables offre plusieurs
    avantages: d'abord, cela facilite la communication entre la couche NLP et le moteur; Ensuite, cela rend le système beacoup plus
    flexible et dynamique car il sera possible d'ajouter bien plus de faits plutard sans toucher au code si le système évoulue."""
    clé = Field(str)
    valeur = Field(str)
    
    
class proposition_filière(Fact):
    """Ce fait est généré par le moteur d'inférence une fois qu'il a trouvé une filière qui corresond au profil de l'étudiant"""
    id_règle = Field(str)
    filière = Field(str)
    débouchés = Field(str)
    
    
class y_n_éligible(Fact):
    """Ce fait généré lors de la phase 2 du processus d'orientation et nous dit si l'étudiant est éligible à la filière qu'il
    aura choisi"""
    éligible = Field(bool)
    filière = Field(str)
    motif = Field(str)
    