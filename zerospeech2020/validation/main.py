#!/usr/bin/env python
"""Checks if a submission to the ZeroSpeech 2020 challenge is valid"""

import argparse
import logging
import sys
from .submission_2020 import Submission2020


# setup logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)
log = logging.getLogger()


def main():
    # parse command line options
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=__doc__,
        epilog='See https://zerospeech.com/2020 for complete documentation')
    parser.add_argument(
        'submission',
        help='path to submission (can be a directory or a zip archive)')
    parser.add_argument(
        '-j', '--njobs', type=int, default=1,
        help='number of parallel processes to use for validation')
    args = parser.parse_args()

    try:
        Submission2020(args.submission, njobs=args.njobs, log=log).validate()
        sys.exit(0)
    except ValueError as err:
        log.error(f'fatal error: {err}')
        log.error(
            'please fix the error and try again, '
            'or contact zerospeech2020@gmail.com if you need assistance')
        sys.exit(1)


if __name__ == '__main__':
    main()
