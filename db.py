import sqlite3 as sqlite3
from core import Champion

#Funksjon for å legge til nye champions 
def leggTilChamp(navn, stein, saks, papir, conn):
    cur = conn.cursor()
    sql = f"INSERT INTO champions (name, rock, paper, scissor) VALUES ('{navn}', {int(stein)}, {int(saks)}, {int(papir)});"
    cur.execute(sql)
    conn.commit()

#Funksjon for å koble til database
def tilkobleDatabase(database):
    conn = sqlite3.connect(database)
    return conn

#Funksjon som retunerer en fortegnelse i riktig format med alle champions fra databasen
def retunerChamp(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM champions")
    rows = cur.fetchall()
    champions = {}
    for row in rows:
        champions[row[0]] = Champion(row[0], row[1], row[2], row[3])

    return champions


#leggTilChamp("Fredrik",70,15,15,tilkobleDatabase("database.db"))
#leggTilChamp("Tobias",40,20,40,tilkobleDatabase("database.db"))