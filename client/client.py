import socket

# toujours la 1ere socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 5000))

client.send("URGENCE".encode())
reponse = client.recv(1024)
print("Réponse du serveur : ", reponse.decode())

client.close()
