
"""
Module principal de l'application de gestion des véhicules d'urgence.
Il contient les classes de gestion des véhicules et des feux, le réseau
routier ainsi que le traitement des demandes de calcul de trajet.
"""

import sys

from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal, QMutex, QSemaphore
from PyQt6.QtGui import QColor, QPen, QBrush, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout,
    QListWidget, QGraphicsView, QGraphicsScene,
    QGraphicsEllipseItem, QGraphicsRectItem,
    QMessageBox, QFrame
)
from client.client import envoyer_demande


# ==================================================
# 1. CLASSE VEHICULE
# ==================================================

class Vehicules:
    """
    Représente un véhicule d'urgence avec son identifiant,
    sa position de départ, sa destination et sa vitesse.
    """

    def __init__(self, identifiant, position, destination, vitesse):
        """
        Initialise un véhicule avec ses principales caractéristiques
        afin de mémoriser les informations nécessaires à son trajet.
        """
        self.id = identifiant
        self.position = position
        self.destination = destination
        self.vitesse = vitesse

    def __str__(self):
        """
        Retourne une représentation textuelle du véhicule
        contenant son identifiant.
        """
        return f"Ambulance {self.id}"


# ==================================================
# 2. CLASSES FEU ET CARREFOUR
# ==================================================

class Feu:
    """
    Représente un feu de circulation associé à une route
    et permet de gérer son état (vert ou rouge).
    """

    def __init__(self, identifiant, position, couleur="vert"):
        """
        Initialise un feu avec son identifiant, sa position
        sur le réseau et sa couleur initiale.
        """
        self.id = identifiant
        self.position = position
        self.couleur = couleur

    def passer_au_vert(self):
        """
        Modifie l'état du feu pour autoriser la circulation
        sur la route concernée.
        """
        self.couleur = "vert"

    def passer_au_rouge(self):
        """
        Modifie l'état du feu pour interrompre la circulation
        sur la route concernée.
        """
        self.couleur = "rouge"


class Carrefour:
    """
    Représente un carrefour composé de plusieurs feux
    et permet de retrouver un feu à partir de sa position.
    """

    def __init__(self, identifiant, feux):
        """
        Initialise un carrefour avec son identifiant
        et la liste des feux qui lui sont associés.
        """
        self.id = identifiant
        self.feux = feux

    def rechercher_feu(self, position):
        """
        Recherche un feu correspondant à une route donnée.
        La recherche fonctionne dans les deux sens de circulation.
        """
        for feu in self.feux:

            if feu.position == position:
                return feu

            # On accepte également la route dans le sens inverse
            depart, arrivee = feu.position.split("-")

            if position == arrivee + "-" + depart:
                return feu

        # Aucun feu correspondant à la position n'a été trouvé
        return None


# ==================================================
# 3. ROUTES ET POSITIONS DES CARREFOURS
# ==================================================

# Représentation du réseau routier sous forme de graphe.
# Chaque intersection est associée à ses voisines et au coût du trajet.
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


# Coordonnées graphiques de chaque intersection dans la simulation
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

# Parcours du graphe pour créer les feux et les segments routiers
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


# Création d'un carrefour regroupant les feux de la maquette
carrefour = Carrefour(1, feux)



def trouver_segment(depart, arrivee):
    """
    Recherche le segment reliant deux intersections.
    La recherche prend en compte les deux sens de circulation.
    """
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
    """
    Calcule le chemin de coût minimal entre deux intersections
    à partir du graphe routier et retourne le chemin ainsi que son coût.
    """

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

        # Arrêt lorsqu'il ne reste plus d'intersection accessible
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
    """
    Thread chargé d'envoyer une demande de calcul de trajet au serveur
    sans bloquer l'interface graphique pendant son traitement.
    """

    # Signal envoyé à la fenêtre principale lorsque le calcul est terminé
    resultat = pyqtSignal(int)

    def __init__(self, identifiant, depart, destination,
                 mutex, resultats_partages, semaphore):
        """
        Initialise le thread avec les informations du trajet
        et les outils de synchronisation utilisés entre les threads.
        """
        super().__init__()

        self.identifiant = identifiant
        self.depart = depart
        self.destination = destination

        self.mutex = mutex
        self.resultats_partages = resultats_partages
        self.semaphore = semaphore

    def run(self):
        """
        Exécute la demande de trajet auprès du serveur, récupère le résultat
        et le stocke dans le dictionnaire partagé de manière sécurisée.
        """

        # Attendre qu'une place soit disponible
        self.semaphore.acquire()

        try:
            try:
                # Envoyer la demande au serveur
                reponse = envoyer_demande(
                    self.depart,
                    self.destination
                )

                # Transformer une réponse d'erreur en résultat exploitable
                if "erreur" in reponse:
                    resultat = {
                        "chemin": [],
                        "cout": None,
                        "erreur": reponse["erreur"]
                    }

                else:
                    # Récupérer le chemin et son coût si le calcul a réussi
                    resultat = {
                        "chemin": reponse["chemin"],
                        "cout": reponse["cout"],
                        "erreur": None
                    }

            except (OSError, ValueError, KeyError) as erreur:

                # Enregistrer l'erreur rencontrée pendant la communication
                resultat = {
                    "chemin": [],
                    "cout": None,
                    "erreur": str(erreur)
                }

            # Protéger le dictionnaire partagé
            self.mutex.lock()

            try:
                self.resultats_partages[self.identifiant] = resultat

            finally:
                # Libérer le mutex même si l'enregistrement échoue
                self.mutex.unlock()

        finally:
            # Libérer le sémaphore
            self.semaphore.release()

        # Informer la fenêtre principale que le résultat est disponible
        self.resultat.emit(self.identifiant)


class PanneauClickable(QGraphicsRectItem):

    def __init__(self, x, y, largeur, hauteur, action):
        super().__init__(x, y, largeur, hauteur)

        self.action = action

        self.setAcceptedMouseButtons(
            Qt.MouseButton.LeftButton
        )

    def mousePressEvent(self, event):
        self.action()
        event.accept()

# ==================================================
# 7. SIMULATION DES VOITURES ET DES AMBULANCES
# ==================================================

class Simulation(QWidget):
    """
    Gère la simulation graphique du réseau routier, des feux
    de circulation, des voitures et des ambulances.
    """

    def __init__(self, ambulances):
        """
        Initialise la fenêtre de simulation, prépare les éléments
        graphiques et démarre le déplacement automatique des véhicules.
        """
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

        # Créer l'écran de zoom
        self.zoom_widget = QWidget()
        zoom_layout = QVBoxLayout(self.zoom_widget)

        self.message_zoom = QLabel()
        self.message_zoom.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.message_zoom.setStyleSheet("""
            background-color: yellow;
            color: black;
            font-size: 24px;
            font-weight: bold;
            padding: 40px;
        """)

        zoom_layout.addWidget(self.message_zoom)

        # Bouton pour revenir à la simulation
        self.bouton_retour = QPushButton(
            "Retour à la simulation"
        )

        self.bouton_retour.clicked.connect(
            self.retour_simulation
        )

        zoom_layout.addWidget(self.bouton_retour)

        layout.addWidget(self.zoom_widget)

        self.zoom_widget.hide()

        # Tous les feux sont verts au début
        for feu in feux:
            feu.passer_au_vert()

        # Dessiner les différents éléments
        self.dessiner_routes()
        self.dessiner_panneaux()
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
    def afficher_zoom(self, segment):

        # Ne pas ouvrir le zoom si le panneau est noir
        if not segment["actif"]:
            return

        self.message_zoom.setText(
            "ATTENTION !\n\n"
            "AMBULANCE\n\n"
            "DÉCALEZ-VOUS SUR\n"
            "LA PISTE CYCLABLE"
        )

        self.vue.hide()
        self.zoom_widget.show()

    def retour_simulation(self):

        self.zoom_widget.hide()
        self.vue.show()
    def dessiner_routes(self):
        """
        Dessine les routes du réseau sur la scène graphique
        et affiche le coût associé à chaque segment.
        """
        for segment in segments:

            depart = segment["depart"]
            arrivee = segment["arrivee"]
            cout = segment["cout"]

            # Récupération des coordonnées des deux extrémités de la route
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

    def dessiner_panneaux(self):

        for segment in segments:
            depart = segment["depart"]
            arrivee = segment["arrivee"]

            x1, y1 = positions[depart]
            x2, y2 = positions[arrivee]

            # Positionner le panneau vers la fin de la route
            x = x1 + (x2 - x1) * 0.80
            y = y1 + (y2 - y1) * 0.80

            # Décaler le panneau pour ne pas toucher la route
            dx = x2 - x1
            dy = y2 - y1
            longueur = (dx ** 2 + dy ** 2) ** 0.5

            x += (dy / longueur) * 35
            y -= (dx / longueur) * 35

            # Créer un petit panneau noir cliquable
            fond = PanneauClickable(
                x - 15, y - 10, 30, 20,
                lambda s=segment: self.afficher_zoom(s)
            )

            fond.setPen(QPen(Qt.GlobalColor.black))
            fond.setBrush(QBrush(QColor("black")))

            self.scene.addItem(fond)

            segment["panneau_fond"] = fond
            segment["actif"] = False


    # ----------------------------------------------
    # DESSINER LES FEUX
    # ----------------------------------------------

    def dessiner_feux(self):
        """
        Dessine les feux de circulation sur les routes.
        Les intersections situées aux extrémités ne possèdent pas de feu.
        """

        # Intersections aux extrémités qui ne possèdent pas de feu
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
        """
        Dessine les intersections du réseau routier
        et affiche leur identifiant sur la scène graphique.
        """
        for nom in positions:

            x, y = positions[nom]

            # Représentation graphique de l'intersection
            self.scene.addEllipse(
                x - 12, y - 12, 24, 24,
                QPen(Qt.GlobalColor.black, 2),
                QBrush(QColor("#f5f5f5"))
            )

            # Affichage du nom de l'intersection
            texte = self.scene.addText(nom)

            texte.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            texte.setPos(x - 7, y - 39)


    # ----------------------------------------------
    # CREER LES VOITURES
    # ----------------------------------------------

    def creer_voitures(self):
        """
        Crée les voitures de la simulation avec leurs trajets
        prédéfinis et leurs couleurs respectives.
        """
        # Définition des parcours suivis par les voitures
        chemins = [
            ["A", "B", "C", "F", "E", "B", "D", "B", "A"],
            ["D", "B", "E", "G", "E", "F", "C", "B", "D"],
            ["J", "C", "B", "E", "H", "E", "F", "I", "F", "C", "J"]
        ]

        couleurs = ["#2878d0", "#e5a000", "#7b4ab5"]

        for i in range(len(chemins)):

            # Création graphique de la voiture
            voiture = QGraphicsRectItem(-8, -5, 16, 10)

            voiture.setPen(QPen(Qt.GlobalColor.black))
            voiture.setBrush(QBrush(QColor(couleurs[i])))

            self.scene.addItem(voiture)

            self.voitures.append(voiture)

            # Mémorisation du trajet et de la progression de la voiture
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
        """
        Crée les représentations graphiques des ambulances
        et initialise les informations nécessaires à leur déplacement.
        """
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

            # Ajouter une croix rouge pour identifier l'ambulance
            ambulance["croix"] = self.scene.addText("+")

            ambulance["croix"].setDefaultTextColor(
                QColor("#d71920")
            )

            ambulance["croix"].setFont(
                QFont("Arial", 16, QFont.Weight.Bold)
            )

            self.scene.addItem(ambulance["croix"])

            # Initialisation de l'étape et de la progression sur le trajet
            ambulance["etape"] = 0
            ambulance["progression"] = 0.0
            ambulance["terminee"] = len(ambulance["chemin"]) < 2

            # Mémoriser les routes déjà parcourues par l'ambulance
            ambulance["routes_parcourues"] = []

            if ambulance["terminee"]:
                self.finis.append(ambulance["id"])

            self.placer_ambulance(ambulance)


    # ----------------------------------------------
    # POSITIONNER UNE AMBULANCE
    # ----------------------------------------------

    def placer_ambulance(self, ambulance):
        """
        Place une ambulance sur son intersection de départ
        et positionne également sa croix rouge.
        """
        chemin = ambulance["chemin"]

        nom = chemin[ambulance["etape"]]

        x, y = positions[nom]

        ambulance["item"].setPos(x, y)

        ambulance["croix"].setPos(x - 7, y - 18)


    # ----------------------------------------------
    # METTRE A JOUR LES FEUX
    # ----------------------------------------------

    def mettre_a_jour_feux(self):
        """
        Actualise les feux en fonction des trajets des ambulances.
        Les routes prioritaires passent au vert et les routes concernées
        par les restrictions de circulation passent au rouge.
        """
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

            # Calculer l'indice des lampes dans la liste générale
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
        """
        Fait avancer une voiture sur son parcours prédéfini.
        La voiture attend lorsqu'elle rencontre un feu rouge au début d'une route.
        """
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

        # Calcul de la position intermédiaire entre les deux intersections
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        voiture.setPos(x, y)

        # Passer au prochain segment lorsque la voiture arrive à destination
        if donnees["progression"] >= 1:

            donnees["etape"] += 1
            donnees["progression"] = 0.0


    # ----------------------------------------------
    # FAIRE AVANCER UNE AMBULANCE
    # ----------------------------------------------

    def avancer_ambulance(self, ambulance):
        """
        Fait avancer une ambulance sur le chemin calculé par le serveur.
        Met également à jour sa position, les panneaux d'information
        et son état lorsqu'elle atteint sa destination.
        """
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

        # Récupérer le segment sur lequel se trouve l'ambulance
        segment = trouver_segment(depart, arrivee)

        # Activer le panneau lorsque l'ambulance approche
        if ambulance["progression"] >= 0.55:
            segment["actif"] = True

            segment["panneau_fond"].setBrush(
                QBrush(QColor("yellow"))
            )

        t = ambulance["progression"]

        x1, y1 = positions[depart]
        x2, y2 = positions[arrivee]

        # Calcul de la position de l'ambulance entre les deux intersections
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t

        ambulance["item"].setPos(x, y)
        ambulance["croix"].setPos(x - 7, y - 18)

        if ambulance["progression"] >= 1:

            # Désactiver le panneau après le passage
            segment["actif"] = False

            segment["panneau_fond"].setBrush(
                QBrush(QColor("black"))
            )

            # Mémoriser la route que l'ambulance  vient de parcourir
            segment = trouver_segment(depart, arrivee)

            ambulance["routes_parcourues"].append(segment)

            ambulance["etape"] += 1
            ambulance["progression"] = 0.0

            # Vérifier si l'ambulance a atteint sa destination
            if ambulance["etape"] >= len(chemin) - 1:

                ambulance["terminee"] = True

                if ambulance["id"] not in self.finis:
                    self.finis.append(ambulance["id"])


    # ----------------------------------------------
    # FONCTION PRINCIPALE DE LA SIMULATION
    # ----------------------------------------------

    def avancer(self):
        """
        Met à jour l'ensemble de la simulation à chaque déclenchement
        du timer : feux, voitures et ambulances.
        """

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

        # Vérifier si toutes les ambulances ont terminé leur trajet
        if len(self.finis) == len(self.ambulances):

            self.mettre_a_jour_feux()

            # Arrêter le timer et afficher le message de fin
            self.timer.stop()

            self.info.setText(
                "Toutes les ambulances sont arrivées."
            )


# ==================================================
# 8. FENETRE PRINCIPALE
# ==================================================

class FenetrePrincipale(QWidget):
    """
    Représente la fenêtre principale de l'application.
    Elle permet d'ajouter des ambulances, de calculer leurs trajets
    et de lancer ou réinitialiser la simulation.
    """
    def __init__(self):
        """
        Initialise l'interface graphique, les éléments de gestion
        des threads et les différentes commandes de l'application.
        """
        super().__init__()

        self.setWindowTitle("Gestion des véhicules d'urgence")
        self.resize(1400, 850)

        # Listes qui mémorisent les demandes, les threads et les résultats
        self.demandes = []
        self.threads = []
        self.calculs = []

        # Mutex utilisé pour protéger l'accès aux résultats partagés
        self.mutex = QMutex()

        #Dictionnaires contenant les résultats transmis par les threads
        self.resultats_partages = {}

        # Limite à deux le nombre de demandes traitées simultanément
        self.semaphore = QSemaphore(2)

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

        # Liste déroulante permettant de choisir le carrefour de départ
        self.depart = QComboBox()
        self.depart.addItems(routes.keys())

        gauche.addWidget(self.depart)

        gauche.addWidget(QLabel("Destination :"))

        # Liste déroulante permettant de choisir la destination
        self.destination = QComboBox()
        self.destination.addItems(routes.keys())

        gauche.addWidget(self.destination)

        # Boutons permettant de gérer les ambulances et la simulation
        self.ajouter = QPushButton("Ajouter une ambulance")
        self.lancer = QPushButton("Calculer et démarrer")
        self.reinitialiser = QPushButton("Nouvelle simulation")

        gauche.addWidget(self.ajouter)
        gauche.addWidget(self.lancer)
        gauche.addWidget(self.reinitialiser)

        gauche.addWidget(QLabel("Ambulances ajoutées :"))

        # Liste des ambulances ajoutées par l'utilisateur
        self.liste = QListWidget()
        gauche.addWidget(self.liste)

        gauche.addWidget(QLabel("Résultats de Dijkstra :"))

        # Liste affichant les chemins calculés et leurs coûts
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

        # Message affiché avant le lancement de la simulation
        self.placeholder = QLabel(
            "Ajoute une ambulance puis clique sur Calculer et démarrer."
        )

        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setFrameShape(QFrame.Shape.StyledPanel)

        droite.addWidget(self.placeholder)

        self.panneau_droit = panneau_droit

        # Ajout des deux panneaux à la fenêtre avec leurs proportions
        principal.addWidget(panneau_gauche, 1)
        principal.addWidget(panneau_droit, 3)

        # ==========================================
        # CONNEXION DES BOUTONS
        # ==========================================

        # Associer chaque bouton à la méthode correspondante
        self.ajouter.clicked.connect(self.ajouter_ambulance)
        self.lancer.clicked.connect(self.lancer_simulation)
        self.reinitialiser.clicked.connect(self.nouvelle_simulation)


    # ----------------------------------------------
    # AJOUTER UNE AMBULANCE
    # ----------------------------------------------

    def ajouter_ambulance(self):
        """
        Ajoute une nouvelle ambulance à la liste des demandes
        après avoir vérifié que le départ et la destination sont différents.
        """
        depart = self.depart.currentText()
        destination = self.destination.currentText()

        # Vérifier que le départ et la destination sont différents
        if depart == destination:

            QMessageBox.information(
                self,
                "Trajet",
                "Choisis deux carrefours différents."
            )

            return

        # Attribuer un identifiant unique à la nouvelle ambulance
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

        # Afficher les informations de l'ambulance dans la liste
        self.liste.addItem(
            f"Ambulance {identifiant} : {depart} -> {destination}"
        )


    # ----------------------------------------------
    # LANCER LES CALCULS
    # ----------------------------------------------

    def lancer_simulation(self):
        """
        Lance les calculs de trajets en créant un thread par ambulance.
        Les demandes sont envoyées au serveur sans bloquer l'interface graphique.
        """

        # Vérifier qu'au moins une ambulance a été ajoutée
        if len(self.demandes) == 0:

            QMessageBox.information(
                self,
                "Ambulances",
                "Ajoute au moins une ambulance."
            )

            return

        # Désactiver les boutons pendant le traitement des demandes
        self.lancer.setEnabled(False)
        self.ajouter.setEnabled(False)

        self.resultats.clear()

        # Réinitialiser les listes utilisées pour les nouveaux calculs
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
                self.resultats_partages,
                self.semaphore
            )

            # Connecter le signal du thread à la méthode de réception
            thread.resultat.connect(self.recevoir_resultat)

            self.threads.append(thread)

        # Démarrer tous les threads
        for thread in self.threads:

            thread.start()


    # ----------------------------------------------
    # RECEVOIR LES RESULTATS DES THREADS
    # ----------------------------------------------

    def recevoir_resultat(self, identifiant):
        """
        Récupère et affiche le résultat d'un calcul de trajet.
        Lorsque toutes les demandes sont traitées, prépare les ambulances
        dont le trajet est valide pour lancer la simulation.
        """

        # Accéder au dictionnaire partagé de manière sécurisée
        self.mutex.lock()

        try:
            resultat = self.resultats_partages[identifiant].copy()

        finally:
            self.mutex.unlock()

        # Récupérer les informations transmises par le thread
        chemin = resultat["chemin"]
        cout = resultat["cout"]
        erreur = resultat.get("erreur")

        resultat = {
            "id": identifiant,
            "chemin": chemin,
            "cout": cout
        }

        self.calculs.append(resultat)

        # Afficher une erreur si le calcul n'a pas abouti
        if erreur:

            self.resultats.addItem(
                f"Ambulance {identifiant} : erreur - {erreur}"
            )

        # Afficher le chemin et son coût lorsque le calcul a réussi
        elif len(chemin) > 0:

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

            # Réactiver les boutons une fois les calculs terminés
            self.lancer.setEnabled(True)
            self.ajouter.setEnabled(True)

            ambulances_valides = []

            # Conserver uniquement les ambulances ayant un chemin valide
            for resultat in self.calculs:

                if len(resultat["chemin"]) > 0:

                    for ambulance in self.demandes:

                        if ambulance.id == resultat["id"]:
                            donnees = {
                                "id": ambulance.id,
                                "chemin": resultat["chemin"]
                            }

                            ambulances_valides.append(donnees)

            # Lancer la simulation si au moins un trajet est valide
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
        """
        Affiche la simulation graphique des ambulances ayant obtenu
        un trajet valide, en remplaçant une éventuelle ancienne simulation.
        """
        # Supprimer l'ancienne simulation si nécessaire
        if self.simulation is not None:

            self.simulation.timer.stop()

            self.panneau_droit.layout().removeWidget(self.simulation)

            self.simulation.setParent(None)
            self.simulation.deleteLater()

        self.placeholder.hide()

        # Créer et afficher la nouvelle simulation
        self.simulation = Simulation(ambulances)

        self.panneau_droit.layout().addWidget(self.simulation)


    # ----------------------------------------------
    # RECOMMENCER UNE SIMULATION
    # ----------------------------------------------

    def nouvelle_simulation(self):
        """
        Réinitialise l'application pour permettre de préparer
        une nouvelle simulation avec de nouvelles demandes d'ambulances.
        """

        # Arrêter et supprimer la simulation actuelle si elle existe
        if self.simulation is not None:

            self.simulation.timer.stop()

            self.panneau_droit.layout().removeWidget(self.simulation)

            self.simulation.setParent(None)
            self.simulation.deleteLater()

            self.simulation = None

        # Vider les listes contenant les demandes et les résultats
        self.demandes.clear()
        self.calculs.clear()
        self.threads.clear()

        self.liste.clear()
        self.resultats.clear()

        # Réinitialiser l'identifiant des prochaines ambulances
        self.prochaine_id = 1

        # Réafficher le message initial et réactiver les boutons
        self.placeholder.show()

        self.lancer.setEnabled(True)
        self.ajouter.setEnabled(True)


# ==================================================
# 9. LANCEMENT DU PROGRAMME
# ==================================================

if __name__ == "__main__":

    # Création de l'application PyQt6
    app = QApplication(sys.argv)

    # Création de la fenêtre principale
    fenetre = FenetrePrincipale()

    # Affichage de la fenêtre
    fenetre.show()

    # Lancement de la boucle principale de l'interface graphique
    sys.exit(app.exec())
