# Server for the Intro to AI module

## Description

 You can find the rules of the game in `./le-fantom-de-l-opera_rules_fr.pdf`

## Requirements

 - Find the dependencies in requirements.txt (none at the moment)

 - Python3.7 minimum

## To launch a game

1. `python3.7 server.py`

2. `python3.7 inspector.py`

3. `python3.7 random.fantom.py`

## Commands on the server

`quit` exit the server in a clean way

## Technical information

To connect a client to the server you need an authentication,
the authentication protocol is described in `protocol_doc.txt` and you have an example in the given clients

You can quit the server using quit in the console

## Additional information

You can set the level of importance of the logging messages : 
 - sent to text files
 - sent to the console

## Difference between game and server
Brown character : takes the moved character to his final position, instead of
any position on the path taken by the brown character.

## Timeout

There is now a timeout of 10 seconds to answer the questions asked by the
server.
