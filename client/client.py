
"""
Module client permettant de communiquer avec le serveur
à l'aide de sockets TCP et d'échanger des données au format JSON.
"""

import socket
import json


def envoyer_demande(depart, destination):
    """
       Envoie au serveur une demande de calcul de trajet entre un départ
       et une destination, puis récupère et retourne sa réponse au format
       dictionnaire Python.
       """

    # Création d'une socket TCP pour communiquer avec le serveur.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:

        # Définition d'un délai maximal de 10 secondes.
        client.settimeout(10)

        # Connexion au serveur sur l'adresse locale et le port 5000.
        client.connect(("127.0.0.1", 5000))

        # Préparation de la demande contenant le départ et la destination.
        demande = {
            "depart": depart,
            "destination": destination
        }

        # Conversion de la demande en JSON et ajout d'un retour à la ligne
        # pour délimiter le message envoyé au serveur.
        message = json.dumps(demande) + "\n"

        # Encodage en UTF-8 et envoi des données au serveur.
        client.sendall(message.encode("utf-8"))

        # Création d'un fichier de lecture associé à la socket.
        fichier = client.makefile("r", encoding="utf-8")

        # Lecture de la réponse envoyée par le serveur.
        ligne = fichier.readline()

        # Vérification de la réception d'une réponse.
        if not ligne:
            raise ConnectionError("Le serveur n'a pas envoyé de réponse.")

        # Conversion de la réponse JSON en dictionnaire Python.
        return json.loads(ligne)
