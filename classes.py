import sys
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout


class Vehicules:
    def __init__(self,identifiant:int,position,destination,vitesse:int):
        self.__identifiant = identifiant
        self.__position = position
        self.__destination = destination
        self.__vitesse = vitesse

    def __str__(self):
        return f"Vehicule {self.__identifiant} : position {self.__position}, destination {self.__destination}, vitesse {self.__vitesse} km/h "
ambulance=Vehicules(
     1,
    (4,2),
    (4,9),
    55
)

print(ambulance)


routes = {
    "A": [("B", 5)],
    "B": [("A", 5), ("C", 4), ("D", 6), ("E", 3)],
    "C": [("B", 4),("F",2),("J",5)],
    "D": [("B", 6)],
    "E": [("B", 3), ("F", 5), ("G", 2), ("H", 6)],
    "F": [("E", 5),("I",5),("C",2)],
    "G": [("E", 2)],
    "H": [("E", 6)],
    "I": [("F", 5)],
    "J": [("C", 5)]

}

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

#Pour chercher un chemin en particulier
chemin, cout = dijkstra(routes, "A", "H")

print("Chemin :", " -> ".join(chemin))
print("Coût total :", cout)

# -------------------------
# INTERFACE
# -------------------------

app = QApplication(sys.argv)

fenetre = QWidget()
fenetre.setWindowTitle("Gestion ambulance")
fenetre.resize(400, 300)


# Titre
titre = QLabel("Gestion de l'ambulance")


# Choix du départ
label_depart = QLabel("Carrefour de départ :")

depart = QComboBox()
depart.addItems(routes.keys())


# Choix de la destination
label_destination = QLabel("Carrefour de destination :")

destination = QComboBox()
destination.addItems(routes.keys())


# Bouton
bouton = QPushButton("Calculer le trajet")


# Résultat
resultat = QLabel("Résultat :")


# Fonction appelée quand on clique sur le bouton
def calculer():

    d = depart.currentText()
    a = destination.currentText()

    chemin, cout = dijkstra(routes, d, a)

    resultat.setText(
        "Trajet : " + " → ".join(chemin) +
        "\nCoût total : " + str(cout)
    )


# Relier le bouton à la fonction
bouton.clicked.connect(calculer)


# Organisation de la fenêtre
layout = QVBoxLayout()

layout.addWidget(titre)

layout.addWidget(label_depart)
layout.addWidget(depart)

layout.addWidget(label_destination)
layout.addWidget(destination)

layout.addWidget(bouton)

layout.addWidget(resultat)

fenetre.setLayout(layout)


# Afficher la fenêtre
fenetre.show()

sys.exit(app.exec())