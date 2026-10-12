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


if __name__ == '__main__':
    feu2 = Feu(2, "A-B", "rouge")
    feu4 = Feu(4, "B-E", "rouge")
    feu6 = Feu(6, "H-E", "rouge")
    feu8 = Feu(8, "E-B", "rouge")

    feu1 = Feu(1, "C-B", "rouge")
    feu3 = Feu(3, "D-B", "rouge")
    feu5 = Feu(5, "F-E", "rouge")
    feu7 = Feu(7, "G-E", "rouge")

    carrefourE = Carrefour(
        1,
        [feu4, feu6, feu5, feu7]
    )

    carrefourB = Carrefour(
        2,
        [feu1, feu2, feu3, feu8]
    )

    print(carrefourE)
    print(carrefourB)

    # Test de recherche du feu
    feu_trouve = carrefourB.rechercher_feu("A-B")

    if feu_trouve is not None:
        print(feu_trouve)
    else:
        print("Aucun feu trouvé")
