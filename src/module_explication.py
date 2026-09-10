# Ce module intervient à la fin de la phase 2 pour générer une justification pédagogique et transparente sur l'éligibilité ou la non
# éligibilité de l'utilisateur

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

# On définit un modèle de variables justificatives
class variables_justificatives(BaseModel):
    """Cette classe renferme toutes les variables nécessaires pour justifier l'éligibilité ou la non eligiblité de l'utilisateur"""
    id_règle: str = Field(..., description="Id de la règle d'éligibilité déclanchée")
    statut: str = Field(..., description="éligible ou non éligible, non admissible, réorientation")
    filière: str = Field(..., description="cursus ou filière évalué")
    message_explicatif: str = Field(..., description="raison détaillée s'appuyant sur les notes, séries du Bac ou diplome d'entrée")
    procedure_suivante: str = Field(..., description="consigne pour l'étudiant (documents requis, réorientation)")
    
# Définissons notre patron d'explicabilité: c'est lui qui définit comment et sous quel schéma seront données les explications
patron_éligibilité: Dict[str, Dict[str, Any]] = {
    # Explications Bac
    "R_Eli_01": {"statut": "éligible", "filière":"Informatique", "condition":"Bac {serie_bac}", "message":"Félicitations! Votre\
        Baccalauréat série {serie_bac} donne un accès direct à la filière Informatique", "procedure":"Dossier retenu. Préparez\
            vos pièces justificatives et procédez à la préinscription en ligne"},
    "R_Eli_02": {"statut": "éligible", "filière":"Mathématique", "condition":"Bac {serie_bac} (Séries C, E, GCE Sc.)",\
        "message":"Félicitations! La série de votre Baccalauréat valide directement les prérequis en Mathématique", "procedure":"Dossier retenu. Préparez\
            vos pièces justificatives et procédez à la préinscription en ligne"},
    "R_Eli_03": {"statut": "éligible", "filière":"Mathématique", "condition":"Bac D avec une note de maths >= 12/20", \
        "message":"Félicitations! Bien que issu d'un Bac D, votre note en mathématique ({note_maths}/20) atteint le seuil exigé (12/20).",
        "procedure":"Dossier retenu. Préparez vos pièces justificatives et procédez à la préinscription en ligne"},
     "R_Eli_04": {"statut": "Non éligible", "filière":"Mathématique", "condition":"Bac D avec une note de maths < 12/20",
        "message":"Malheureusement, votre note en mathématique ({note_maths}/20) est inférieure au seuil de 12/20\
        exigé pour la filière Mathématique avec un Bac D", "procedure":"Avec notre profil, vous etes éligibles sans condition \
        en Informatique ou en Sciences de la Terre. Nous vous conseillons de réorienter votre choix"},
     "R_Eli_05": {"statut": "éligible", "filière":"Chimie ou Physique", "condition":"Bac {serie_bac} (Séries C, E, F)", 
        "message":"Félicitations! La série de votre Bac ({serie_bac}) vous confère un accès direct en Chimie et en Physique",
        "procedure":"Dossier retenu. Préparez vos pièces justificatives et procédez à la préinscription en ligne"},
     "R_Eli_06": {"statut": "éligible", "filière":"Chimie", "condition":"Bac D avec une note de maths >= 10/20 ou chimie  >= 10/20",
        "message":"Félicitations! Vos résultats scientifiques (Maths: {note_maths}/20, Chimie: {note_chimie}/20 satisfont la condition\
        minimale d'accès.", "procedure":"Dossier retenu. Préparez vos pièces justificatives et procédez à la préinscription en ligne"},
     "R_Eli_07": {"statut": "non éligible", "filière":"Chimie", "condition":"Bac D avec une note de maths < 10/20 ou chimie < 10/20",
        "message": "Les sciences dures requièrent une base solide dans les matières scientifiques. Vos notes actuelles (Maths: {note_maths}/20, Chimie: {note_chimie}/20) \
        ne satisfont pas les prérequis", "procedure":"Votre profil serait plus adapté en Informatique ou en Biologie"},
     "R_Eli_08": {"statut": "éligible", "filière":"Physique", "condition":"Bac D avec une note de maths >= 10/20 ou physique >= 10/20",
        "message":"Félicitations! Vos notes en maths: {note_maths}/20 et en physique: {note_physique}/20 valident vos prérequis pour la \
        filière Physique", "procedure":"Dossier retenu. Préparez vos pièces justificatives et procédez à la préinscription en ligne"},
     "R_Eli_09": {"statut": "non éligible", "filière":"Physique", "condition":"Bac D avec une note de maths < 10/20 ou Physique < 10/20",
        "message": "Les sciences dures requièrent une base solide dans les matières scientifiques. Vos notes actuelles (Maths: {note_maths}/20, Physique: {note_physique}/20 \
        sont insuffisantes pour la physique", "procedure":"Votre profil serait plus adapté en Informatique ou en Géologie."},
     "R_Eli_10": {"statut": "éligible", "filière":"Sciences Biologiques ou de la Terre", "condition":"Bac {serie_bac} (C, D, F, GCE Sc)",
        "message":"Félicitations! Votre Baccalauréat série {serie_bac} vous permet d'accéder directement aux Sciences Biologiques ou de la Terre",
        "procedure":"Dossier retenu. Préparez vos pièces justificatives et procédez à la préinscription en ligne"},
     "R_Eli_11": {"statut": "Non Admissible", "filière":"Toutes filières", "condition":"Bac littéraies ou techniques non scientifique",
        "message":"Les filières de la Facultés des Sciences requièrent obligatoirement un Baccalauréat scientifique ou technique orienté science.",
        "procedure": "Admission impossible. Nous vous invitons à vous orienter vers les facultés littéraires, juridiques ou de sciences humaines."},
     
     # Explications Bac+2
    "R_Eli_01_Bac2": {"statut": "éligible (sous réserve du Bac+2)", "filière":"Licence Professionnelle (LIDA/ TL/ MIME)", "condition":"Cursus Bac+2 Classique ou Professionnel",
        "message": "Dossier pré-validé! Votre diplome de niveau Bac+2 ({type_bac2}) est reconnu comme passerelle directe vers nos Licences Professionnelles.",
        "procedure": "Préparez vos relevés de note l1 et l2 et la copie certifiée du Bac+2 pour la validation administrative."},
    "R_Eli_02_Bac2": {"statut": "éligible (sous réserve du Bac+2)", "filière":"Licence 3 Classique", "condition":"Bac+2 classique isuu d'une Université d'Etat",
        "message": "Dossier pré-validé! Votre cursus universitaire classique ({type_bac2}) en Université d'Etat permet une entrée directe en L3 classique.",
        "procedure": "Déposez vos relevés de notes certifiés auprès de la scolarité de la Faculté des Sciences."},
    "R_Eli_03_Bac2": {"statut": "Réorientation", "filière":"Licence 3 Classique", "condition":"Bac+2 Professionnel vers L3 classique.",
        "message": "Un cursus initialement professionnel ne permet pas une admission directe en L3 Classique.",
        "procedure": "Nous vous conseillons de vous réorienter vers nos Licences Pro qui sont parfaitement adaptées à votre profil pratique."}
     }

# Fonction d'explicabilité
def explication(id_regle:str, profil_data: Optional[Dict[str, Any]] = None):
    """Cette fonction reçoit l'Id de la règle déclenchée par Experta et les notes/série du candidat pour générer une justification détaillée"""
    if profil_data is None:
        profil_data = {}
    patron = patron_éligibilité.get(id_regle)
    if not patron:
        return("Décision conforme aux critères académiques de la Faculté des Sciences.")
    
    # On récupère les données de l'étudiant
    serie_bac = profil_data.get("serie_bac", "N/A")
    note_maths = profil_data.get("note_maths", "N/A")
    note_chimie = profil_data.get("note_chimie", "N/A")
    note_physique = profil_data.get("note_physique", "N/A")
    type_bac2 = profil_data.get("type_bac2", "N/A")
    
    # Formatage du message explicatif
    try:
        msg_formate = patron["message"].format(serie_bac = serie_bac,
            note_maths = note_maths, note_chimie = note_chimie, note_physique = note_physique, type_bac2 = type_bac2)
    except Exception:
        msg_formate = patron["message"]
        
    # Le rendu final du message
    rendu = (
        f"{patron['statut']} - Filière: {patron['filière']}\n\n"
        f"Condition évaluée: {patron['condition']}\n\n"
        f"Justification: \n{msg_formate}\n\n"
        f"Démarche à suivre: \n{patron['procedure']}"
    )
    
    return rendu

####################################################################################################################
# Test d'intégration
if __name__ == "__main__":
    print("Début du Test Unitaire du module d'explication")
    # Cas 1: Bac D rejeté en Mathématique
    print("[TEST 1]: Candidat Bac D avec 9.5 en maths et qui veut faire Mathématique:")
    candidat_1 = {"serie_bac": "D", "note_maths":9.5}
    print(explication("R_Eli_04", candidat_1))
    
    # Cas 2: Bac D admis en Chimie
    print("[TEST 2]: Candidat Bac D avec 11/20 en maths et 8/20 en chimie et qui veut faire Chimie:")
    candidat_2 =  {"serie_bac": "D", "note_maths":11, "note_chimie":8}
    print(explication("R_Eli_06", candidat_2))