import csv
import os
import threading
import time
import src.utils.globals as glob

# this needs to be module level variable
from typing.io import IO

from src.game.PlayerType import PlayerType

lockfile = threading.Lock()

csv_stats_file = open('db/stored_statistics.csv', mode='a+')
csv_stats_file.seek(0, os.SEEK_END)
csv_writer = csv.writer(csv_stats_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

# csv_writer.writerow(['username', 'playertype', 'issuccess', 'date'])


def insert_success(username: str, playertype: PlayerType):
    with lockfile:
        csv_writer.writerow([username, str(playertype), str(1), str(time.time())])


def insert_failure(username: str, playertype: PlayerType):
    with lockfile:
        csv_writer.writerow([username, str(playertype), str(0), str(time.time())])


def auto_flush_file(file: IO):
    while glob.server_running:
        time.sleep(20)
        with lockfile:
            file.flush()
