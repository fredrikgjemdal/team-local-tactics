import threading
import socket
import pickle
from core import Champion, Match, Shape, Team
from rich import print
from rich.prompt import Prompt
from rich.table import Table
import time

#Lager en socket instans og kobler til serveren via TCP
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 50002))

def print_match_summary(match: Match) -> None:

    EMOJI = {
        Shape.ROCK: ':raised_fist-emoji:',
        Shape.PAPER: ':raised_hand-emoji:',
        Shape.SCISSORS: ':victory_hand-emoji:'
    }

    # For each round print a table with the results
    for index, round in enumerate(match.rounds):

        # Create a table containing the results of the round
        round_summary = Table(title=f'Round {index+1}')

        # Add columns for each team
        round_summary.add_column("Red",
                                 style="red",
                                 no_wrap=True)
        round_summary.add_column("Blue",
                                 style="blue",
                                 no_wrap=True)

        # Populate the table
        for key in round:
            red, blue = key.split(', ')
            round_summary.add_row(f'{red} {EMOJI[round[key].red]}',
                                  f'{blue} {EMOJI[round[key].blue]}')
        print(round_summary)
        print('\n')

    # Print the score
    red_score, blue_score = match.score
    print(f'Red: {red_score}\n'
          f'Blue: {blue_score}')

    # Print the winner
    if red_score > blue_score:
        print('\n[red]Red victory! :grin:')
    elif red_score < blue_score:
        print('\n[blue]Blue victory! :grin:')
    else:
        print('\nDraw :expressionless:')


def print_available_champs(champions: dict[Champion]) -> None:

    # Create a table containing available champions
    available_champs = Table(title='Available champions')

    # Add the columns Name, probability of rock, probability of paper and
    # probability of scissors
    available_champs.add_column("Name", style="cyan", no_wrap=True)
    available_champs.add_column("prob(:raised_fist-emoji:)", justify="center")
    available_champs.add_column("prob(:raised_hand-emoji:)", justify="center")
    available_champs.add_column("prob(:victory_hand-emoji:)", justify="center")

    # Populate the table
    for champion in champions.values():
        available_champs.add_row(*champion.str_tuple)
    print(available_champs)

#Funksjon som tar i mot meldinger
def client_receive():
    while True:
        try:
            message = client.recv(1024)
            messageUTF8 = message.decode("utf-8")
            print(messageUTF8)
        #Det må være en bedre måte å gjøre dette på, men er dette jeg fikk til å funke for å ta i mot pickle meldingen
        except:
            #Spillet starter
            try:
                print('\n'
          'Welcome to [bold yellow]Team Local Tactics[/bold yellow]!'
          '\n'
          'Each player choose a champion each time.'
          '\n')
                champions = pickle.loads(message)
                print_available_champs(champions)
            except:
                #Her kommer resultatene av hvem som vinner spillet og det blir printa fint ved hjelp av print_match_summary
                matchResultat = pickle.loads(message)
                print_match_summary(matchResultat)
                print("")
                #Hvis spillerne ønsker kan de spille igjen ved å velge to nye champions
                print("Velg to nye champions hvis du vil spillet igjen")
                print("Skriv !disconnect hvis du vil avslutte")
                


def client_send():
    while True:
        message = input("")
        client.send(message.encode("utf-8"))

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()

