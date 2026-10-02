class Route:
    def __init__(self, depart, arrivee, temps, distance):
        self.depart = depart
        self.arrivee = arrivee
        self.temps = temps
        self.distance = distance


    def __str__(self):
        return f"La route de {self.depart} à {self.arrivee} d'un distance de {self.distance}km et une durée de {self.temps} min "



