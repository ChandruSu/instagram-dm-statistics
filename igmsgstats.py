import os
import re
import sys
import json
import os.path as path
import pandas as pd

# ------------------------ CMD and File IO ------------------------

def get_args():
    ''' Extracts command line arguments and returns an
    array of atomic arguments and keyword arguments. '''

    args_in = iter(sys.argv)

    args = []
    kwargs = {}

    for arg in args_in:
        if arg.startswith('-'):
            kwargs[arg[1:]] = next(args_in)
        else:
            args.append(arg)

    return (args, kwargs)


def ismsgfile(fpath):
    ''' Validates instagram message filepath. '''
    return re.match('.*message_\d+\.json', fpath) is not None


def read_messages(dir_path):
    ''' Retreives data from JSON files and stores them in a single
    pandas data frame object. '''

    # retrieves all message_n.json files
    filenames = filter(lambda f: path.isfile(path.join(dir_path, f)) and ismsgfile(f), os.listdir(dir_path))

    frames = []
    for fname in filenames:
        raw = json.load(open(path.join(dir_path, fname), encoding='utf-8'))
        frame = pd.DataFrame(raw['messages'])
        frames.append(frame)

    # returns unified data frame
    return pd.concat(frames).reset_index()

# ------------------------- Data Analysis -------------------------



# -----------------------------------------------------------------

# program starts here.
if __name__ == '__main__':
    msgdir = os.getcwd()

    args, kwargs = get_args()

    # sets specified directory path for message files.
    if 'path' in kwargs:
        msgdir = kwargs['path']

    print(read_messages(msgdir))


