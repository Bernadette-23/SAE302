import socket
import json


def envoyer_demande(depart, destination):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(5)
        client.connect(("127.0.0.1", 5000))

        demande = {
            "depart": depart,
            "destination": destination
        }

        client.sendall(
            (json.dumps(demande) + "\n").encode("utf-8")
        )

        fichier = client.makefile("r", encoding="utf-8")
        reponse = json.loads(fichier.readline())

        return reponse



"""import socket
import json

def envoyer_demande(depart, destination):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.connect(("127.0.0.1", 5000))

        demande = {
            "depart": depart,
            "destination": destination
        }

        client.sendall(
            (json.dumps(demande) + "\n").encode("utf-8")
        )

        fichier = client.makefile("r", encoding="utf-8")
        reponse = json.loads(fichier.readline())

        print("Réponse du serveur :", reponse)


envoyer_demande("A", "H")
"""

"""
# toujours la 1ere socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

message = "URGENCE;1;A;H"

client.send(message.encode())

reponse = client.recv(1024)
print("Réponse du serveur :", reponse.decode())

client.close()
"""