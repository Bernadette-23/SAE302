import socket
import json

def envoyer_demande(depart, destination):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(10)

        client.connect(("127.0.0.1", 5000))

        demande = {
            "depart": depart,
            "destination": destination
        }

        message = json.dumps(demande) + "\n"
        client.sendall(message.encode("utf-8"))

        fichier = client.makefile("r", encoding="utf-8")
        ligne = fichier.readline()

        if not ligne:
            raise ConnectionError("Le serveur n'a pas envoyé de réponse.")

        return json.loads(ligne)
