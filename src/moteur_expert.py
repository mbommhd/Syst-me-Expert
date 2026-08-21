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
    @Rule(niveau_étudiant(niveau='Bac'))
    def scenario_Bac(self):
        self.declare(scénario_adéquat(scénario='scénario Bac'))
        
    @Rule(niveau_étudiant(niveau='Bac+2'))
    def scenario_Bac2(self):
        self.declare(scénario_adéquat(scénario='scénario Bac+2'))
        
    # règles métiers dédiées au scénario BAC
    ########################################
    
    # phase 1: Proposition de la filière
    ####################################
    
    # matière préférée informatique
    @Rule(scénario_adéquat(scénario='Bac'), faits_métier(clé='matière préférée', valeur='Informatique'))
    def règle_ori_bac_info(self):
        self.declare(proposition_filière(id_règle='R_Ori_01', filière='Informatique/GID',
            débouchés='Spécialiste en Data, Admin système et réseaux, Développeur web/applications'))
        
    # matière préférée Mathématique
    @Rule(scénario_adéquat(scénario='Bac'), faits_métier(clé='matière préférée', valeur='Mathématique'))
    def règle_ori_bac_maths(self):
        self.declare(proposition_filière(id_règle='R_Ori_02', filière='Mathématique',
            débouchés="Ingénierie, Génie minier et férroviaire, Métiers des finances, Enseignement"))
        
    # matière préférée Physique
    @Rule(scénario_adéquat(scénario='Bac'), faits_métier(clé='matière préférée', valeur='Physique'))
    def règle_ori_bac_physique(self):
        self.declare(proposition_filière(id_règle='R_Ori_03', filière='Physique',
             débouchés='Ingénierie, Aéronotique, Energie Renouvelable'))
         
    # matière préférée chimie
    @Rule(scénario_adéquat(scénario='Bac'), faits_métier(clé='matière préférée', valeur='Chimie'))
    def règle_ori_bac_chimie(self):
        self.declare(proposition_filière(id_règle='R_Ori_04', filière='Chimie',
             débouchés='Industrie agro-alimentaire et pharmaceutique, Métallurgie, Petrochimie, Electrochimie'))
        
    #matière préférée sciences biologiques
    @Rule(scénario_adéquat(scénario='Bac'), faits_métier(clé='matière préférée', valeur='sciences biologiques'))
    def règle_ori_bac_sciences_biologiques(self):
        self.declare(proposition_filière(id_règle='R_Ori_05', filière='Sciences Biologiques',
            débouchés='Agronomie, Foresterie, Ecologie, Bio Informatique'))
        
    #matière préférée sciences de la terre
    @Rule(scénario_adéquat(scénario='Bac'), faits_métier(clé='matière préférée', valeur='sciences de la terre'))
    def règle_ori_bac_sciences_de_la_terre(self):
        self.declare(proposition_filière(id_règle='R_Ori_06', filière='Sciences de la Terre',
             débouchés='Exploitation des minerais et des matériaux, Géochimiste, Gestion des sols, Génie civil'))
        
    
    # phase 2: Vérification de l'éligibilité
    ########################################
    
    # Filière Informatique : Eligible pour tous les Bac Scientifiques sans aucune conditions de note
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Informatique'),
          faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(lambda s: s in ['C','D','E','F','GCE sc','TI']))
    def r_eli_01(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Informatique', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Mathématique : Eligible pour les Bac C, E, GCE sc sans condition de note
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Mathématique'),
          faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(lambda s: s in ['C','E','GCE sc']))
    def r_eli_02(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Mathématique', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Mathématique : Eligible pour les Bac D avec condition sur la note de maths
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Mathématique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.n), TEST(
              lambda n: n>= 12))
    def r_eli_03(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Mathématique', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Mathématique : Cas des Bac D dont la note de maths est insuffisante
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Mathématique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.n), TEST(
              lambda n: n<12))
    def r_eli_04(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Mathématique', motif = ("Malheureusement, ta note en maths \
            ne te permet pas d'entrer dans cette filière. Mais avec ton profil, tu es éligible sans condition en Informatique \
                ou en Sciences de la Terre.")))
        
    # Filière Chimie ou physique: Eligible pour les Bac C, E, F sans aucune condition de note
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = MATCH.f), TEST(
        lambda f: f in ['Chimie', 'Physique'], faits_métier(clé = 'série_bac', valeur = MATCH.s & TEST(lambda s: s in ['C', 'E', 'F']))))
    def r_eli_05(self, f):
        self.declare(y_n_éligible(éligible = True, filière = f, motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Chimie: cas des Bac D avec conditions sur les notes de maths et/ou chimie
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Chimie'),
        faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
        faits_métier(clé = 'note_chimie', valeur = MATCH.nc), TEST(lambda nm, nc : nm >= 10 or nc >= 10))
    def r_eli_06(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Chimie', motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
     # Filière Chimie: cas des Bac D dont les notes de maths et/ou de chimie sont insuffisantes
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Chimie'),
           faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
           faits_métier(clé = 'note_chimie', valeur = MATCH.nc), TEST(lambda nm, nc : nm < 10 and nc < 10))
    def r_eli_07(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Chimie', motif = ("Les sciences dures requiert une base solide dans\
            les matières scientifiques. Ton profil serait plus adapté en Informatique ou en Biologie.")))
        
    # Filière Physique: cas des Bac D avec conditions sur les notes de maths et/ou chimie
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Physique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
          faits_métier(clé = 'note_physique', valeur = MATCH.np), TEST(lambda nm, np : nm >= 10 or np >= 10))
    def r_eli_08(self):
        self.declare(y_n_éligible(éligible = True, filière = 'Physique', motif ='Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Filière Physique: cas des Bac D dont les notes de maths et/ou de Physique sont insuffisantes
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = 'Physique'),
          faits_métier(clé = 'série_bac', valeur = 'D'), faits_métier(clé = 'note_maths', valeur = MATCH.nm),
          faits_métier(clé = 'note_physique', valeur = MATCH.np), TEST(lambda nm, np : nm < 10 and np < 10))
    def r_eli_09(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Physique', motif = ("Les sciences dures requiert une base solide dans\
            les matières scientifiques. Ton profil serait plus adapté en Informatique ou en Sciences Géologiques.")))
        
    # Filière Sciences de la Vie et de la Terre
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'filière choisie', valeur = MATCH.f), TEST(
        lambda f: f in ["Sciences Biologiques", "Sciences de la Terre", "Biologie"]), faits_métier(clé = 'série_bac', valeur = \
            MATCH.s), TEST(lambda s: s in ['C', 'D', 'F', 'GCE sc']))
    def r_eli_10(self, f):
        self.declare(y_n_éligible(éligible = True, filière = f, motif = 'Félicitations + Document requis + Procédure \
            de préinscription en ligne'))
        
    # Baccalauréats littéraires
    @Rule(scénario_adéquat(scénario = 'Bac'), faits_métier(clé = 'série_bac', valeur = MATCH.s), TEST(
        lambda s: s in ['Littéraire', 'Technique', 'A4', 'ABI', 'CG', 'ACC', 'FGI']))
    def r_eli_11(self):
        self.declare(y_n_éligible(éligible = False, filière = 'Toutes filières', motif = "Les filières de la Faculté des Sciences \
            requièrent baccalauréats scientifiques ou techniques."))
        
    