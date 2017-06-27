import argparse
import argh
import os
import random
import re
import sys
import gtp as gtp_lib

from policy import PolicyNetwork
from strategies import RandomPlayer, PolicyNetworkBestMovePlayer, PolicyNetworkRandomMovePlayer, MCTS
from load_data_sets import DataSet, parse_data_sets

TRAINING_CHUNK_RE = re.compile(r"train\d+\.chunk.gz")

def gtp(strategy, read_file=None):
    n = PolicyNetwork(use_cpu=True)
    if strategy == 'random':
        instance = RandomPlayer()
    elif strategy == 'policy':
        instance = PolicyNetworkBestMovePlayer(n, read_file)
    elif strategy == 'randompolicy':
        instance = PolicyNetworkRandomMovePlayer(n, read_file)
    elif strategy == 'mcts':
        instance = MCTS(n, read_file)
    else:
        sys.stderr.write("Unknown strategy")
        sys.exit()
    gtp_engine = gtp_lib.Engine(instance)
    sys.stderr.write("GTP engine ready\n")
    sys.stderr.flush()

    play_side = 0
    while not gtp_engine.disconnect:
        if play_side % 2 == 0:
            inpt = input()
            if inpt != "quit":
                inpt = "play b " + inpt
        else:
            inpt = "genmove w"
        # handle either single lines at a time
        # or multiple commands separated by '\n'
        try:
            cmd_list = inpt.split("\n")
        except:
            cmd_list = [inpt]
        for cmd in cmd_list:
            engine_reply = gtp_engine.send(cmd)
            sys.stdout.write(engine_reply)
            if play_side % 2 == 1:
                sys.stdout.write(instance.showboard())
            sys.stdout.flush()
        play_side += 1

parser = argparse.ArgumentParser()
argh.add_commands(parser, [gtp])

if __name__ == '__main__':
    argh.dispatch(parser)
