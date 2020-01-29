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
    parser.add_argument('-t',
        "--track",
        choices=['track1_17', 'track1_19', 'track2'],
        help="Choose track to evaluate. If none specified,"
             " trying to evaluate everything")
    parser.add_argument('-l',
        "--languages",
        nargs='+',
        choices=['english_17', 'english_19',
                 'french', 'mandarin'],
        help='Choose language to evaluate.'
             'If none specified, evaluating all')
    parser.add_argument('-j',
        '--njobs',
        type=int,
        default=1,
        help="Number of jobs")

    args = parser.parse_args()

    try:
        Evaluation2020(args.submission, njobs=args.njobs,
                       log=log, track=args.track,
                       language_choice=args.languages
                       ).evaluate()
    except ValueError as err:
        log.error(f'fatal error: {err}')
        log.error(
            'please fix the error and try again, '
            'or contact zerospeech2020@gmail.com if you need assistance')
        sys.exit(1)

if __name__ == "__main__": 
    main()
