import socket

#création d'une premiere socket à voir et à affiner en consequence

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind(('127.0.0.1', 5000))
serveur.listen()
print("Serveur en attente d'une connexion...")

client, adresse = serveur.accept()
print("Client connecté !")
message = client.recv(1024)
print(message.decode())
client.send("Message reçu par le serveur".encode())

serveur.close()