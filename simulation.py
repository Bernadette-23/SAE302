
import sys
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout,
    QGraphicsScene, QGraphicsView
)
from PyQt6.QtGui import QPen, QBrush, QColor


# -------------------------
# 1. CLASSES FEU ET CARREFOUR
# -------------------------

class Feu:
    def __init__(self, id, position, couleur):
        self.id = id
        self.position = position
        self.couleur = couleur

    def get_position(self):
        return self.position

    def passer_au_vert(self):
        self.couleur = "vert"

    def passer_au_rouge(self):
        self.couleur = "rouge"


class Carrefour:
    def __init__(self, id, feux):
        self.id = id
        self.feux = feux

    def rechercher_feu(self, position):
        for feu in self.feux:
            if feu.get_position() == position:
                return feu
        return None


# -------------------------
# 2. CREATION DES FEUX
# -------------------------

feu1 = Feu(1, "C-B", "rouge")
feu2 = Feu(2, "A-B", "rouge")
feu3 = Feu(3, "D-B", "rouge")
feu8 = Feu(8, "E-B", "rouge")

feu4 = Feu(4, "B-E", "rouge")
feu5 = Feu(5, "F-E", "rouge")
feu6 = Feu(6, "H-E", "rouge")
feu7 = Feu(7, "G-E", "rouge")

carrefourB = Carrefour(2, [feu1, feu2, feu3, feu8])
carrefourE = Carrefour(1, [feu4, feu5, feu6, feu7])

carrefours = {
    "B": carrefourB,
    "E": carrefourE
}

tous_les_feux = [
    feu1, feu2, feu3, feu4,
    feu5, feu6, feu7, feu8
]


# -------------------------
# 3. ROUTES
# -------------------------

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
    "A": (60, 180),
    "B": (170, 180),
    "C": (300, 180),
    "D": (170, 70),
    "E": (260, 300),
    "F": (400, 300),
    "G": (200, 390),
    "H": (310, 390),
    "I": (510, 300),
    "J": (440, 180)
}


# -------------------------
# 4. DIJKSTRA
# -------------------------

def dijkstra(routes, depart, destination):

    distances = {}
    precedents = {}
    visites = []

    for noeud in routes:
        distances[noeud] = float("inf")
        precedents[noeud] = None

    distances[depart] = 0

    while len(visites) < len(routes):

        noeud = None

        for n in routes:
            if n not in visites:
                if noeud is None or distances[n] < distances[noeud]:
                    noeud = n

        if noeud is None or distances[noeud] == float("inf"):
            break

        visites.append(noeud)

        for voisin, cout in routes[noeud]:
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


# -------------------------
# 5. INTERFACE
# -------------------------

app = QApplication(sys.argv)

fenetre = QWidget()
fenetre.setWindowTitle("Simulation des ambulances")
fenetre.resize(800, 700)

titre = QLabel("Simulation des véhicules d'urgence")

depart = QComboBox()
depart.addItems(routes.keys())

destination = QComboBox()
destination.addItems(routes.keys())

bouton = QPushButton("Lancer l'ambulance")
resultat = QLabel("Choisis un départ et une destination.")

scene = QGraphicsScene()
scene.setSceneRect(0, 0, 600, 450)
scene.setBackgroundBrush(QColor("#eeeeee"))

vue = QGraphicsView(scene)


# -------------------------
# 6. DESSIN DES ROUTES
# -------------------------

dessinees = []

for noeud in routes:
    for voisin, cout in routes[noeud]:

        route = tuple(sorted((noeud, voisin)))

        if route not in dessinees:
            dessinees.append(route)

            x1, y1 = positions[noeud]
            x2, y2 = positions[voisin]

            scene.addLine(
                x1, y1, x2, y2,
                QPen(QColor("#777777"), 6)
            )

            texte = scene.addText(str(cout))
            texte.setPos((x1 + x2) / 2, (y1 + y2) / 2)


# -------------------------
# 7. DESSIN DES VOITURES
# -------------------------

voitures = [
    ("A", "B", 0.30),
    ("B", "C", 0.65),
    ("E", "F", 0.35)
]

for d, a, proportion in voitures:

    x1, y1 = positions[d]
    x2, y2 = positions[a]

    x = x1 + (x2 - x1) * proportion
    y = y1 + (y2 - y1) * proportion

    scene.addRect(
        x - 10, y - 6, 20, 12,
        QPen(QColor("#174ea6")),
        QBrush(QColor("#4285f4"))
    )


# -------------------------
# 8. DESSIN DES CARREFOURS
# -------------------------

for noeud, (x, y) in positions.items():

    scene.addEllipse(
        x - 14, y - 14, 28, 28,
        QPen(QColor("black")),
        QBrush(QColor("white"))
    )

    texte = scene.addText(noeud)
    texte.setPos(x - 5, y - 11)


# -------------------------
# 9. DESSIN DES FEUX
# -------------------------

positions_feux = {
    1: (190, 145),
    2: (140, 145),
    3: (140, 205),
    8: (190, 205),

    4: (230, 265),
    5: (290, 265),
    6: (290, 335),
    7: (230, 335)
}

dessin_feux = {}

for feu in tous_les_feux:

    x, y = positions_feux[feu.id]

    cercle = scene.addEllipse(
        x, y, 14, 14,
        QPen(QColor("black")),
        QBrush(QColor("red"))
    )

    texte = scene.addText(feu.position)
    texte.setPos(x - 10, y - 20)

    dessin_feux[feu.id] = cercle


# -------------------------
# 10. GESTION DES FEUX
# -------------------------

def actualiser_feux():
    for feu in tous_les_feux:

        if feu.couleur == "vert":
            couleur = QColor("green")
        else:
            couleur = QColor("red")

        dessin_feux[feu.id].setBrush(QBrush(couleur))


def activer_feu(carrefour, prochain):

    # Tous les feux repassent au rouge
    for feu in tous_les_feux:
        feu.passer_au_rouge()

    # Chercher le feu correspondant à la route
    if carrefour in carrefours:

        position_feu = prochain + "-" + carrefour

        feu = carrefours[carrefour].rechercher_feu(position_feu)

        if feu is not None:
            feu.passer_au_vert()

    actualiser_feux()


# -------------------------
# 11. AMBULANCE
# -------------------------

ambulance = scene.addEllipse(
    -10, -10, 20, 20,
    QPen(QColor("darkred")),
    QBrush(QColor("red"))
)

lettre = scene.addText("A")
lettre.setDefaultTextColor(QColor("white"))

ambulance.setPos(*positions["A"])
lettre.setPos(positions["A"][0] - 5, positions["A"][1] - 11)

chemin_actuel = []
index_chemin = 1

timer = QTimer()


# -------------------------
# 12. LANCER LA SIMULATION
# -------------------------

def lancer_simulation():

    global chemin_actuel, index_chemin

    timer.stop()

    for feu in tous_les_feux:
        feu.passer_au_rouge()

    actualiser_feux()

    d = depart.currentText()
    a = destination.currentText()

    chemin, cout = dijkstra(routes, d, a)

    if not chemin:
        resultat.setText("Aucun chemin trouvé.")
        return

    chemin_actuel = chemin
    index_chemin = 1

    x, y = positions[d]
    ambulance.setPos(x, y)
    lettre.setPos(x - 5, y - 11)

    resultat.setText(
        "Chemin : " + " -> ".join(chemin)
        + " | Coût : " + str(cout)
    )

    if len(chemin) == 1:
        resultat.setText("L'ambulance est déjà arrivée.")
        return

    # Activer le feu sur la première route
    activer_feu(chemin[0], chemin[1])

    timer.start(30)


# -------------------------
# 13. DEPLACER L'AMBULANCE
# -------------------------

def deplacer_ambulance():

    global index_chemin

    if index_chemin >= len(chemin_actuel):
        timer.stop()

        for feu in tous_les_feux:
            feu.passer_au_rouge()

        actualiser_feux()
        resultat.setText(resultat.text() + " | Ambulance arrivée !")
        return

    x = ambulance.x()
    y = ambulance.y()

    prochain = chemin_actuel[index_chemin]
    cible_x, cible_y = positions[prochain]

    dx = cible_x - x
    dy = cible_y - y

    distance = (dx ** 2 + dy ** 2) ** 0.5

    if distance <= 3:

        ambulance.setPos(cible_x, cible_y)
        lettre.setPos(cible_x - 5, cible_y - 11)

        index_chemin += 1

        # Le feu change au carrefour atteint,
        # pour préparer la prochaine route
        if index_chemin < len(chemin_actuel):
            activer_feu(
                chemin_actuel[index_chemin - 1],
                chemin_actuel[index_chemin]
            )

    else:

        x += dx / distance * 3
        y += dy / distance * 3

        ambulance.setPos(x, y)
        lettre.setPos(x - 5, y - 11)


timer.timeout.connect(deplacer_ambulance)
bouton.clicked.connect(lancer_simulation)


# -------------------------
# 14. ORGANISATION
# -------------------------

choix = QHBoxLayout()
choix.addWidget(QLabel("Départ :"))
choix.addWidget(depart)
choix.addWidget(QLabel("Destination :"))
choix.addWidget(destination)
choix.addWidget(bouton)

layout = QVBoxLayout()
layout.addWidget(titre)
layout.addLayout(choix)
layout.addWidget(vue)
layout.addWidget(resultat)

fenetre.setLayout(layout)
fenetre.show()

sys.exit(app.exec())