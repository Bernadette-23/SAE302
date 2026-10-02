import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout


# Notre réseau
routes = {
    "A": [("B", 5)],
    "B": [("A", 5), ("C", 4), ("E", 3)],
    "C": [("B", 4), ("F", 2)],
    "E": [("B", 3), ("F", 5), ("H", 6)],
    "F": [("E", 5), ("C", 2)],
    "H": [("E", 6)]
}


# Dijkstra
def dijkstra(depart, destination):

    distances = {}

    for noeud in routes:
        distances[noeud] = 9999

    distances[depart] = 0

    visites = []

    precedents = {}

    while len(visites) < len(routes):

        noeud = None

        for n in routes:
            if n not in visites:
                if noeud is None or distances[n] < distances[noeud]:
                    noeud = n

        visites.append(noeud)

        for voisin, cout in routes[noeud]:

            nouvelle_distance = distances[noeud] + cout

            if nouvelle_distance < distances[voisin]:
                distances[voisin] = nouvelle_distance
                precedents[voisin] = noeud

    # Construire le chemin
    chemin = []
    noeud = destination

    while noeud != depart:
        chemin.append(noeud)
        noeud = precedents[noeud]

    chemin.append(depart)
    chemin.reverse()

    return chemin, distances[destination]


# -------------------------
# INTERFACE
# -------------------------

app = QApplication(sys.argv)

fenetre = QWidget()
fenetre.setWindowTitle("Gestion ambulance")
fenetre.resize(400, 300)


titre = QLabel("Gestion de l'ambulance")

depart = QComboBox()
depart.addItems(routes.keys())

destination = QComboBox()
destination.addItems(routes.keys())

bouton = QPushButton("Calculer le trajet")

resultat = QLabel("Résultat :")


# Quand on clique sur le bouton
def calculer():

    d = depart.currentText()
    a = destination.currentText()

    chemin, cout = dijkstra(d, a)

    resultat.setText(
        "Trajet : " + " → ".join(chemin) +
        "\nCoût : " + str(cout)
    )


bouton.clicked.connect(calculer)


# Organisation
layout = QVBoxLayout()

layout.addWidget(titre)
layout.addWidget(QLabel("Départ"))
layout.addWidget(depart)
layout.addWidget(QLabel("Destination"))
layout.addWidget(destination)
layout.addWidget(bouton)
layout.addWidget(resultat)

fenetre.setLayout(layout)

fenetre.show()

sys.exit(app.exec())