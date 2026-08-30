# C'est ici que nous allons coder nos faits, le moteur d'inférence et les règles métier que celui-ci appliquera.

# Gestion de compatibilté entre Experta et les versions récentes de python
import collections
import collections.abc

collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping


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
    # Etape: Orientation ou Eligibilité
    étape = Field(str)
    
    
class faits_métier(Fact):
    """On utilise les variables 'clé' et 'valeur' pour capter les faits de l'utilisateur. En effet,les faits sont transmis au
    système sous forme de dictionnaire python. Capter les données de l'utilisateur avec ces deux variables offre plusieurs
    avantages: d'abord, cela facilite la communication entre la couche NLP et le moteur; Ensuite, cela rend le système beacoup plus
    flexible et dynamique car il sera possible d'ajouter bien plus de faits plutard sans toucher au code si le système évoulue."""
    clé = Field(str)
    valeur = Field(object)
    
    
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
    
    
# Moteur d'inférence
class moteur_inférence(KnowledgeEngine):
    
    ##################################################
    # Chargement des faits métier depuis le module nlp
    def load_facts_nlp(self, pydantic_fact):
        """Cette méthode convertit l'objet pydantic généré par le NLP en faits métiers pour le moteur d'inférence"""
        
        # Conversions de l'objet pydantic en dictionnaire python
        données = pydantic_fact.model_dump()
        
        # Niveau étudiant
        niveau_etu = données.get('niveau')
        if niveau_etu:
            self.declare(niveau_étudiant(niveau = niveau_etu))
            # Mappage des clés pydantic vers les clés attendus les règles métiers
            map_clé = {
                'matière_préférée':'matière préférée', 'serie_bac':'série_bac', 'note_maths':'note_maths',
                'note_physique':'note_physique', 'note_chimie':'note_chimie', 'filière_origine':'filière_origine',
                'centre_interet':'centre_interet', 'cursus_choisi':'filière choisie', 'provenance_bac2':'provenance',
                'type_bac2':'type_bac2'
            }
            for cle_pydantic, valeur in données.items():
                if cle_pydantic != 'niveau' and valeur is not None:
                    cle_métier = map_clé.get(cle_pydantic, cle_pydantic)
                    self.declare(faits_métier(clé = cle_métier, valeur = valeur))
        
    @Rule(niveau_étudiant(niveau='Bac'))
    def scenario_Bac(self):
        self.declare(scénario_adéquat(scénario='Bac', étape='Orientation'))
        
    @Rule(niveau_étudiant(niveau='Bac+2'))
    def scenario_Bac2(self):
        self.declare(scénario_adéquat(scénario='Bac+2', étape='Orientation'))
        
    # règles métiers dédiées au scénario BAC
    ########################################
    
    # phase 1: Proposition de la filière
    ####################################
    
    # matière préférée informatique
    @Rule(scénario_adéquat(scénario='Bac', étape='Orientation'), faits_métier(clé='matière préférée', valeur='Informatique'))
    def règle_ori_bac_info(self):
        self.declare(proposition_filière(id_règle='R_Ori_01', filière='Informatique/GID',
            débouchés='Spécialiste en Data, Admin système et réseaux, Développeur web/applications'))
        self.declare(scénario_adéquat(scénario='Bac', étape='Eligibilité'))
        
    # matière préférée Mathématique
    @Rule(scénario_adéquat(scénario='Bac', étape='Orientation'), faits_métier(clé='matière préférée', valeur='Mathématique'))
    def règle_ori_bac_maths(self):
        self.declare(proposition_filière(id_règle='R_Ori_02', filière='Mathématique',
            débouchés="Ingénierie, Génie minier et férroviaire, Métiers des finances, Enseignement"))
        self.declare(scénario_adéquat(scénario='Bac', étape='Eligibilité'))
        
    # matière préférée Physique
    @Rule(scénario_adéquat(scénario='Bac', étape='Orientation'), faits_métier(clé='matière préférée', valeur='Physique'))
    def règle_ori_bac_physique(self):
        self.declare(proposition_filière(id_règle='R_Ori_03', filière='Physique',
             débouchés='Ingénierie, Aéronotique, Energie Renouvelable'))
        self.declare(scénario_adéquat(scénario='Bac', étape='Eligibilité'))
         
    # matière préférée chimie
    @Rule(scénario_adéquat(scénario='Bac', étape='Orientation'), faits_métier(clé='matière préférée', valeur='Chimie'))
    def règle_ori_bac_chimie(self):
        self.declare(proposition_filière(id_règle='R_Ori_04', filière='Chimie',
             débouchés='Industrie agro-alimentaire et pharmaceutique, Métallurgie, Petrochimie, Electrochimie'))
        self.declare(scénario_adéquat(scénario='Bac', étape='Eligibilité'))
        
    #matière préférée sciences biologiques
    @Rule(scénario_adéquat(scénario='Bac', étape='Orientation'), faits_métier(clé='matière préférée', valeur='sciences biologiques'))
    def règle_ori_bac_sciences_biologiques(self):
        self.declare(proposition_filière(id_règle='R_Ori_05', filière='Sciences Biologiques',
            débouchés='Agronomie, Foresterie, Ecologie, Bio Informatique'))
        self.declare(scénario_adéquat(scénario='Bac', étape='Eligibilité'))
        
    #matière préférée sciences de la terre
    @Rule(scénario_adéquat(scénario='Bac', étape='Orientation'), faits_métier(clé='matière préférée', valeur='sciences de la terre'))
    def règle_ori_bac_sciences_de_la_terre(self):
        self.declare(proposition_filière(id_règle='R_Ori_06', filière='Sciences de la Terre',
             débouchés='Exploitation des minerais et des matériaux, Géochimiste, Gestion des sols, Génie civil'))
        self.declare(scénario_adéquat(scénario='Bac', étape='Eligibilité'))
        
    
    # phase 2: Vérification de l'éligibilité
    ########################################
    
    # Filière Informatique : Eligible pour tous les Bac Scientifiques sans aucune conditions de note
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Informatique'),
          faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(lambda s: s in ['C','D','E','F','GCE sc','TI']))
    def r_eli_01(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Informatique', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Mathématique : Eligible pour les Bac C, E, GCE sc sans condition de note
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Mathématique'),
          faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(lambda s: s in ['C','E','GCE sc']))
    def r_eli_02(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Mathématique', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Mathématique : Eligible pour les Bac D avec condition sur la note de maths
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Mathématique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.n), TEST(
              lambda n: n>= 12))
    def r_eli_03(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Mathématique', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Mathématique : Cas des Bac D dont la note de maths est insuffisante
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Mathématique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.n), TEST(
              lambda n: n<12))
    def r_eli_04(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Mathématique', motif = ("Malheureusement, ta note en maths \
            ne te permet pas d'entrer dans cette filière. Mais avec ton profil, tu es éligible sans condition en Informatique \
                ou en Sciences de la Terre.")))
        
    # Filière Chimie ou physique: Eligible pour les Bac C, E, F sans aucune condition de note
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = MATCH.f), TEST(
        lambda f: f in ['Chimie', 'Physique']), faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(lambda s: s in ['C', 'E', 'F']))
    def r_eli_05(self, f):
        self.declare(y_n_éligible(éligible = True, filière = f, motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Chimie: cas des Bac D avec conditions sur les notes de maths et/ou chimie
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Chimie'),
        faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
        faits_métier(clé = 'note_chimie', valeur = MATCH.nc), TEST(lambda nm, nc : nm >= 10 or nc >= 10))
    def r_eli_06(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Chimie', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
     # Filière Chimie: cas des Bac D dont les notes de maths et/ou de chimie sont insuffisantes
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Chimie'),
           faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
           faits_métier(clé = 'note_chimie', valeur = MATCH.nc), TEST(lambda nm, nc : nm < 10 and nc < 10))
    def r_eli_07(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Chimie', motif = ("Les sciences dures requiert une base solide dans\
            les matières scientifiques. Ton profil serait plus adapté en Informatique ou en Biologie.")))
        
    # Filière Physique: cas des Bac D avec conditions sur les notes de maths et/ou chimie
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Physique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
          faits_métier(clé = 'note_physique', valeur = MATCH.np), TEST(lambda nm, np : nm >= 10 or np >= 10))
    def r_eli_08(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Physique', motif ='Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Physique: cas des Bac D dont les notes de maths et/ou de Physique sont insuffisantes
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Physique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
          faits_métier(clé = 'note_physique', valeur = MATCH.np), TEST(lambda nm, np : nm < 10 and np < 10))
    def r_eli_09(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Physique', motif = ("Les sciences dures requiert une base solide dans\
            les matières scientifiques. Ton profil serait plus adapté en Informatique ou en Sciences Géologiques.")))
        
    # Filière Sciences de la Vie et de la Terre
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = MATCH.f), TEST(
        lambda f: f in ["Sciences Biologiques", "Sciences de la Terre", "Biologie"]), faits_métier(clé = 'série_bac', valeur = \
            MATCH.s), TEST(lambda s: s in ['C', 'D', 'F', 'GCE sc']))
    def r_eli_10(self, f):
        self.declare(y_n_éligible(éligible = True, filière = f, motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Baccalauréats littéraires
    @Rule(scénario_adéquat(scénario = 'Bac', étape='Eligibilité'), faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(
        lambda s: s in ['Littéraire', 'Technique', 'A4', 'ABI', 'CG', 'ACC', 'FGI']))
    def r_eli_11(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Toutes filières', motif = "Les filières de la Faculté des Sciences \
            requièrent baccalauréats scientifiques ou techniques."))
        
    
    # règles métiers dédiées au scénario BAC+2
    ##########################################
    
    # phase 1: Proposition de la filière
    ####################################
    
    # Orientation en LIDA
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Orientation'), faits_métier(clé = "filière_origine", valeur = MATCH.f), TEST(lambda f: f in [
        'Informatique', 'Mathématique', 'Physique', 'Génie Logiciel', 'Réseaux']), faits_métier(clé = 'centre_interet', valeur = MATCH.ci),
          TEST( lambda ci: ci in ['code', 'Développement', 'Data', 'IA', 'Objet connectés']))
    def règle_ori_bac2_LIDA(self):
        self.declare(proposition_filière(id_règle = 'R_ori_bac2_01', filière = 'Licence Pro LIDA',
        débouchés = 'Ingénieur en système embarqués, Développeur Web, Mobile, Logiciel, Analyste BI, Data Scientist'))
        self.declare(scénario_adéquat(scénario='Bac+2', étape='Eligibilité'))
        
    # Orientation en TL
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Orientation'), faits_métier(clé = "filière_origine", valeur = MATCH.f), TEST(lambda f: f in [
        'Chimie', 'Biochimie', 'Biologie', 'Science de la vie']), faits_métier(clé = 'centre_interet', valeur = MATCH.ci), 
           TEST( lambda ci: ci in ['Laboratoire', 'Cosmétique']))
    def règle_ori_bac2_TL(self):
        self.declare(proposition_filière(id_règle = 'R_ori_bac2_02', filière = 'Licence Pro Techniques des Laboratoires',
        débouchés = 'Analyste Biomédicale, Vétérinaire'))
        self.declare(scénario_adéquat(scénario='Bac+2', étape='Eligibilité'))
        
    # Orientation en MIME
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Orientation'), faits_métier(clé = "filière_origine", valeur = MATCH.f), TEST(lambda f: f in [
        'Biochimie', 'Microbiologie']), faits_métier(clé = 'centre_interet', valeur = MATCH.ci), TEST( lambda ci: ci in [
            'Bactérie', 'Diagnostic', 'Santé', 'Virus']))
    def règle_ori_bac2_MIME(self):
        self.declare(proposition_filière(id_règle = 'R_ori_bac2_03', filière = 'Licence Pro MIME', débouchés = 'Industries Pharmaceutique, Industries des ferments'))
        self.declare(scénario_adéquat(scénario='Bac+2', étape='Eligibilité'))
    
    # Orientation en filières classiques    
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Orientation'), faits_métier(clé = "filière_origine", valeur = MATCH.f), TEST(lambda f: f in [
        'Mathématique', 'Physique', 'Chimie',]) , faits_métier(clé = 'centre_interet', valeur = MATCH.ci), TEST( lambda ci: ci in [
            'Recherche', 'Enseignement', 'Doctorat', 'Longues études']))
    def règle_ori_bac2_classique(self):
        self.declare(proposition_filière(id_règle = 'R_ori_bac2_04', filière = 'Licence 3 classique', débouchés = 'Docteur, Professeur'))
        self.declare(scénario_adéquat(scénario='Bac+2', étape='Eligibilité'))
        
    # phase 2: Vérification de l'éligibilité
    ########################################
    
    # Licence Pro LIDA/TL/MIME ouverte aux Bac+ pro ou classiques
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = MATCH.c), TEST(lambda c: c in [
        'Licence Pro LIDA', 'Licence Pro MIME', 'Licence Pro Techniques des Laboratoires']), faits_métier(clé = 'type_bac2', valeur = MATCH.t),
          TEST(lambda t: t in ['Classique', 'Professionel']))
    def r_eli_bac2_01(self, c):
        self.declare(y_n_éligible(éligible = True, filière = c, motif = "Dossier pré-validé + Document requis"))
        
    # L3 classique accessible si Bac+2 classique d'Université d'Etat
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Licence 3 Classique'),
          faits_métier(clé = 'type_bac2', valeur = 'Classique'), faits_métier(clé = 'provenance', valeur = "Université d'Etat"))
    def r_eli_bac2_02(self):
        self.declare(y_n_éligible(éligible = True, filière='Licence 3 Calssique', motif = "Dossier pré-validé + Document requis"))
        
    # L3 classique resufé si Bac+2 professionnel
    @Rule(scénario_adéquat(scénario = 'Bac+2', étape='Eligibilité'), faits_métier(clé = 'filière choisie', valeur = 'Licence 3 Classique'),
          faits_métier(clé = 'type_bac2', valeur = 'Professionnel'))
    def r_eli_bac2_03(self):
        self.declare(y_n_éligible(éligible = False, filière='Non éligibe en filière classique', motif = "Réorientation en filière pro selon le profil du candidat"))
        
####################################################################
# Test : Simulation de la réception d'un objet pydantic du moule NLP
if __name__ == '__main__':
    class Fake_pydantic_result:
        def model_dump(self):
            return {'niveau':'Bac', 'serie_bac':'D', 'matière_préférée':'Informatique', 'cursus_choisi':'Informatique'}
        
    moteur = moteur_inférence()
    moteur.reset()
        
    moteur.load_facts_nlp(Fake_pydantic_result())
    moteur.run()

    for fact_id, fact in moteur.facts.items():
        print(f"Fait {fact_id}: {dict(fact)}")