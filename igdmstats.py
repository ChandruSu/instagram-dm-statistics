import os
import re
import sys
import json
import datetime
import os.path as path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# ------------------------ CMD and File IO ------------------------

def failure(msg):
    print(f'\033[31m[Error] {msg}!\033[0m')
    quit()


def get_args():
    ''' Extracts command line arguments and returns an
    array of atomic arguments and keyword arguments. '''

    args_in = iter(sys.argv[1:])

    args = []
    kwargs = {}

    for arg in args_in:
        if arg.startswith('--'):
            args.append(arg[2:])
        elif arg.startswith('-'):
            kwargs[arg[1:]] = next(args_in, None)
        else:
            failure('Invalid argument, must be prefixed with - or --')

    return (args, kwargs)


def ismsgfile(fpath):
    ''' Validates instagram message filepath. '''
    return re.match('.*message_\d+\.json', fpath) is not None


def read_messages(dir_path):
    ''' Retreives data from JSON files and stores them in a single
    pandas data frame object. '''

    if dir_path is None:
        failure('Expected valid directory')

    # retrieves all message_n.json files
    filenames = tuple(filter(lambda f: path.isfile(path.join(dir_path, f)) and ismsgfile(f), os.listdir(dir_path)))

    if not len(filenames):
        failure('No message_n.json files found')

    frames = []
    for fname in filenames:
        raw = json.load(open(path.join(dir_path, fname), encoding='utf-8'))
        frame = pd.DataFrame(raw['messages'])
        frames.append(frame)

    # returns unified data frame
    data = pd.concat(frames).reset_index(drop=True)
    
    data.rename(columns={ 'timestamp_ms':'date' }, inplace=True)
    data['date'] = pd.to_datetime(data['date'], unit='ms')
    return data

# ------------------------- Data Analysis -------------------------

def process_message(stats, msg):
    ''' Extracts statistical information for a given message and stores
    it in stats dictionary. '''

    # creates stat container for user
    if msg['sender_name'] not in stats:
        stats[msg['sender_name']] = { 'count': 0, 'tchars': 0 }

    user = stats[msg['sender_name']]
    user['count'] += 1
    
    if isinstance(msg['content'], str):
        user['tchars'] += len(msg['content'])


def process_data(data):
    ''' Iterates through every message and calculates per-message statistics. '''

    stats = {}

    for index, row in data.iterrows():
        process_message(stats, row)

    for user, ustats in stats.items():
        ustats['achars'] = ustats['tchars'] / ustats['count']

    return stats


def display_stats(stats):
    print(f'''
    STATISTICS
    ----------''')

    for user, ustats in stats.items():
        print(f'''
        {user}
        ------
        Message Count: {ustats['count']}
        Total Chars: {ustats['tchars']}
        Average Chars: {ustats['achars']}
        ''')

# ----------------------- Message Retrieval -----------------------

def fetch_messages(data, date_):

    print(f'Messages from {date_.date()}:\n--------')

    data = data.sort_values('date')
    data['date'] = pd.to_datetime(data['date']).dt.date
    messages = data[data['date'] == date_.date()]
    
    for i, msg in messages.iterrows():
        print('{:<15} {}'.format(msg['sender_name'], msg['content']))

# ------------------------ Graph Plotting -------------------------

def plot_stats(data):
    ''' Represents message data as matplotlib graphs. '''

    df = data[['date', 'sender_name']]
    
    df['date'] = df['date'].dt.date
    fig = df.groupby(['date', 'sender_name']).size().unstack('sender_name').plot(kind='bar', stacked=True)
    plt.show()

# -----------------------------------------------------------------

HELP_TEXT = '''
Instagram direct message analytics. Author: Chandru Suresh (2022)

Instructions:
    To run, have pandas and matplotlib installed globally or in local
    virtual environment, then execute 'python igdmstats.py -path /path/to/dir'
    where the specified path contains the message.json file.

Arguments:
    -path [path]    Path to directory containing message.json files

    --plot          Plots stacked bar chart of messages over time
    --help          Prints this help text and quits program
'''

# program starts here.
if __name__ == '__main__':
    msgdir = os.getcwd()

    args, kwargs = get_args()

    if 'help' in args:
        print(HELP_TEXT)
        quit()

    # sets specified directory path for message files.
    if 'path' in kwargs:
        msgdir = kwargs['path']

    data = read_messages(msgdir)
    display_stats(process_data(data))
    
    if 'plot' in args:
        plot_stats(data)
    
    if 'list-messages' in kwargs:
        fetch_messages(data, pd.to_datetime(kwargs['list-messages']))

