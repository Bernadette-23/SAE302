import socket
import json

from gestion_trajet import routes, dijkstra
from commun.base_donnees import enregistrer_evenement


def traiter_demande(demande):
    depart = demande.get("depart")
    destination = demande.get("destination")

    if not isinstance(depart, str) or not isinstance(destination, str):
        return {"erreur": "Départ ou destination invalide"}

    chemin, cout = dijkstra(routes, depart, destination)

    if not chemin:
        return {"erreur": "Aucun trajet possible"}

    # Enregistrement de la demande dans MariaDB
    enregistre = enregistrer_evenement(
        type_evenement="urgence",
        depart=depart,
        destination=destination,
        chemin=" -> ".join(chemin),
        cout=cout,
        details="Demande de priorité d'un véhicule d'urgence"
    )

    return {
        "chemin": chemin,
        "cout": cout,
        "nombre_de_feux": max(0, len(chemin) - 1),
        "evenement_enregistre": enregistre
    }


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
                        reponse = traiter_demande(demande)

                    except (ValueError, TypeError, KeyError):
                        reponse = {"erreur": "Demande invalide"}

                    connexion.sendall(
                        (json.dumps(reponse) + "\n").encode("utf-8")
                    )

    except KeyboardInterrupt:
        print("Arrêt du serveur.")

    finally:
        serveur.close()


if __name__ == "__main__":
    lancer_serveur()
