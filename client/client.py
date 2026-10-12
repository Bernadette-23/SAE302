import socket

# toujours la 1ere socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

message = "URGENCE;1;A;H"

client.send(message.encode())

reponse = client.recv(1024)
print("Réponse du serveur :", reponse.decode())

client.close()
