class Feu:
    def __init__(self, id, position, couleur):
        self.id = id
        self.position = position
        self.couleur = couleur

    def passer_au_vert(self):
        self.couleur = "vert"

    def passer_au_rouge(self):
        self.couleur = "rouge"

    def __str__(self):
        return f"Le feu n°{self.id} est actuellement de couleur {self.couleur}"


"""
classe Carrefour qui gere les feux mais pas encore sure :*

* fait passer les feux des routes perpendiculaire au rouge

class Carrefour:
    def __init__(self, feux):
        self.feux = feux

    def priorite_urgence(self, feu_prioritaire):
        for feu in self.feux:
            feu.passer_au_rouge()

        feu_prioritaire.passer_au_vert()
"""
