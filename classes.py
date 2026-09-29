class Vehicules:
    def __init__(self,identifiant:int,position,destination,vitesse:int):
        self.__identifiant = identifiant
        self.__position = position
        self.__destination = destination
        self.__vitesse = vitesse

    def __str__(self):
        return f"Vehicule {self.__identifiant} : position {self.__position}, destination {self.__destination}, vitesse {self.__vitesse} km/h"
ambulance=Vehicules(
     1,
    (4,2),
    (4,9),
    55
)

print(ambulance)
print(Vehicules())
