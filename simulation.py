import sys
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QListWidget, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem,
    QGraphicsRectItem, QMessageBox, QSplitter, QFrame
)

# ============================================================
# ROUTES : coûts bidirectionnels
# ============================================================

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

# Positions du schéma. La vue peut défiler si nécessaire.
positions = {
    "I": (100, 70), "F": (100, 230), "C": (100, 430), "J": (100, 600),
    "H": (340, 70), "E": (340, 230), "B": (340, 430), "A": (340, 600),
    "G": (590, 230), "D": (590, 430)
}


# ============================================================
# FEUX ET CARREFOURS
# ============================================================

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
        recherche = frozenset(position.split("-"))
        for feu in self.feux:
            if frozenset(feu.position.split("-")) == recherche:
                return feu
        return None


segments = []
for a, voisins in routes.items():
    for b, cout in voisins:
        cle = frozenset((a, b))
        if not any(s["cle"] == cle for s in segments):
            segments.append({
                "cle": cle, "a": a, "b": b, "cout": cout,
                "feu": Feu(len(segments) + 1, f"{a}-{b}", "vert")
            })

feux = [s["feu"] for s in segments]
carrefours = [Carrefour(1, feux)]


def trouver_segment(a, b):
    cle = frozenset((a, b))
    for segment in segments:
        if segment["cle"] == cle:
            return segment
    return None


# ============================================================
# DIJKSTRA
# ============================================================

def dijkstra(graphe, depart, destination):
    distances = {noeud: float("inf") for noeud in graphe}
    precedents = {noeud: None for noeud in graphe}
    visites = []
    distances[depart] = 0

    while len(visites) < len(graphe):
        noeud = None
        for candidat in graphe:
            if candidat not in visites:
                if noeud is None or distances[candidat] < distances[noeud]:
                    noeud = candidat

        if noeud is None or distances[noeud] == float("inf"):
            break

        visites.append(noeud)
        for voisin, cout in graphe[noeud]:
            nouvelle_distance = distances[noeud] + cout
            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = noeud

    if distances[destination] == float("inf"):
        return [], float("inf")

    chemin = []
    noeud = destination
    while noeud is not None:
        chemin.append(noeud)
        noeud = precedents[noeud]
    chemin.reverse()
    return chemin, distances[destination]


# ============================================================
# THREAD DE CALCUL
# ============================================================

class CalculThread(QThread):
    resultat = pyqtSignal(int, str, str, object, object)

    def __init__(self, identifiant, depart, destination):
        super().__init__()
        self.identifiant = identifiant
        self.depart = depart
        self.destination = destination

    def run(self):
        chemin, cout = dijkstra(routes, self.depart, self.destination)
        self.resultat.emit(
            self.identifiant, self.depart, self.destination, chemin, cout
        )


# ============================================================
# SIMULATION (panneau de droite)
# ============================================================

class Simulation(QWidget):
    def __init__(self, ambulances):
        super().__init__()
        self.ambulances = ambulances
        self.voitures = []
        self.voitures_donnees = []
        self.lampes = {}
        self.finis = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        self.info = QLabel("Ambulances prioritaires | Les voitures s'arrêtent devant un feu rouge.")
        self.info.setWordWrap(True)
        layout.addWidget(self.info)

        self.scene = QGraphicsScene(0, 0, 700, 670)
        self.vue = QGraphicsView(self.scene)
        self.vue.setRenderHint(self.vue.renderHints())
        self.vue.setMinimumWidth(480)
        self.vue.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.vue.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        layout.addWidget(self.vue)

        self.dessiner_routes()
        self.dessiner_feux()
        self.dessiner_carrefours()
        self.creer_voitures()
        self.creer_ambulances()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.avancer)
        self.timer.start(35)

    def dessiner_routes(self):
        for segment in segments:
            a, b, cout = segment["a"], segment["b"], segment["cout"]
            x1, y1 = positions[a]
            x2, y2 = positions[b]

            route = QGraphicsLineItem(x1, y1, x2, y2)
            route.setPen(QPen(QColor("#454545"), 18, Qt.PenStyle.SolidLine,
                              Qt.PenCapStyle.RoundCap))
            self.scene.addItem(route)

            axe = QGraphicsLineItem(x1, y1, x2, y2)
            axe.setPen(QPen(QColor("white"), 2, Qt.PenStyle.DashLine))
            self.scene.addItem(axe)

            texte = self.scene.addText(str(cout))
            texte.setDefaultTextColor(QColor("#14813b"))
            texte.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            texte.setPos((x1 + x2) / 2 + 6, (y1 + y2) / 2 - 21)

    def dessiner_feux(self):
        # Pas de feu aux extrémités des carrefours I, H, G, D, A et J.
        # Cela laisse exactement 14 feux sur le graphe.
        self.lampes = {}
        extremites_sans_feu = {"I", "H", "G", "D", "A", "J"}

        for segment in segments:
            a, b = segment["a"], segment["b"]
            x1, y1 = positions[a]
            x2, y2 = positions[b]

            # Feu proche du début du segment
            if a not in extremites_sans_feu:
                x = x1 + (x2 - x1) * 0.18
                y = y1 + (y2 - y1) * 0.18
                item = QGraphicsEllipseItem(x - 7, y - 7, 14, 14)
                item.setPen(QPen(Qt.GlobalColor.black, 1))
                item.setBrush(QBrush(QColor("#20a34a")))
                self.scene.addItem(item)
                self.lampes[(segment["cle"], "debut")] = item

            # Feu proche de la fin du segment
            if b not in extremites_sans_feu:
                x = x1 + (x2 - x1) * 0.82
                y = y1 + (y2 - y1) * 0.82
                item = QGraphicsEllipseItem(x - 7, y - 7, 14, 14)
                item.setPen(QPen(Qt.GlobalColor.black, 1))
                item.setBrush(QBrush(QColor("#20a34a")))
                self.scene.addItem(item)
                self.lampes[(segment["cle"], "fin")] = item

    def dessiner_carrefours(self):
        for nom, (x, y) in positions.items():
            point = QGraphicsEllipseItem(x - 12, y - 12, 24, 24)
            point.setPen(QPen(Qt.GlobalColor.black, 2))
            point.setBrush(QBrush(QColor("#f5f5f5")))
            self.scene.addItem(point)

            texte = self.scene.addText(nom)
            texte.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            texte.setPos(x - 7, y - 39)

    def creer_voitures(self):
        chemins = [
            ["A", "B", "C", "F", "E", "B", "D", "B", "A"],
            ["D", "B", "E", "G", "E", "F", "C", "B", "D"],
            ["J", "C", "B", "E", "H", "E", "F", "I", "F", "C", "J"]
        ]
        couleurs = ["#2878d0", "#e5a000", "#7b4ab5"]
        for i, chemin in enumerate(chemins):
            item = QGraphicsRectItem(-8, -5, 16, 10)
            item.setPen(QPen(Qt.GlobalColor.black, 1))
            item.setBrush(QBrush(QColor(couleurs[i])))
            self.scene.addItem(item)
            self.voitures.append(item)
            self.voitures_donnees.append({
                "chemin": chemin,
                "etape": 0,
                "progression": i * 0.25,
                "attente": 0
            })

    def creer_ambulances(self):
        couleurs = ["#ffffff", "#f4f4f4", "#e8f0ff", "#fff0f0"]
        for i, amb in enumerate(self.ambulances):
            item = QGraphicsRectItem(-12, -8, 24, 16)
            item.setPen(QPen(QColor("#b71c1c"), 2))
            item.setBrush(QBrush(QColor(couleurs[i % len(couleurs)])))
            self.scene.addItem(item)

            croix = self.scene.addText("+")
            croix.setDefaultTextColor(QColor("#d71920"))
            croix.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            self.scene.addItem(croix)

            amb["item"] = item
            amb["croix"] = croix
            amb["etape"] = 0
            amb["progression"] = 0.0
            amb["terminee"] = len(amb["chemin"]) < 2
            if amb["terminee"]:
                self.finis.add(amb["id"])
            self.placer_amb(amb)

    def placer_amb(self, amb):
        nom = amb["chemin"][min(amb["etape"], len(amb["chemin"]) - 1)]
        x, y = positions[nom]
        amb["item"].setPos(x, y)
        amb["croix"].setPos(x - 7, y - 18)

    def mettre_a_jour_feux(self):
        # Tous les feux sont verts par défaut. Les feux des routes
        # conflictuelles au prochain carrefour passent au rouge.
        rouges, verts = set(), set()

        for amb in self.ambulances:
            if amb["terminee"]:
                continue
            chemin, etape = amb["chemin"], amb["etape"]
            if etape >= len(chemin) - 1:
                continue

            depart, arrivee = chemin[etape], chemin[etape + 1]
            verts.add(frozenset((depart, arrivee)))

            for voisin, _ in routes[arrivee]:
                cle = frozenset((arrivee, voisin))
                if cle != frozenset((depart, arrivee)):
                    rouges.add(cle)

        rouges -= verts

        for segment in segments:
            if segment["cle"] in rouges:
                segment["feu"].passer_au_rouge()
                couleur = QColor("#e53935")
            else:
                segment["feu"].passer_au_vert()
                couleur = QColor("#20a34a")

            for sens in ("debut", "fin"):
                lampe = self.lampes.get((segment["cle"], sens))
                if lampe is not None:
                    lampe.setBrush(QBrush(couleur))

    def avancer_voiture(self, item, voiture):
        chemin = voiture["chemin"]
        if len(chemin) < 2:
            return

        if voiture["etape"] >= len(chemin) - 1:
            voiture["etape"] = 0
            voiture["progression"] = 0.0

        depart = chemin[voiture["etape"]]
        arrivee = chemin[voiture["etape"] + 1]
        segment = trouver_segment(depart, arrivee)

        # Une voiture qui attend au début d'un segment rouge ne bouge pas.
        if voiture["progression"] == 0 and segment["feu"].couleur == "rouge":
            return

        voiture["progression"] += 0.012
        t = voiture["progression"]
        x1, y1 = positions[depart]
        x2, y2 = positions[arrivee]
        item.setPos(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t)

        if voiture["progression"] >= 1:
            voiture["etape"] += 1
            voiture["progression"] = 0.0

    def avancer_amb(self, amb):
        if amb["terminee"]:
            return

        chemin = amb["chemin"]
        if amb["etape"] >= len(chemin) - 1:
            amb["terminee"] = True
            self.finis.add(amb["id"])
            return

        depart, arrivee = chemin[amb["etape"]], chemin[amb["etape"] + 1]
        amb["progression"] += 0.005
        t = amb["progression"]
        x1, y1 = positions[depart]
        x2, y2 = positions[arrivee]
        x = x1 + (x2 - x1) * t
        y = y1 + (y2 - y1) * t
        amb["item"].setPos(x, y)
        amb["croix"].setPos(x - 7, y - 18)

        if amb["progression"] >= 1:
            amb["etape"] += 1
            amb["progression"] = 0.0

    def avancer(self):
        self.mettre_a_jour_feux()

        for voiture, donnees in zip(self.voitures, self.voitures_donnees):
            self.avancer_voiture(voiture, donnees)

        for amb in self.ambulances:
            self.avancer_amb(amb)

        if len(self.finis) == len(self.ambulances):
            self.mettre_a_jour_feux()
            self.timer.stop()
            self.info.setText("Toutes les ambulances sont arrivées.")


# ============================================================
# FENETRE PRINCIPALE : choix à gauche, simulation à droite
# ============================================================

class FenetrePrincipale(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestion des véhicules d'urgence")
        self.resize(1400, 850)

        principal = QHBoxLayout(self)

        # Panneau gauche : contrôles et résultats
        panneau_gauche = QWidget()
        panneau_gauche.setMinimumWidth(300)
        panneau_gauche.setMaximumWidth(380)
        gauche = QVBoxLayout(panneau_gauche)

        titre = QLabel("Gestion des ambulances")
        titre.setStyleSheet("font-size: 18px; font-weight: bold;")
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
        gauche.addWidget(self.liste, 1)

        gauche.addWidget(QLabel("Résultats de Dijkstra :"))
        self.resultats = QListWidget()
        gauche.addWidget(self.resultats, 2)

        # Panneau droit : simulation intégrée dans la même fenêtre.
        panneau_droit = QWidget()
        droite = QVBoxLayout(panneau_droit)
        droite.setContentsMargins(0, 0, 0, 0)
        label_simulation = QLabel("Simulation du carrefour")
        label_simulation.setStyleSheet("font-size: 18px; font-weight: bold;")
        droite.addWidget(label_simulation)

        self.simulation = None
        self.placeholder = QLabel("Ajoute une ambulance puis clique sur « Calculer et démarrer ».")
        self.placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder.setFrameShape(QFrame.Shape.StyledPanel)
        droite.addWidget(self.placeholder)

        self.panneau_droit = panneau_droit
        principal.addWidget(panneau_gauche, 0)
        principal.addWidget(panneau_droit, 1)

        self.demandes = []
        self.threads = []
        self.calculs = {}
        self.prochaine_id = 1

        self.ajouter.clicked.connect(self.ajouter_ambulance)
        self.lancer.clicked.connect(self.lancer_simulation)
        self.reinitialiser.clicked.connect(self.nouvelle_simulation)

    def ajouter_ambulance(self):
        depart = self.depart.currentText()
        destination = self.destination.currentText()

        if depart == destination:
            QMessageBox.information(self, "Trajet", "Choisis deux carrefours différents.")
            return

        identifiant = self.prochaine_id
        self.prochaine_id += 1
        self.demandes.append((identifiant, depart, destination))
        self.liste.addItem(f"Ambulance {identifiant} : {depart} → {destination}")

    def lancer_simulation(self):
        if not self.demandes:
            QMessageBox.information(self, "Ambulances", "Ajoute au moins une ambulance.")
            return

        self.lancer.setEnabled(False)
        self.ajouter.setEnabled(False)
        self.resultats.clear()
        self.calculs = {}
        self.threads = []

        for identifiant, depart, destination in self.demandes:
            thread = CalculThread(identifiant, depart, destination)
            thread.resultat.connect(self.recevoir_resultat)
            self.threads.append(thread)

        for thread in self.threads:
            thread.start()

    def recevoir_resultat(self, identifiant, depart, destination, chemin, cout):
        self.calculs[identifiant] = {
            "id": identifiant, "depart": depart, "destination": destination,
            "chemin": chemin, "cout": cout
        }

        if chemin:
            self.resultats.addItem(
                f"Ambulance {identifiant} : {' → '.join(chemin)} | coût : {cout}"
            )
        else:
            self.resultats.addItem(f"Ambulance {identifiant} : aucun chemin.")

        if len(self.calculs) == len(self.demandes):
            for thread in self.threads:
                thread.wait()

            self.lancer.setEnabled(True)
            self.ajouter.setEnabled(True)

            valides = [r for r in self.calculs.values() if r["chemin"]]
            if valides:
                self.afficher_simulation(valides)
            else:
                QMessageBox.warning(self, "Trajets", "Aucun trajet valide.")

    def afficher_simulation(self, ambulances):
        if self.simulation is not None:
            self.simulation.timer.stop()
            self.panneau_droit.layout().removeWidget(self.simulation)
            self.simulation.setParent(None)
            self.simulation.deleteLater()

        self.placeholder.hide()
        self.simulation = Simulation(ambulances)
        self.panneau_droit.layout().addWidget(self.simulation)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = FenetrePrincipale()
    fenetre.show()
    sys.exit(app.exec())
