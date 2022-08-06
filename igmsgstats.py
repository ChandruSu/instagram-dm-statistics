import os
import re
import sys
import json
import datetime
import os.path as path
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------ CMD and File IO ------------------------

def failure(msg):
    print(f'\033[31m[Error] {msg}!\033[0m')
    quit()

def mstodate(ms):
    return datetime.datetime.fromtimestamp(ms/1000.0)

def get_args():
    ''' Extracts command line arguments and returns an
    array of atomic arguments and keyword arguments. '''

    args_in = iter(sys.argv)

    args = []
    kwargs = {}

    for arg in args_in:
        if arg.startswith('-'):
            kwargs[arg[1:]] = next(args_in, None)
        else:
            args.append(arg)

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
    data['date'] = pd.to_datetime(data['date'], unit='ms').dt.date
    return data

# ------------------------- Data Analysis -------------------------

def process_message(stats, msg):

    # creates stat container for user
    if msg['sender_name'] not in stats:
        stats[msg['sender_name']] = { 'count': 0, 'tchars': 0 }

    user = stats[msg['sender_name']]
    user['count'] += 1
    
    if isinstance(msg['content'], str):
        user['tchars'] += len(msg['content'])


def process_data(data):
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
        Total Chars: {ustats['achars']}
        Average Chars: {ustats['tchars']}
        ''')

# ------------------------ Graph Plotting -------------------------

def plot_stats(data):
    df = data[['date', 'sender_name']]
    df.groupby(['date', 'sender_name']).size().unstack('sender_name').plot(kind='bar', stacked=True)
    plt.show()

# -----------------------------------------------------------------

# program starts here.
if __name__ == '__main__':
    msgdir = os.getcwd()

    args, kwargs = get_args()

    # sets specified directory path for message files.
    if 'path' in kwargs:
        msgdir = kwargs['path']

    data = read_messages(msgdir)
    display_stats(process_data(data))
    plot_stats(data)
    print(data)

