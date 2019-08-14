from accounting import utils
from accounting.client import client

import os
import re
import readline
import glob

import sys
import readline
from os import environ

class PathCompleter():  # Custom completer
    def __init__(self):
        pass
        # == #self.options = sorted(options)
    def complete(self, text, state):
        if state == 0:  # on first trigger, build possible matches
            pass
            if not text:
                self.matches = glob.glob(os.path.join('.', '*'))
            else:
                self.matches =  glob.glob(text+'*')
        # return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None
    def display_matches(self, substitution, matches, longest_match_length):
        line_buffer = readline.get_line_buffer()
        columns = environ.get("COLUMNS", 80)
        print()
        tpl = "{:<" + str(int(max(map(len, matches)) * 1.2)) + "}"
        buffer = ""
        for match in matches:
            #==#match = tpl.format(match[len(substitution):])
            match = tpl.format(match)
            if len(buffer + match) > columns:
                print(buffer)
                buffer = ""
            buffer += match
        if buffer:
            print(buffer)
        print("> ", end="")
        print(line_buffer, end="")
        sys.stdout.flush()

def create_client():
    completer = PathCompleter()
    readline.set_completer_delims(' \t\n;')
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    readline.set_completion_display_matches_hook(completer.display_matches)
    print('Enter a client database name\n\t')
    db_path = input("> ")
    db_extension = '.pickle'
    if not os.path.exists(db_path):
        if not db_path.endswith(db_extension):
            db_path += db_extension
        print('New database will be created at {}'.format(db_path))
        clients = []
    else:
        print('Read database from {}'.format(db_path))
        clients = utils.load_clients(db_path)
    
    client_name = input('Nom client: ')
    new_client = client.Client(client_name)
    print(new_client.name)
    utils.append_client_to_db(clients, new_client)
    print(' '.join(['{}:{}'.format(c.id_, c.name) for c in clients]))
    # == "
    # == "# save client list
    utils.save_clients(clients,  db_path)
# == "
# ====== #class MyCompleter(object):  # Custom completer
# ====== #
# ====== #    def __init__(self, options):
# ====== #        self.options = sorted(options)
# ====== #
# ====== #    def complete(self, text, state):
# ====== #        if state == 0:  # on first trigger, build possible matches
# ====== #            if not text:
# ====== #                self.matches = self.options[:]
# ====== #            else:
# ====== #                self.matches = [s for s in self.options
# ====== #                                if s and s.startswith(text)]
# ====== #
# ====== #        # return match indexed by state
# ====== #        try:
# ====== #            return self.matches[state]
# ====== #        except IndexError:
# ====== #            return None
# ====== #
# ====== #    def display_matches(self, substitution, matches, longest_match_length):
# ====== #        line_buffer = readline.get_line_buffer()
# ====== #        columns = environ.get("COLUMNS", 80)
# ====== #
# ====== #        print()
# ====== #
# ====== #        tpl = "{:<" + str(int(max(map(len, matches)) * 1.2)) + "}"
# ====== #
# ====== #        buffer = ""
# ====== #        for match in matches:
# ====== #            match = tpl.format(match[len(substitution):])
# ====== #            if len(buffer + match) > columns:
# ====== #                print(buffer)
# ====== #                buffer = ""
# ====== #            buffer += match
# ====== #
# ====== #        if buffer:
# ====== #            print(buffer)
# ====== #
# ====== #        print("> ", end="")
# ====== #        print(line_buffer, end="")
# ====== #        sys.stdout.flush()
# ====== #
# ====== #
# ====== #dates = [
# ====== #    '10/10/2013 13:03:51',
# ====== #    '10/10/2013 13:54:32',
# ====== #    '10/10/2013 18:48:48',
# ====== #    '10/10/2013 19:13:00',
# ====== #    '10/13/2013 12:58:17',
# ====== #    '10/13/2013 13:38:15',
# ====== #    '10/13/2013 16:48:58',
# ====== #    '10/13/2013 17:23:59',
# ====== #    '10/13/2013 20:09:56',
# ====== #    '10/13/2013 21:54:14',
# ====== #    '10/13/2013 21:57:43',
# ====== #    '10/13/2013 22:47:40',
# ====== #    '10/14/2013 13:32:53',
# ====== #    '10/14/2013 21:14:51',
# ====== #    '10/15/2013 10:18:23'
# ====== #    ]
# ====== #
# ====== #dates = [x.split(' ')[0] for x in dates]
# ====== #
# ====== #completer = MyCompleter(list(set(dates)))
# ====== #readline.set_completer_delims(' \t\n;')
# ====== #readline.set_completer(completer.complete)
# ====== #readline.parse_and_bind('tab: complete')
# ====== #readline.set_completion_display_matches_hook(completer.display_matches)
# ====== #print('Enter a date in m/d/yy format\n\t')
# ====== #date = input("> ")
