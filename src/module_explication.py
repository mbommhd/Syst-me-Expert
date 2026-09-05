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
    
# Dédinissons notre patron d'explicabilité: c'est lui qui définit comment et sous quel schéma seront données les explications
patron_éligibilité: Dict[str, Dict[str, Any]] = {
    # Explications Bac
    "R_Eli_01": {"statut": "éligible", "filière":"Informatique", "condition":"Bac {serie_bac}", "message":"Félicitations! Votre\
        Baccalauréat série {serie_bac} donne un accès direct à la filière Informatique", "procedure":"Dossier retenu. Préparez\
            vos pièces justificatives et procédez à la préinscription en ligne"},
    
}