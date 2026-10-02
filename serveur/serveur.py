import socket

#création d'une premiere socket à voir et à affiner en consequence

serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur.bind(('127.0.0.1', 8080))
serveur.listen()
client, adresse = serveur.accept()
message = client.recv(1024)
print(message.decode())

serveur.close()