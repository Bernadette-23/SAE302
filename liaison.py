""" ICI il y a les routes , le dijsktra et la fonction 'calculer_trajet_vehicule'
Sans oublier la classe Vehicules avec l'objet ambulance """

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
feu10 = Feu(10, "J-C", "rouge")
feu12 = Feu(12, "C-F", "rouge")
feu14 = Feu(14, "I-F", "rouge")
feu16 = Feu(16, "F-C", "rouge")

feu1 = Feu(1, "C-B", "rouge")
feu3 = Feu(3, "D-B", "rouge")
feu5 = Feu(5, "F-E", "rouge")
feu7 = Feu(7, "G-E", "rouge")
feu9 = Feu(9, "B-C", "rouge")
feu11 = Feu(11, "E-F", "rouge")

carrefourE = Carrefour(1, [feu4, feu6, feu5, feu7])
carrefourB = Carrefour(2, [feu1, feu2, feu3, feu8])
carrefourC = Carrefour(3, [feu10, feu16, feu9])
carrefourF = Carrefour(4, [feu12, feu14, feu11])

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


carrefours = [carrefourE, carrefourB, carrefourC, carrefourF]

chemin, cout, feux = traiter_urgence(
    ambulance, "A", "H", routes, carrefours
)

terminer_urgence(feux)
