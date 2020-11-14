import csv
import threading
import time

# this needs to be module level variable
from src.game.PlayerType import PlayerType

lockfile = threading.Lock()

csv_stats_file = open('db/stored_statistics.csv', mode='w')
csv_writer = csv.writer(csv_stats_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

csv_writer.writerow(['username', 'playertype', 'issuccess', 'date'])


def insert_success(username: str, playertype: PlayerType):
    with lockfile:
        csv_writer.writerow([username, str(playertype), str(1), str(time.time())])
        csv_stats_file.flush()
    # Write a success into the file


def insert_failure(username: str, playertype: PlayerType):
    with lockfile:
        csv_writer.writerow([username, str(playertype), str(0), str(time.time())])
        csv_stats_file.flush()
