#!/usr/bin/env python
import time
import argparse
import logging
import sys
from evaluation_2020 import Evaluation2020
#from .evaluation_2017 import Evaluation2017_track1 
#from .evaluation_2019 import *

# setup logging
logging.basicConfig(format='%(message)s', level=logging.DEBUG)
log = logging.getLogger()

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__,
        epilog='See https://zerospeech.com/2020 for complete documentation')
    parser.add_argument(
        'submission',
        help='path to submission (can be a directory or a zip archive)')
    subparser = parser.add_subparsers(help='edition', dest="edition")
    parser_17 = subparser.add_parser('2017')
    parser_19 = subparser.add_parser('2019')
    parser_all = subparser.add_parser('both')

    # if 2017 edition chosen 
    parser_17.add_argument('-l',
                           '--language',
                           choices=['english',
                                    'french',
                                    'mandarin',
                                    'lang1',
                                    'lang2'],
                           help='choose language to evaluate. If None chosen, all will be evaluated')

    subparser_17 = parser_17.add_subparsers(help='track', dest="track")
    track1_17 = subparser_17.add_parser('track1')

    track1_17.add_argument('-d',
                           '--distance',
                           default='cosine',
                           choices=['cosine', 'KL'],
                           help='Choose metric for ABX score')
    track1_17.add_argument('task_folder',
                           help='Folder containing the ABX tasks')

    track2_17 = subparser_17.add_parser('track2')

    # if 2019 edition chosen
    parser_19.add_argument('-l',
                           '--language',
                           choices=['english',
                                    'surprise'],
                           help='choose language to evaluate. If None chosen, all will be evaluated')

    parser_19.add_argument('-d',
                           '--distance',
                           default='cosine',
                           choices=['cosine', 'KL', 'levenshtein'],
                           help='Choose metric for ABX score')
    parser_19.add_argument('task_folder',
                           help='Folder containing the ABX tasks')
    # If both editions are chosen
    parser_all.add_argument('-l',
                           '--language',
                           choices=['english',
                                    'surprise'],
                           help='choose language to evaluate. If None chosen, all will be evaluated')

    parser_all.add_argument('task_folder',
                           help='Folder containing the ABX tasks')
    parser_all.add_argument('-d17',
                            '--distance17',
                            default='cosine',
                            choices=['cosine', 'KL'],
                            help='Choose metric for ABX score for 2017 edition')
    parser_all.add_argument('-d19',
                            '--distance19',
                            default='cosine',
                            choices=['cosine', 'KL', 'levenshtein'],
                            help='Choose metric for ABX score for 2019 edition')

    #parser.add_argument('-t',
    #    "--track",
    #    nargs='+',
    #    choices=['track1_17', 'track1_19', 'track2'],
    #    help="Choose track to evaluate. If none specified,"
    #         " trying to evaluate everything")
    #parser.add_argument('-l',
    #    "--languages",
    #    nargs='+',
    #    choices=['english_17', 'english_19',
    #             'french', 'mandarin'],
    #    help='Choose language to evaluate.'
    #         'If none specified, evaluating all')
    #parser.add_argument('-d',
    #        '--distance',
    #        default='cosine',
    #        choices=['KL', 'Levenshtein', 'cosine'],
    #        help='distance')
    parser.add_argument('-j',
        '--njobs',
        type=int,
        default=1,
        help="Number of jobs")

    args = parser.parse_args()
    print(args)

    try:
        Evaluation2020(args.submission, njobs=args.njobs,
                       log=log, edition=args.edition,
                       track=args.track,
                       language_choice=args.language,
                       tasks=args.task_folder,
                       distance="default",
                       normalize=1
                       ).evaluate()
    except ValueError as err:
        log.error(f'fatal error: {err}')
        log.error(
            'please fix the error and try again, '
            'or contact zerospeech2020@gmail.com if you need assistance')
        sys.exit(1)

if __name__ == "__main__": 
    main()
