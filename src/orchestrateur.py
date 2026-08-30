# Le controleur ou l'orchestrateur joue un role essentiel dans l'architecture de notre système
class orchestrateur:
    """L'orchestrateur joue plusieurs roles majeurs dans l'architecture de notre système:
    * Gère la mémoire de session: C'est lui accumule les informations fournies par l'utilisateur tout au long de la discussion;
    * Pipeline de communication: Il reçoit le message brut de l'utilisateur, le transmet au module NLP et récupère l'objet pydantic
      généré; Il injecte ensuite l'objet pydantic dans le moteur d'inférence et le lance;
    * Détection des informations manquantes et Génération des relances: En fonction des réponses du moteur d'inférence, il est capable
      de détecter s'il manque des données et de demander à la l'utilisateur de fournir plus de précisions sur son profil."""
      
    def __init__(self, module_nlp, moteur_expert):
        """Initialisation de l'orchestrateur avec le module NLP et le moteur expert"""
        self.nlp = module_nlp
        self.moteur = moteur_expert
        # C'est dans l'attribut profi_complet que nous allons stocker toutes les infos relatives au profil de l'étudiant
        self.profi_complet = {}
        
    def update_profil(self, infos:dict):
        """Cette méthode permet de mettre à jour le profil de l'étudiant en ajoutant de nouvelles informations sur le profil
        de l'étudiant à celle déjà connues"""
        for clé, valeur in infos.items():
            if valeur is not None:
                self.profi_complet[clé] = valeur
                
    def _résultat_inférence(self):
        """Cette méthode inspecete la mémoire de travail du moteur expert post-inférence pour déterminer la réponse appropriée à
        retourner"""
        proposition_orientation = None
        décision_éligibilité = None
        
        # On parcours les faits métiers présents dans le moteur après execution
        for fact_id, fact in self.moteur.facts.items():
            # si le fait contient la clé éligible, c'est la phase à aboutie
            if 'éligible' in fact:
                décision_éligibilité = fact
            # Si le fait contient la clé débouchés, la phase 1 à généré une proposition
            elif 'débouchés' in fact:
                proposition_orientation  = fact
                
        # Cas 1: Décision d'éligibilité rendue
        if décision_éligibilité :
            return {
                "statut" : "SUCCES",
                "étape" : "Eligibilité",
                "éligible" : décision_éligibilité["élibible"],
                "filière" : décision_éligibilité["filière"],
                "messsage" : décision_éligibilité["motif"]
            }
        # cas 2: Orientation proposée mais éligibilité incomplète (données insuffisantes)
        if proposition_orientation:
            return {
                "statut" : "INCOMPLET",
                "étape" : "Orientation",
                "proposition" : proposition_orientation["filière"],
                "débouchés" : proposition_orientation["débouchés"],
                "messsage" : "Orientation identifiée, mais il manque des informations académiques pour vérifier votre éligibilité"
            }
        # cas 3: Aucune règle ne s'est déclanchée
        return {
            "statut" : "INCOMPLET",
            "étape" : "Initialisation",
            "messsage" : "Informations insuffisantes pour orienter ou vérifier l'éligibilité"
        }
                
    def traitement_message(self, message:str):
        """Cette méthode orchestre tout le voyage de l'information, du message brut envoyé par l'utilisateur jusqu'à la prise de
        désicion par le système"""
        
        # Extraction des données du message texte grace à Gemini + Pydantic
        msg_extrait = self.nlp.extraire_données(message)
        données_extraites = msg_extrait.model_dump()
        
        # On ajoute ces nouvelles infos à la mémoire de travail
        self.update_profil(données_extraites)
        
        # On prépare le moteur avec des données à jour
        self.moteur.reset()
        self.moteur.load_facts_nlp(self.profi_complet)
        
        # Puis on lance le raisonnement
        self.moteur.run()
        
        # Puis on analyse le résultat du moteur
        self._résultat_inférence()
        
        return self._résultat_inférence()