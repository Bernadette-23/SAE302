"""
Module du serveur chargé de recevoir les demandes des clients,
de calculer les trajets et d'enregistrer les événements en base de données.
"""

import socket
import json
import threading

from commun.gestion_trajet import routes, dijkstra
from commun.base_donnees import enregistrer_evenement



def traiter_demande(demande):
    """
    Traite une demande de trajet en vérifiant les informations reçues,
    en calculant le chemin et en enregistrant l'événement dans MariaDB.
    """
    depart = demande.get("depart")
    destination = demande.get("destination")

    # Vérification des informations transmises par le client
    if not isinstance(depart, str) or not isinstance(destination, str):
        return {"erreur": "Départ ou destination invalide"}

    # Calcul du trajet le plus court à l'aide de l'algorithme de Dijkstra
    chemin, cout = dijkstra(routes, depart, destination)

    if not chemin:
        return {"erreur": "Aucun trajet possible"}

    # Enregistrement de la demande dans la base de données MariaDB
    enregistre = enregistrer_evenement(
        type_evenement="urgence",
        depart=depart,
        destination=destination,
        chemin=" -> ".join(chemin),
        cout=cout,
        details="Demande de priorité d'un véhicule d'urgence"
    )

    # Préparation de la réponse qui sera envoyée au client
    return {
        "chemin": chemin,
        "cout": cout,
        "nombre_de_feux": max(0, len(chemin) - 1),
        "evenement_enregistre": enregistre
    }


def lancer_serveur():
    """
    Démarre le serveur TCP, écoute les connexions des clients et traite
    leurs demandes de trajet avant de leur renvoyer une réponse JSON.
    """
    serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Autorise la réutilisation de l'adresse après l'arrêt du serveur
    serveur.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Association du serveur à l'adresse locale et au port 5000
    serveur.bind(("127.0.0.1", 5000))
    serveur.listen(5)

    print("Serveur en attente de demandes...")


    try:
        # Boucle principale : attente et traitement des connexions clientes
        while True:
            connexion, adresse = serveur.accept()
            print("Client connecté :", adresse)

            with connexion:
                # Lecture des messages envoyés par le client, ligne par ligne
                fichier = connexion.makefile("r", encoding="utf-8")

                for ligne in fichier:
                    try:
                        # Conversion du message JSON en dictionnaire Python
                        demande = json.loads(ligne)
                        reponse = traiter_demande(demande)

                    except (ValueError, TypeError, KeyError):
                        # Envoi d'un message d'erreur si la demande est invalide
                        reponse = {"erreur": "Demande invalide"}

                    # Conversion de la réponse en JSON et envoi au client
                    connexion.sendall(
                        (json.dumps(reponse) + "\n").encode("utf-8")
                    )

    except KeyboardInterrupt:
        # Arrêt propre du serveur lors d'une interruption au clavier
        print("Arrêt du serveur.")

    finally:
        # Fermeture de la socket du serveur
        serveur.close()


# Démarrage du serveur uniquement si ce fichier est exécuté directement
if __name__ == "__main__":
    lancer_serveur()