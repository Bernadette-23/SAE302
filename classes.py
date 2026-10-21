import sys
import socket

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtCore import QThread, pyqtSignal

#import sys
#from PyQt6.QtWidgets import QApplication, QWidget
'''from PySide6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QComboBox, QVBoxLayout'''
"""
app=QApplication(sys.argv)
root=QWidget()
root.resize(400, 300)
root.setWindowTitle("Test Ambulance")
root.show()

if __name__=='__main__':
    sys.exit(app.exec())
"""
class Vehicules:
    def __init__(self,identifiant:int,position,destination,vitesse:int):
        self.__identifiant = identifiant
        self.__position = position
        self.__destination = destination
        self.__vitesse = vitesse

    def get_position(self):
        return self.__position

    def get_destination(self):
        return self.__destination

    def __str__(self):
        return f"Vehicule {self.__identifiant} : position {self.__position}, destination {self.__destination}, vitesse {self.__vitesse} km/h "

ambulance=Vehicules(
     1,
    (4,2),
    (4,9),
    55
)
#print(ambulance)

class Feu:
    def __init__(self, id : int, position : str, couleur : str):
        self.__id = id
        self.__position = position
        self.__couleur = couleur

    def get_position(self):
        return self.__position

    def passer_au_vert(self):
        self.__couleur = "vert"

    def passer_au_rouge(self):
        self.__couleur = "rouge"

    def __str__(self):
        return f"Le feu n°{self.__id} est actuellement de couleur {self.__couleur}"


class Carrefour:
    def __init__(self, id, feux):
        self.__id = id
        self.__feux = feux

    def __str__(self):
        return f"Carrefour {self.__id} avec {len(self.__feux)} feux"

    def rechercher_feu(self, position):
        for feu in self.__feux:
            if feu.get_position() == position:
                return feu

        return None

# Création des feux, en dehors de la classe
feu2 = Feu(2, "A-B", "rouge")
feu4 = Feu(4, "B-E", "rouge")
feu6 = Feu(6, "H-E", "rouge")
feu8 = Feu(8, "E-B", "rouge")

feu1 = Feu(1, "C-B", "rouge")
feu3 = Feu(3, "D-B", "rouge")
feu5 = Feu(5, "F-E", "rouge")
feu7 = Feu(7, "G-E", "rouge")

carrefourE = Carrefour(1, [feu4, feu6, feu5, feu7])
carrefourB = Carrefour(2, [feu1, feu2, feu3, feu8])



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

    # éviter que le programme plante si quelqu'un demande un trajet vers un point qui n'existe pas.
    if depart not in routes or destination not in routes:
        return [], float("inf")

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

def calculer_trajet_vehicule(vehicule, depart, destination, routes):
    chemin, cout = dijkstra(routes, depart, destination)

    print("Véhicule :", vehicule)
    print("Trajet :", " -> ".join(chemin))
    print("Coût total :", cout)

    return chemin, cout



#chemin, cout = dijkstra(routes, "A", "H")


def rechercher_feux_du_trajet(chemin, carrefours):
    feux_trouves = []

    for i in range(len(chemin) - 1):
        depart = chemin[i]
        arrivee = chemin[i + 1]

        position = depart + "-" + arrivee

        for carrefour in carrefours:
            feu = carrefour.rechercher_feu(position)

            if feu is not None and feu not in feux_trouves:
                feux_trouves.append(feu)

    return feux_trouves

"""
#avant 
def traiter_urgence(depart, destination, routes, carrefours):
    # 1. Calculer le trajet
    chemin, cout = dijkstra(routes, depart, destination)

    # 2. Chercher les feux sur ce trajet
    feux = rechercher_feux_du_trajet(chemin, carrefours)

    # 3. Afficher les résultats
    print("Trajet :", " -> ".join(chemin))
    print("Coût total :", cout)

    print("Feux trouvés :")
    for feu in feux:
        print(feu)

    for feu in feux:
        feu.passer_au_vert()
        print(feu)

    return chemin, cout, feux
"""
def traiter_urgence(vehicule, depart, destination, routes, carrefours):

    chemin, cout = calculer_trajet_vehicule(
        vehicule, depart, destination, routes
    )

    if not chemin or cout == float("inf"):
        print("Aucun trajet possible.")
        return [], cout, []

    feux = rechercher_feux_du_trajet(chemin, carrefours)

    print("Feux trouvés sur le trajet :")
    for feu in feux:
        print(feu)

    # 3. Passer les feux trouvés au vert
    print("\nActivation des feux :")

    for feu in feux:
        feu.passer_au_vert()
        print(feu)

    # 4. Afficher le trajet
    print("\nTrajet :", " -> ".join(chemin))
    print("Coût total :", cout)

    # 5. Retourner les résultats
    return chemin, cout, feux

def terminer_urgence(feux):
    print("\nFin de la demande d'urgence :")

    for feu in feux:
        feu.passer_au_rouge()
        print(feu)


carrefours = [carrefourE, carrefourB]

chemin, cout, feux = traiter_urgence(
    ambulance, "A", "H", routes, carrefours
)

terminer_urgence(feux)


#print("Chemin :", " -> ".join(chemin))
#print("Coût total :", cout)


'''
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

sys.exit(app.exec())'''