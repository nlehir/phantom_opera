# Server for the Intro to AI module

## Description of the game

You can find the rules of the game in ./le-fantom-de-l-opera_rules_fr.pdf

## To launch a game

1) python3.6 server.py

2) python3.6 inspector.py

3) python3.6 random.fantom.py

You can also use a more recent version of python.

## Additional information 

You can set the level of importance of the logging messages : 
- sent to text files
- sent to the console

## Difference between game and server
Brown character : takes the moved character to his final position, instead of
any position on the path taken by the brown character.

## Todo

Edit protocol and server so that the players could connect in whatever order.

## Timeout

There is now a timeout of 10 seconds to answer the questions asked by the
server.
