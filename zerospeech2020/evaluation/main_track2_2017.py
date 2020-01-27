#!/usr/bin/env python
import time
import argparse
import logging
from .evaluation_2017_track2 import Evaluation2017_track2

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

    args = parser.parse_args()

    try:
        Evaluation2017_track2(args.submission,
                              log=log).evaluate()
    except ValueError as err:
        log.error(f'fatal error: {err}')
        log.error(
            'please fix the error and try again, '
            'or contact zerospeech2020@gmail.com if you need assistance')
        sys.exit(1)

if __name__ == "__main__": 
    main()
