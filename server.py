import threading
import socket
import pickle
from core import Champion, Match, Shape, Team
from db import retunerChamp, tilkobleDatabase 
from rich import print
from rich.prompt import Prompt
from rich.table import Table
import time

#Starter socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 50002))
server.listen()
clients = []

#Kobler til databasen og retunerer alle championene som en fortegnelse
def getDatabase():
    conn = tilkobleDatabase("database.db")
    db = retunerChamp(conn)
    return db

db = getDatabase()

#Sterilizerer databasen ved hjelp av pickle og sender den til spillerne
def sendDatabase():
    db = getDatabase()
    pickleDB = pickle.dumps(db)
    for client in clients:
        client.send(pickleDB)
        time.sleep(1)

#Funksjon for å sende en melding til spillerne
def broadcast(message):
    for client in clients:
        client.send(message.encode("utf-8"))

#Funksjon som regner ut hvem som vinner spillet og sender resultatet til spillerne
def gameTime(player1,player2):
    champions = getDatabase()
    print('\n')

                    # Match
    match = Match(
    Team([champions[name] for name in player1]),
    Team([champions[name] for name in player2])
    )
    match.play()
    data = pickle.dumps(match)
    for client in clients:
        client.send(data)
        time.sleep(1)
    # Print a summary

spiller1 = []
spiller2 = []

#Funksjon som kommuniserer med spillerne og tar i mot alle meldingene de skriver
def handle_client(client):
    global spiller1
    global spiller2
    while True:
        try:
            #Hvis begge spillerne har valgt 2 champions, så starter gametime()
            if len(spiller1) == 2 and len(spiller2) == 2:
                    gameTime(spiller1,spiller2)
                    spiller1.clear()
                    spiller2.clear()                
            data = client.recv(1024)
            if data:
                if client == clients[0]:
                        melding = data.decode("utf-8")
                        if melding == "!disconnect":
                            clients.remove(client)
                            client.close()
                        elif str.title(melding) in db and len(spiller1) < 2:
                            spiller1.append(str.title(melding))
                            print(spiller1)
                        else:
                            client.send("Champion er ikke i tabellen, prøv igjen!".encode("utf-8"))
                            print("player 1: "+melding)

                elif client == clients[1]:
                    melding = data.decode("utf-8")
                    if melding == "!disconnect":
                            clients.remove(client)
                            client.close()
                    elif str.title(melding) in db and len(spiller2) < 2:
                            spiller2.append(str.title(melding))
                            print(spiller2)
                    else:
                        print("player 2: "+melding)
                        client.send("Champion er ikke i tabellen, prøv igjen!".encode("utf-8"))
                else:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()

#
def start_spill():
    broadcast("To spillere er koblet til, spillet kan nå starte!")
    clients[0].send("Du er spiller 1!".encode("utf-8"))
    clients[1].send("Du er spiller 2!".encode("utf-8"))
    sendDatabase()
    broadcast("Velg to champions fra taballen")

def receive():
    while True:
        print("Serveren er på og venter på tilkoblinger...")
        client, address = server.accept()
        clients.append(client)
        print(str(address)+" er koblet til")
        client.send("Du er nå koblet til, venter på enda en spiller...".encode("utf-8"))
        #Starter thread for å håndtere flere spillere samtidig
        thread = threading.Thread(target=handle_client, args=(client, )).start()
        #Når to spillere er koblet til serveren starter spillet og det er ikke mulig for nye spillere å koble til
        if len(clients) == 2:
            start_spill()
            break

    

if __name__ == "__main__":
    receive()
  

    