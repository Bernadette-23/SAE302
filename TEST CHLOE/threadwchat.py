
import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QComboBox, QVBoxLayout, QListWidget
)


# -------------------------
# ROUTES
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


# -------------------------
# DIJKSTRA
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
# THREAD
# -------------------------

class CalculThread(QThread):

    resultat_obtenu = pyqtSignal(str)

    def __init__(self, identifiant, depart, destination):
        super().__init__()

        self.identifiant = identifiant
        self.depart = depart
        self.destination = destination

    def run(self):
        chemin, cout = dijkstra(
            routes, self.depart, self.destination
        )

        if chemin:
            message = (
                f"Trajet {self.identifiant} : "
                f"{self.depart} -> {self.destination} | "
                f"Chemin : {' -> '.join(chemin)} | "
                f"Coût : {cout}"
            )
        else:
            message = (
                f"Trajet {self.identifiant} : "
                "aucun chemin trouvé"
            )

        self.resultat_obtenu.emit(message)


# -------------------------
# INTERFACE
# -------------------------

app = QApplication(sys.argv)

fenetre = QWidget()
fenetre.setWindowTitle("Gestion des ambulances")
fenetre.resize(600, 450)

titre = QLabel("Calcul de plusieurs trajets")

depart = QComboBox()
depart.addItems(routes.keys())

destination = QComboBox()
destination.addItems(routes.keys())

bouton_ajouter = QPushButton("Ajouter le trajet")
bouton_calculer = QPushButton("Lancer les calculs")

liste_trajets = QListWidget()
resultats = QListWidget()

# On mémorise les trajets à calculer
trajets = []

# On conserve les threads actifs
threads = []

# Identifiant du prochain trajet
numero = 1


# Ajouter un trajet à la liste
def ajouter_trajet():
    global numero

    d = depart.currentText()
    a = destination.currentText()

    if d == a:
        liste_trajets.addItem("Départ et destination identiques.")
        return

    trajets.append((numero, d, a))

    liste_trajets.addItem(
        f"Trajet {numero} : {d} -> {a}"
    )

    numero += 1


# Lancer tous les calculs
def lancer_calculs():

    if not trajets:
        resultats.addItem("Ajoute d'abord un trajet.")
        return

    bouton_calculer.setEnabled(False)

    resultats.clear()
    threads.clear()

    for identifiant, d, a in trajets:

        thread = CalculThread(identifiant, d, a)

        thread.resultat_obtenu.connect(resultats.addItem)

        threads.append(thread)

    # On démarre tous les threads
    for thread in threads:
        thread.start()

    # On réactive le bouton après la fin de tous les threads
    for thread in threads:
        thread.finished.connect(verifier_fin)


def verifier_fin():
    if all(not thread.isRunning() for thread in threads):
        bouton_calculer.setEnabled(True)


bouton_ajouter.clicked.connect(ajouter_trajet)
bouton_calculer.clicked.connect(lancer_calculs)


# Organisation de la fenêtre
layout = QVBoxLayout()

layout.addWidget(titre)

layout.addWidget(QLabel("Départ :"))
layout.addWidget(depart)

layout.addWidget(QLabel("Destination :"))
layout.addWidget(destination)

layout.addWidget(bouton_ajouter)

layout.addWidget(QLabel("Trajets à calculer :"))
layout.addWidget(liste_trajets)

layout.addWidget(bouton_calculer)

layout.addWidget(QLabel("Résultats :"))
layout.addWidget(resultats)

fenetre.setLayout(layout)
fenetre.show()

sys.exit(app.exec())