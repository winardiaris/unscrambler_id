#!/usr/bin/env python

import getopt
import os
import sys
from itertools import permutations
from multiprocessing import Process
from pathlib import Path
from threading import Thread

from kbbi import KBBI

# CONFIG
ROOT_DIR = Path.home().joinpath('.unscrambler_id')

# MODES
NORMAL = 1
MULTITHREADING = 2
MULTIPROCESSING = 3
MODES = [NORMAL, MULTITHREADING, MULTIPROCESSING]

# GLOBAL
SCRAMBLED_WORD = None
WORD_LENGTH = 0
CLUES = ""
FIND_ONLINE = False
PROCESS_MODE = MULTIPROCESSING
VERBOSE = False
OPTION = None


HELP = 1


def find_combinations(scrambled_word, word_length, clues, find_online=False):
    if not scrambled_word:
        print('Please type a word')
        show_help()
        sys.exit(2)

    if word_length == 0:
        permutation_list = [pm for wl in range(3, len(scrambled_word) + 1) for pm in permutations(scrambled_word, wl)]
    else:
        permutation_list = list(permutations(scrambled_word, word_length))

    result = {word for word in sorted({''.join(permutation) for permutation in permutation_list}) if not clues or all(find_clue(word, f) for f in clues.split(","))}

    for word in sorted(result):
        found, _ = search_word_in_files(ROOT_DIR, word)

        if not found and find_online:
            try:
                kbbi = KBBI(word)
            except:
                result.discard(word)
        elif not found:
            result.discard(word)
        else:
            print(word)


def find_clue(word, clues):
    letter_to, clue = map(str, clues.split(":"))
    if int(letter_to) <= len(word):
        return word[int(letter_to) - 1] == clue
    return False


def search_word_in_files(root_dir, word):
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(subdir, file), "r") as f:
                    for line in f:
                        if line.strip().lower().startswith(word):
                            return True, extract_first_word(line.strip())
    return False, None


def extract_first_word(text):
    first_space = text.find(' ')

    if first_space == -1:
        return text
    else:
        return text[:first_space]


def show_help():
    f = open("{}/man/unscrambler_id.man".format(ROOT_DIR), 'r')
    print(f.read())


def unscrambler():
    if OPTION == HELP:
        show_help()
        sys.exit(2)

    if VERBOSE:
        print('----------------------------------------------')
        print('Scrambled word \t: {}'.format(SCRAMBLED_WORD))
        print('Word length \t: {}'.format(WORD_LENGTH))
        print('Clues \t\t: {}'.format(CLUES))
        print('Find online? \t: {}'.format(FIND_ONLINE))
        print('Mode \t\t: {}'.format(PROCESS_MODE))
        print('----------------------------------------------\n')

    if PROCESS_MODE not in MODES:
        print("Unrecognized mode: {}".format(PROCESS_MODE))
        show_help()
        sys.exit(2)

    if PROCESS_MODE == NORMAL:
        find_combinations(SCRAMBLED_WORD, WORD_LENGTH, CLUES, FIND_ONLINE)
    elif PROCESS_MODE == MULTITHREADING:
        t = Thread(target=find_combinations, args=[SCRAMBLED_WORD, WORD_LENGTH, CLUES, FIND_ONLINE])
        t.run()
    elif PROCESS_MODE == MULTIPROCESSING:
        p = Process(target=find_combinations, args=(SCRAMBLED_WORD, WORD_LENGTH, CLUES, FIND_ONLINE))
        p.start()
        p.join()


def main(argv):
    global SCRAMBLED_WORD
    global WORD_LENGTH
    global CLUES
    global FIND_ONLINE
    global PROCESS_MODE
    global VERBOSE
    global OPTION

    try:
        opts, args = getopt.getopt(
            argv, "w:l:c:om:vh", ['word=', 'length=', 'clues=', 'online', 'mode=', 'verbose', 'help'])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-w', '--word'):
            SCRAMBLED_WORD = arg
        elif opt in ('-l', '--length'):
            WORD_LENGTH = int(arg)
        elif opt in ('-c', '--clues'):
            CLUES = arg
        elif opt in ('-o', '--online'):
            FIND_ONLINE = True
        elif opt in ('-m', '--mode'):
            PROCESS_MODE = int(arg)
        elif opt in ('-v', '--verbose'):
            VERBOSE = True
        elif opt in ('-h', '--help'):
            OPTION = HELP
        else:
            return False, "Unrecognized option: " + opt

    unscrambler()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        show_help()
        sys.exit(2)
    main(sys.argv[1:])
