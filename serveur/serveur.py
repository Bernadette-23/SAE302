import socket
import json

from T_gestion_urgence import (
    routes,
    carrefourE,
    carrefourB,
    ambulance,
    traiter_urgence
)

from commun.base_donnees import enregistrer_evenement

carrefours = [carrefourE, carrefourB]

def lancer_serveur():
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serveur.bind(("127.0.0.1", 5000))
    serveur.listen(5)

    print("Serveur en attente de demandes...")

    try:
        while True:
            connexion, adresse = serveur.accept()
            print("Client connecté :", adresse)

            with connexion:
                fichier = connexion.makefile("r", encoding="utf-8")

                for ligne in fichier:
                    try:
                        demande = json.loads(ligne)

                        depart = demande["depart"]
                        destination = demande["destination"]

                        chemin, cout, feux = traiter_urgence(
                            ambulance,
                            depart,
                            destination,
                            routes,
                            carrefours
                        )

                        if chemin and cout != float("inf"):
                            enregistrer_evenement(
                                type_evenement="urgence",
                                depart=depart,
                                destination=destination,
                                chemin=" -> ".join(chemin),
                                cout=cout,
                                details="Demande de priorité d'un véhicule d'urgence"
                            )

                        reponse = {
                            "chemin": chemin,
                            "cout": cout if cout != float("inf") else None,
                            "nombre_de_feux": len(feux)
                        }

                    except (ValueError, KeyError, TypeError):
                        reponse = {
                            "erreur": "Demande invalide"
                        }

                    connexion.sendall(
                        (json.dumps(reponse) + "\n").encode("utf-8")
                    )

    except KeyboardInterrupt:
        print("Arrêt du serveur.")

    finally:
        serveur.close()


if __name__ == "__main__":
    lancer_serveur()

""""
#création d'une premiere socket à voir et à affiner en consequence

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind(('127.0.0.1', 5000))
serveur.listen()
print("Serveur en attente d'une connexion...")

client, adresse = serveur.accept()
print("Client connecté !")
message = client.recv(1024).decode()

donnees = message.split(";")

type_message = donnees[0]
id_vehicule = donnees[1]
depart = donnees[2]
destination = donnees[3]

print("Type :", type_message)
print("Véhicule :", id_vehicule)
print("Départ :", depart)
print("Destination :", destination)

print(message)
client.send("Message reçu par le serveur ".encode())

serveur.close()
"""