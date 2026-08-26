# 
import os
from google import genai
from pathlib import Path
from typing import Optional
from google.genai import types
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Chargeons nos variables d'environnement
env_path = Path(__file__).resolve().parent.parent/'.env'
load_dotenv(dotenv_path=env_path)

# Initialisons notre modèle pydantic
class extraction_des_faits_métiers(BaseModel):
    """Cette classe permet de cadrer la réponse ou les informations que Gemini doit nous retourner après analyse du texte de l'utilisateur"""
    
    # Entrées communes
    niveau : Optional[str] = Field(None, description = "Le niveau académique détecté. Doit etre strictement 'Bac' ou 'Bac+2'")
    centre_interet : Optional[str] = Field(None, description = "Le domaine passionnant l'étudiant (ex: 'IA', 'Data', 'Sciences naturelles', etc)")
    projet_professionnel : Optional[str] = Field(None, description = "Le projet professionnel ou ambition à long terme (ex: 'Devenir Data scientist, Chercheur, Enseignant')")
    cursus_choisi : Optional[str] = Field(None, description = "La filière ou le cursus visé par l'étudiant")
        
    # Entrées profil Bac
    serie_bac : Optional[str] = Field(None, description = "La série du Baccalauréat (ex: 'C', 'D', 'F', 'TI', 'Littéraire', 'GCE sc', 'Technique')")
    matière_préférée : Optional[str] = Field(None, description = "La matière préférée de l'élève (ex: 'Informatique', 'Mathématique', 'Physique', 'Chimie', 'Biologie/SVT', 'Géologie/SVT')")
    note_maths : Optional[str] = Field(None, description = "La note de maths sur 20 si mentionnée dans le texte")
    note_physique : Optional[str] = Field(None, description = "La note de physique sur 20 si mentionnée dans le texte")
    note_chimie : Optional[str] = Field(None, description = "La note de chimie sur 20 si mentionnée dans le texte")
    
    # Entrées profil Bac+2
    filière_origine : Optional[str] = Field(None, description = "La filière d'origine (ex: 'Infomatique', 'Mathématique')")
    type_bac2 : Optional[str] = Field(None, description = "Le type de la formation Bac+2 si mentionné. Doit etre 'Classique' ou 'Professionnel'.")
    provenance_bac2 : Optional[str] = Field(None, description = "La provenance pour le Bac+2 'Université d'Etat', 'Institut Privé'")
    
def input_user(user_promt: str):
    
    # Création du client de connexion vers Gemini
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # Instruction à Gemini
    instruction_Gemni = "Tu es un assistant d'orientation unversitaire pour la Faculté des Sciences de l'Université de Douala. \
        Ton unique role est de lire et analyser le texte d'un étudiant et extraire les faits utiles pour le moteur d'inférence.\
            Règles strictes:\
                -si l'étudiant parle de Baccalauréat, 'niveau' = 'Bac'\
                -si l'étudiant parle de BTS, DUT, Licence 2 ou Bac+2, 'niveau' = 'Bac+2'\
                -Notes: Récupère les notes chiffrées si l'étudiant les indiques (ex: '14 en maths alors note_maths = 14')\
                -N'invente aucune information non mentionnée dans le texte."
    
    # Envoie du texte de l'utilisateur + les intructions + le modèle pydantic
    response = client.models.generate_content(
        model='gemini-3.6-flash', contents=user_promt, config=types.GenerateContentConfig(
            system_instruction=instruction_Gemni, response_mime_type="application/json", response_schema=extraction_des_faits_métiers, temperature=0.1)
    )
    
    # Transformation de la chaine JSON renvoyée par Gemini par pydantic en objet python manipulable
    extraction_données = extraction_des_faits_métiers.model_validate_json(response.text)
    return extraction_données
    
###############################################################################################
# Test
if __name__ == '__main__':
    "Exemple d'entrée utilisateur"
    phrase_test = "Je m'appelles Hachley. Je suis titulaire d'un DUT en Génie Informatique et je suis très porté vers le secteur des Datas et plutard j'aimerais bien devenir Data Scientist"
    try:
        result = input_user(phrase_test)
        # Affichons les donnnées structurées récupérées
        print(f"* Niveau détecté: {result.niveau}")
        print(f"* Filière d'origine: {result.filière_origine}")
        print(f"* Centre d'interet: {result.centre_interet}")
        print(f"* Type de Bac+2: {result.type_bac2}")
        print(f"* Projet professionnel: {result.projet_professionnel}")
        print(f"* Série du Bac: {result.serie_bac}")
        print(f"* Matière préférée: {result.matière_préférée}")
    except Exception as e:
        print(f"Erreur lors de l'appel: {e}")