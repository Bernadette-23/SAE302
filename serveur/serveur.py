import socket

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