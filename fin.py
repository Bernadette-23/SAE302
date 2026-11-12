
import sys

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QMutex
from PyQt6.QtGui import QColor, QPen, QBrush, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout,
    QListWidget, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsRectItem,
    QMessageBox, QFrame
)


# ==================================================
# 1. CLASSE VEHICULE
# ==================================================

class Vehicules:

    def __init__(self, identifiant, position, destination, vitesse):
        self.id = identifiant
        self.position = position
        self.destination = destination
        self.vitesse = vitesse

    def __str__(self):
        return f"Ambulance {self.id}"


# ==================================================
# 2. CLASSES FEU ET CARREFOUR
# ==================================================

class Feu:

    def __init__(self, identifiant, position, couleur="vert"):
        self.id = identifiant
        self.position = position
        self.couleur = couleur

    def passer_au_vert(self):
        self.couleur = "vert"

    def passer_au_rouge(self):
        self.couleur = "rouge"


class Carrefour:

    def __init__(self, identifiant, feux):
        self.id = identifiant
        self.feux = feux

    def rechercher_feu(self, position):

        for feu in self.feux:

            if feu.position == position:
                return feu

            # On accepte aussi le sens inverse
            depart, arrivee = feu.position.split("-")

            if position == arrivee + "-" + depart:
                return feu

        return None


# ==================================================
# 3. ROUTES ET POSITIONS DES CARREFOURS
# ==================================================

routes = {
    "A": [("B", 5)],
    "B": [("A", 5), ("C", 4), ("D", 6), ("E", 3)],
    "C": [("B", 4), ("F", 2), ("J", 5)],
    "D": [("B", 6)],
    "E": [("B", 3), ("F", 5), ("G", 2), ("H", 6)],
    "F": [("E", 5), ("I", 5), ("C", 2)],
    "G": [("E", 2)],
    "H": [("E", 6)],
    "I": [("F", 5)],
    "J": [("C", 5)]
}


positions = {
    "I": (100, 70),
    "F": (100, 230),
    "C": (100, 430),
    "J": (100, 600),
    "H": (340, 70),
    "E": (340, 230),
    "B": (340, 430),
    "A": (340, 600),
    "G": (590, 230),
    "D": (590, 430)
}


# ==================================================
# 4. CREATION DES FEUX ET DES SEGMENTS
# ==================================================

segments = []
feux = []

numero_feu = 1

for depart in routes:

    for arrivee, cout in routes[depart]:

        # Vérifier si le feu existe déjà
        feu_existe = False

        for feu in feux:

            if feu.position == depart + "-" + arrivee:
                feu_existe = True

            if feu.position == arrivee + "-" + depart:
                feu_existe = True

        # Créer le feu seulement s'il n'existe pas
        if not feu_existe:

            feu = Feu(numero_feu, depart + "-" + arrivee)

            feux.append(feu)

            # Un segment représente une route entre deux carrefours
            segment = {
                "depart": depart,
                "arrivee": arrivee,
                "cout": cout,
                "feu": feu
            }

            segments.append(segment)

            numero_feu += 1


# Un carrefour contenant les feux de la maquette
carrefour = Carrefour(1, feux)


# Rechercher un segment entre deux carrefours

def trouver_segment(depart, arrivee):

    for segment in segments:

        if segment["depart"] == depart and segment["arrivee"] == arrivee:
            return segment

        if segment["depart"] == arrivee and segment["arrivee"] == depart:
            return segment

    return None


# ==================================================
# 5. ALGORITHME DE DIJKSTRA
# ==================================================

def dijkstra(routes, depart, destination):

    # On donne une distance infinie à chaque carrefour
    distances = {}

    for noeud in routes:
        distances[noeud] = float("inf")

    # Le départ est à une distance de 0
    distances[depart] = 0

    # Permet de savoir quels carrefours ont déjà été visités
    visites = []

    # Permet de savoir par quel carrefour on est passé
    precedents = {}

    for noeud in routes:
        precedents[noeud] = None

    # Tant qu'il reste des carrefours à visiter
    while len(visites) < len(routes):

        # Chercher le carrefour non visité avec
        # la plus petite distance
        noeud = None

        for n in routes:
            if n not in visites:
                if noeud is None or distances[n] < distances[noeud]:
                    noeud = n

        if noeud is None or distances[noeud] == float("inf"):
            break

        visites.append(noeud)

        # Regarder les routes qui partent de ce carrefour
        for voisin, cout in routes[noeud]:

            nouvelle_distance = distances[noeud] + cout

            # Si on trouve un chemin moins cher
            if nouvelle_distance < distances[voisin]:

                distances[voisin] = nouvelle_distance

                # On mémorise par où on est passé
                precedents[voisin] = noeud

    # Construire le chemin
    chemin = []
    noeud = destination

    while noeud is not None:
        chemin.append(noeud)
        noeud = precedents[noeud]

    # Le chemin est construit à l'envers
    chemin.reverse()

    return chemin, distances[destination]


# ==================================================
# 6. THREAD POUR CALCULER LES TRAJETS
# ==================================================


class CalculThread(QThread):

    # Le signal transmet l'identifiant de l'ambulance
    resultat = pyqtSignal(int)

    def __init__(self, identifiant, depart, destination,
                 mutex, resultats_partages):

        super().__init__()

        self.identifiant = identifiant
        self.depart = depart
        self.destination = destination

        # Ressources partagées
        self.mutex = mutex
        self.resultats_partages = resultats_partages

    def run(self):

        # Calcul du trajet
        chemin, cout = dijkstra(
            routes,
            self.depart,
            self.destination
        )

        # Demander l'accès au dictionnaire partagé
        self.mutex.lock()

        try:
            # Enregistrer le résultat
            self.resultats_partages[self.identifiant] = {
                "chemin": chemin,
                "cout": cout
            }

        finally:
            # Libérer le mutex, même en cas d'erreur
            self.mutex.unlock()

        # Prévenir la fenêtre que le résultat est disponible
        self.resultat.emit(self.identifiant)



# ==================================================
# 7. SIMULATION DES VOITURES ET DES AMBULANCES
# ==================================================

class Simulation(QWidget):

    def __init__(self, ambulances):
        super().__init__()

        self.ambulances = ambulances

        self.voitures = []
        self.donnees_voitures = []

        self.lampes = []

        self.finis = []

        layout = QVBoxLayout(self)

        self.info = QLabel(
            "Les ambulances sont prioritaires. "
            "Les voitures s'arrêtent devant les feux rouges."
        )

        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        # Zone dans laquelle on dessine la simulation
        self.scene = QGraphicsScene(0, 0, 700, 670)

        self.vue = QGraphicsView(self.scene)

        self.vue.setMinimumWidth(480)

        layout.addWidget(self.vue)

        # Tous les feux sont verts au début
        for feu in feux:
            feu.passer_au_vert()

        # Dessiner les différents éléments
        self.dessiner_routes()
        self.dessiner_feux()
        self.dessiner_carrefours()

        self.creer_voitures()
        self.creer_ambulances()

        # Le timer permet de faire avancer les véhicules
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.avancer)

        self.timer.start(35)


    # ----------------------------------------------
    # DESSINER LES ROUTES
    # ----------------------------------------------

    def dessiner_routes(self):

        for segment in segments:

            depart = segment["depart"]
            arrivee = segment["arrivee"]
            cout = segment["cout"]

            x1, y1 = positions[depart]
            x2, y2 = positions[arrivee]

            # Dessiner la route
            self.scene.addLine(
                x1, y1, x2, y2,
                QPen(QColor("#454545"), 18, Qt.PenStyle.SolidLine,
                     Qt.PenCapStyle.RoundCap)
            )

            # Dessiner le trait au milieu de la route
            self.scene.addLine(
                x1, y1, x2, y2,
                QPen(QColor("white"), 2, Qt.PenStyle.DashLine)
            )

            # Afficher le coût de la route
            texte = self.scene.addText(str(cout))

            texte.setDefaultTextColor(QColor("#14813b"))
            texte.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            texte.setPos(
                (x1 + x2) / 2 + 6,
                (y1 + y2) / 2 - 21
            )


    # ----------------------------------------------
    # DESSINER LES FEUX
    # ----------------------------------------------

    def dessiner_feux(self):

        # Pas de feu aux extrémités I, H, G, D, A et J
        extremites_sans_feu = ["I", "H", "G", "D", "A", "J"]

        for segment in segments:
            segment["lampes"]= []

            depart = segment["depart"]
            arrivee = segment["arrivee"]

            x1, y1 = positions[depart]
            x2, y2 = positions[arrivee]

            # Premier feu : proche du départ
            if depart not in extremites_sans_feu:

                x = x1 + (x2 - x1) * 0.18
                y = y1 + (y2 - y1) * 0.18

                lampe = self.scene.addEllipse(
                    x - 7, y - 7, 14, 14,
                    QPen(Qt.GlobalColor.black),
                    QBrush(QColor("#20a34a"))
                )

                self.lampes.append(lampe)
                segment["lampes"].append(lampe)

            # Deuxième feu : proche de l'arrivée
            if arrivee not in extremites_sans_feu:

                x = x1 + (x2 - x1) * 0.82
                y = y1 + (y2 - y1) * 0.82

                lampe = self.scene.addEllipse(
                    x - 7, y - 7, 14, 14,
                    QPen(Qt.GlobalColor.black),
                    QBrush(QColor("#20a34a"))
                )

                self.lampes.append(lampe)
                segment["lampes"].append(lampe)


    # ----------------------------------------------
    # DESSINER LES CARREFOURS
    # ----------------------------------------------

    def dessiner_carrefours(self):

        for nom in positions:

            x, y = positions[nom]

            self.scene.addEllipse(
                x - 12, y - 12, 24, 24,
                QPen(Qt.GlobalColor.black, 2),
                QBrush(QColor("#f5f5f5"))
            )

            texte = self.scene.addText(nom)

            texte.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            texte.setPos(x - 7, y - 39)


    # ----------------------------------------------
    # CREER LES VOITURES
    # ----------------------------------------------

    def creer_voitures(self):

        chemins = [
            ["A", "B", "C", "F", "E", "B", "D", "B", "A"],
            ["D", "B", "E", "G", "E", "F", "C", "B", "D"],
            ["J", "C", "B", "E", "H", "E", "F", "I", "F", "C", "J"]
        ]

        couleurs = ["#2878d0", "#e5a000", "#7b4ab5"]

        for i in range(len(chemins)):

            voiture = QGraphicsRectItem(-8, -5, 16, 10)

            voiture.setPen(QPen(Qt.GlobalColor.black))
            voiture.setBrush(QBrush(QColor(couleurs[i])))

            self.scene.addItem(voiture)

            self.voitures.append(voiture)

            donnees = {
                "chemin": chemins[i],
                "etape": 0,
                "progression": i * 0.25
            }

            self.donnees_voitures.append(donnees)


    # ----------------------------------------------
    # CREER LES AMBULANCES
    # ----------------------------------------------

    def creer_ambulances(self):

        for ambulance in self.ambulances:

            # Dessiner l'ambulance
            ambulance["item"] = QGraphicsRectItem(-12, -8, 24, 16)

            ambulance["item"].setPen(
                QPen(QColor("#b71c1c"), 2)
            )

            ambulance["item"].setBrush(
                QBrush(QColor("white"))
            )

            self.scene.addItem(ambulance["item"])

            # Ajouter une croix rouge
            ambulance["croix"] = self.scene.addText("+")

            ambulance["croix"].setDefaultTextColor(
                QColor("#d71920")
            )

            ambulance["croix"].setFont(
                QFont("Arial", 16, QFont.Weight.Bold)
            )

            self.scene.addItem(ambulance["croix"])

            ambulance["etape"] = 0
            ambulance["progression"] = 0.0
            ambulance["terminee"] = len(ambulance["chemin"]) < 2

            # Mémoriser les routes déjà parcourues
            ambulance["routes_parcourues"] = []

            if ambulance["terminee"]:
                self.finis.append(ambulance["id"])

            self.placer_ambulance(ambulance)


    # ----------------------------------------------
    # POSITIONNER UNE AMBULANCE
    # ----------------------------------------------

    def placer_ambulance(self, ambulance):

        chemin = ambulance["chemin"]

        nom = chemin[ambulance["etape"]]

        x, y = positions[nom]

        ambulance["item"].setPos(x, y)

        ambulance["croix"].setPos(x - 7, y - 18)


    # ----------------------------------------------
    # METTRE A JOUR LES FEUX
    # ----------------------------------------------

    def mettre_a_jour_feux(self):

        routes_rouges = []
        routes_vertes = []

        for ambulance in self.ambulances:

            if ambulance["terminee"]:
                continue

            chemin = ambulance["chemin"]
            etape = ambulance["etape"]

            if etape >= len(chemin) - 1:
                continue

            depart = chemin[etape]
            arrivee = chemin[etape + 1]

            # Le feu de la route actuelle passe au vert
            segment_actuel = trouver_segment(depart, arrivee)

            if segment_actuel is not None:
                routes_vertes.append(segment_actuel)

            # Les routes déjà parcourues repassent au rouge
            for segment in ambulance["routes_parcourues"]:

                if segment not in routes_rouges:
                    routes_rouges.append(segment)

            # Les routes qui croisent le prochain carrefour passent au rouge
            for voisin, cout in routes[arrivee]:

                segment = trouver_segment(arrivee, voisin)

                if segment != segment_actuel:

                    if segment not in routes_rouges:
                        routes_rouges.append(segment)

        # Mettre les feux rouges
        for segment in routes_rouges:

            segment["feu"].passer_au_rouge()

        # Les routes prioritaires restent vertes
        for segment in routes_vertes:

            segment["feu"].passer_au_vert()

            # Mettre à jour les lumières dessinées
            for segment in segments:

                if segment["feu"].couleur == "rouge":
                    couleur = QColor("#e53935")
                else:
                    couleur = QColor("#20a34a")

                for lampe in segment["lampes"]:
                    lampe.setBrush(QBrush(couleur))

            # Retrouver les deux lampes du segment
            depart = segment["depart"]
            arrivee = segment["arrivee"]

            x1, y1 = positions[depart]
            x2, y2 = positions[arrivee]

            index = 0

            for autre_segment in segments:

                if autre_segment == segment:
                    break

                a = autre_segment["depart"]
                b = autre_segment["arrivee"]

                if a not in ["I", "H", "G", "D", "A", "J"]:
                    index += 1

                if b not in ["I", "H", "G", "D", "A", "J"]:
                    index += 1

            nombre_lampes = 0

            if depart not in ["I", "H", "G", "D", "A", "J"]:
                self.lampes[index].setBrush(QBrush(couleur))
                nombre_lampes += 1

            if arrivee not in ["I", "H", "G", "D", "A", "J"]:
                self.lampes[index + nombre_lampes].setBrush(QBrush(couleur))


    # ----------------------------------------------
    # FAIRE AVANCER UNE VOITURE
    # ----------------------------------------------

    def avancer_voiture(self, voiture, donnees):

        chemin = donnees["chemin"]

        if len(chemin) < 2:
            return

        # Recommencer le parcours quand la voiture arrive au bout
        if donnees["etape"] >= len(chemin) - 1:

            donnees["etape"] = 0
            donnees["progression"] = 0.0

        depart = chemin[donnees["etape"]]
        arrivee = chemin[donnees["etape"] + 1]

        segment = trouver_segment(depart, arrivee)

        # Une voiture attend si le feu est rouge
        if donnees["progression"] == 0:

            if segment["feu"].couleur == "rouge":
                return

        # Faire avancer la voiture
        donnees["progression"] += 0.012

        t = donnees["progression"]

        x1, y1 = positions[depart]
        x2, y2 = positions[arrivee]

        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        voiture.setPos(x, y)

        # Passer au prochain segment
        if donnees["progression"] >= 1:

            donnees["etape"] += 1
            donnees["progression"] = 0.0


    # ----------------------------------------------
    # FAIRE AVANCER UNE AMBULANCE
    # ----------------------------------------------

    def avancer_ambulance(self, ambulance):

        if ambulance["terminee"]:
            return

        chemin = ambulance["chemin"]
        etape = ambulance["etape"]

        if etape >= len(chemin) - 1:

            ambulance["terminee"] = True

            if ambulance["id"] not in self.finis:
                self.finis.append(ambulance["id"])

            return

        depart = chemin[etape]
        arrivee = chemin[etape + 1]

        ambulance["progression"] += 0.005

        t = ambulance["progression"]

        x1, y1 = positions[depart]
        x2, y2 = positions[arrivee]

        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        ambulance["item"].setPos(x, y)
        ambulance["croix"].setPos(x - 7, y - 18)

        # Quand l'ambulance arrive au carrefour suivant
        if ambulance["progression"] >= 1:

            # Mémoriser la route qu'elle vient de parcourir
            segment = trouver_segment(depart, arrivee)

            ambulance["routes_parcourues"].append(segment)

            ambulance["etape"] += 1
            ambulance["progression"] = 0.0

            # Vérifier si elle est arrivée à destination
            if ambulance["etape"] >= len(chemin) - 1:

                ambulance["terminee"] = True

                if ambulance["id"] not in self.finis:
                    self.finis.append(ambulance["id"])


    # ----------------------------------------------
    # FONCTION PRINCIPALE DE LA SIMULATION
    # ----------------------------------------------

    def avancer(self):

        # Mettre à jour les feux
        self.mettre_a_jour_feux()

        # Faire avancer les voitures
        for i in range(len(self.voitures)):

            self.avancer_voiture(
                self.voitures[i],
                self.donnees_voitures[i]
            )

        # Faire avancer les ambulances
        for ambulance in self.ambulances:

            self.avancer_ambulance(ambulance)

        # Vérifier si toutes les ambulances sont arrivées
        if len(self.finis) == len(self.ambulances):

            self.mettre_a_jour_feux()

            self.timer.stop()

            self.info.setText(
                "Toutes les ambulances sont arrivées."
            )


# ==================================================
# 8. FENETRE PRINCIPALE
# ==================================================

class FenetrePrincipale(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Gestion des véhicules d'urgence")
        self.resize(1400, 850)

        # Listes qui mémorisent les données
        self.demandes = []
        self.threads = []
        self.calculs = []
        #Mutex pour protéger les résultats partagés
        self.mutex = QMutex()

        #Dictionnaires contenant les résultats des threads
        self.resultats_partages = {}

        self.prochaine_id = 1
        self.simulation = None

        # Organisation générale de la fenêtre
        principal = QHBoxLayout(self)

        # ==========================================
        # PANNEAU GAUCHE
        # ==========================================

        panneau_gauche = QWidget()

        gauche = QVBoxLayout(panneau_gauche)

        titre = QLabel("Gestion des ambulances")

        titre.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        gauche.addWidget(titre)

        gauche.addWidget(QLabel("Départ :"))

        self.depart = QComboBox()
        self.depart.addItems(routes.keys())

        gauche.addWidget(self.depart)

        gauche.addWidget(QLabel("Destination :"))

        self.destination = QComboBox()
        self.destination.addItems(routes.keys())

        gauche.addWidget(self.destination)

        self.ajouter = QPushButton("Ajouter une ambulance")
        self.lancer = QPushButton("Calculer et démarrer")
        self.reinitialiser = QPushButton("Nouvelle simulation")

        gauche.addWidget(self.ajouter)
        gauche.addWidget(self.lancer)
        gauche.addWidget(self.reinitialiser)

        gauche.addWidget(QLabel("Ambulances ajoutées :"))

        self.liste = QListWidget()
        gauche.addWidget(self.liste)

        gauche.addWidget(QLabel("Résultats de Dijkstra :"))

        self.resultats = QListWidget()
        gauche.addWidget(self.resultats)

        # ==========================================
        # PANNEAU DROIT
        # ==========================================

        panneau_droit = QWidget()

        droite = QVBoxLayout(panneau_droit)

        titre_simulation = QLabel("Simulation du carrefour")

        titre_simulation.setStyleSheet(
            "font-size: 18px; font-weight: bold;"
        )

        droite.addWidget(titre_simulation)

        self.placeholder = QLabel(
            "Ajoute une ambulance puis clique sur Calculer et démarrer."
        )

        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setFrameShape(QFrame.Shape.StyledPanel)

        droite.addWidget(self.placeholder)

        self.panneau_droit = panneau_droit

        principal.addWidget(panneau_gauche, 1)
        principal.addWidget(panneau_droit, 3)

        # ==========================================
        # CONNEXION DES BOUTONS
        # ==========================================

        self.ajouter.clicked.connect(self.ajouter_ambulance)
        self.lancer.clicked.connect(self.lancer_simulation)
        self.reinitialiser.clicked.connect(self.nouvelle_simulation)


    # ----------------------------------------------
    # AJOUTER UNE AMBULANCE
    # ----------------------------------------------

    def ajouter_ambulance(self):

        depart = self.depart.currentText()
        destination = self.destination.currentText()

        if depart == destination:

            QMessageBox.information(
                self,
                "Trajet",
                "Choisis deux carrefours différents."
            )

            return

        identifiant = self.prochaine_id

        self.prochaine_id += 1

        # Créer l'ambulance
        ambulance = Vehicules(
            identifiant,
            depart,
            destination,
            55
        )

        self.demandes.append(ambulance)

        self.liste.addItem(
            f"Ambulance {identifiant} : {depart} -> {destination}"
        )


    # ----------------------------------------------
    # LANCER LES CALCULS
    # ----------------------------------------------

    def lancer_simulation(self):

        if len(self.demandes) == 0:

            QMessageBox.information(
                self,
                "Ambulances",
                "Ajoute au moins une ambulance."
            )

            return

        self.lancer.setEnabled(False)
        self.ajouter.setEnabled(False)

        self.resultats.clear()

        self.calculs = []
        self.threads = []
        self.resultats_partages.clear()

        # Créer un thread pour chaque ambulance
        for ambulance in self.demandes:

            thread = CalculThread(
                ambulance.id,
                ambulance.position,
                ambulance.destination,
                self.mutex,
                self.resultats_partages
            )

            thread.resultat.connect(self.recevoir_resultat)

            self.threads.append(thread)

        # Démarrer tous les threads
        for thread in self.threads:

            thread.start()


    # ----------------------------------------------
    # RECEVOIR LES RESULTATS DES THREADS
    # ----------------------------------------------

    def recevoir_resultat(self, identifiant):

        # Accéder au dictionnaire partagé
        self.mutex.lock()

        try:
            resultat = self.resultats_partages[identifiant].copy()

        finally:
            self.mutex.unlock()

        # Récupérer les informations du résultat
        chemin = resultat["chemin"]
        cout = resultat["cout"]

        resultat = {
            "id": identifiant,
            "chemin": chemin,
            "cout": cout
        }

        self.calculs.append(resultat)

        if len(chemin) > 0:

            texte = " -> ".join(chemin)

            self.resultats.addItem(
                f"Ambulance {identifiant} : {texte} | Coût : {cout}"
            )

        else:

            self.resultats.addItem(
                f"Ambulance {identifiant} : aucun chemin."
            )

        # Vérifier si tous les calculs sont terminés
        if len(self.calculs) == len(self.demandes):

            self.lancer.setEnabled(True)
            self.ajouter.setEnabled(True)

            ambulances_valides = []

            for resultat in self.calculs:

                if len(resultat["chemin"]) > 0:

                    for ambulance in self.demandes:

                        if ambulance.id == resultat["id"]:
                            donnees = {
                                "id": ambulance.id,
                                "chemin": resultat["chemin"]
                            }

                            ambulances_valides.append(donnees)

            if len(ambulances_valides) > 0:

                self.afficher_simulation(ambulances_valides)

            else:

                QMessageBox.warning(
                    self,
                    "Trajets",
                    "Aucun trajet valide."
                )

    # ----------------------------------------------
    # AFFICHER LA SIMULATION
    # ----------------------------------------------

    def afficher_simulation(self, ambulances):

        # Supprimer l'ancienne simulation si nécessaire
        if self.simulation is not None:

            self.simulation.timer.stop()

            self.panneau_droit.layout().removeWidget(self.simulation)

            self.simulation.setParent(None)
            self.simulation.deleteLater()

        self.placeholder.hide()

        # Créer la nouvelle simulation
        self.simulation = Simulation(ambulances)

        self.panneau_droit.layout().addWidget(self.simulation)


    # ----------------------------------------------
    # RECOMMENCER UNE SIMULATION
    # ----------------------------------------------

    def nouvelle_simulation(self):

        if self.simulation is not None:

            self.simulation.timer.stop()

            self.panneau_droit.layout().removeWidget(self.simulation)

            self.simulation.setParent(None)
            self.simulation.deleteLater()

            self.simulation = None

        self.demandes.clear()
        self.calculs.clear()
        self.threads.clear()

        self.liste.clear()
        self.resultats.clear()

        self.prochaine_id = 1

        self.placeholder.show()

        self.lancer.setEnabled(True)
        self.ajouter.setEnabled(True)


# ==================================================
# 9. LANCEMENT DU PROGRAMME
# ==================================================

if __name__ == "__main__":

    app = QApplication(sys.argv)

    fenetre = FenetrePrincipale()

    fenetre.show()

    sys.exit(app.exec())
