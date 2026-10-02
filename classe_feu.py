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