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


def find_combinations(scrambled_word, word_length, clues, find_online=False):
    temp, result = set(), set()

    if not scrambled_word:
        print('Please type a word')
        sys.exit(2)

    if word_length == 0:
        word_length = len(scrambled_word)

    permutation_list = list(permutations(scrambled_word, word_length))

    for permutation in permutation_list:
        temp.add(''.join(permutation))

    for word in sorted(list(temp)):
        if not clues or all(find_clue(word, f) for f in clues.split(",")):
            result.add(''.join(word))

    for word in sorted(result):
        found, _ = search_word_in_files(ROOT_DIR, word)

        if not found and find_online:
            try:
                kbbi = KBBI(word)
            except:
                result.remove(word)
        elif not found:
            result.remove(word)
        else:
            print(word)


def find_clue(word, clues):
    split = clues.split(":")
    letter_to = int(split[0])
    clue = split[1]
    return word[letter_to - 1] == clue


def search_word_in_files(root_dir, word):
    found = False
    res = None
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".txt"):
                file_path = os.path.join(subdir, file)
                with open(file_path, "r") as f:
                    for line in f:
                        if line.strip().lower().startswith(word):
                            found = True
                            res = extract_first_word(line.strip())
                            break

    return found, res


def extract_first_word(text):
    first_space = text.find(' ')

    if first_space == -1:
        return text
    else:
        return text[:first_space]


def unscrambler():
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

    try:
        opts, args = getopt.getopt(
            argv, "w:l:c:om:v", ['word=', 'length=', 'clues=', 'online', 'mode=', 'verbose'])
    except getopt.GetoptError:
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
            PROCESS_MODE = arg
        elif opt in ('-v', '--verbose'):
            VERBOSE = True
        else:
            return False, "Unrecognized option: " + opt

    unscrambler()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        sys.exit(2)
    main(sys.argv[1:])
