#!/usr/bin/env python
"""Evaluate submission for the ZeroSpeech2020 challenge"""

import argparse
import json
import logging
import os
import sys

from zerospeech2020.evaluation import (
    evaluation_2017_track1,
    evaluation_2017_track2,
    evaluation_2019)
from zerospeech2020.validation import utils


# setup logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
log = logging.getLogger()


def _add_common_arguments(parser, add_dataset=True, add_njobs=True):
    parser.add_argument(
        'submission',
        help='path to submission (must be a directory or a zip archive)')
    parser.add_argument(
        '-o', '--output', metavar='<json>', default=None,
        help='''output JSON file to write. If not specified, write on
        standard output. If the file already exists and is a valid JSON file,
        update its content.''')

    if add_dataset:
        parser.add_argument(
            '-D', '--dataset', metavar='<dir>', default=None,
            help='path to the ZeroSpeech 2020 dataset. If not specified on '
            'command line, must be declared in the ZEROSPEECH2020_DATASET '
            'environment variable. The dataset is required to load the '
            'ABX task files.')

    if add_njobs:
        parser.add_argument(
            '-j', '--njobs', type=int, default=1, metavar='<int>',
            help="number of parallel jobs to use, default to %(default)s.")

    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help='increase verbosity level to DEBUG, default is INFO.')


def _write_output(score, output):
    log.info(
        'writing score to %s',
        'stdout' if output == sys.stdout else output)

    if output != sys.stdout:
        if os.path.dirname(output):
            os.makedirs(os.path.dirname(output), exist_ok=True)
        output = open(output, 'w')

    output.write(json.dumps(score, indent=4) + '\n')


def _parse_arguments():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog='See https://zerospeech.com/2020 for complete documentation')

    # define subparsers for editions/tracks
    subparser = parser.add_subparsers(
        help='''Choose the track you want to evaluate.
        Choices are 2017-track1, 2017-track2, 2019 or all.''', dest='track')

    # parser for 2017 track1 part of the challenge
    parser_2017_track1 = subparser.add_parser(
        '2017-track1',
        description='Evaluation of the 2017 track1 part of the challenge')
    _add_common_arguments(parser_2017_track1)
    parser_2017_track1.add_argument(
        '-l', '--language', default=None,
        choices=['english', 'french', 'mandarin'],
        help='Choose language to evaluate, default is to evaluate all.')
    parser_2017_track1.add_argument(
        '-dr', '--duration', default=None,
        choices=['1s', '10s', '120s'],
        help='Evaluate only one duration subset, default is to evaluate all.')
    parser_2017_track1.add_argument(
        '-d', '--distance', default='cosine', choices=['cosine', 'KL'],
        help='Choose metric for ABX score, default to %(default)s.')
    parser_2017_track1.add_argument(
        '-n', '--normalize', type=bool, metavar='<bool>', default=True,
        help="choose to normalize DTW distance, default to %(default)s.")

    # parser for 2017 track2 part of the challenge
    parser_2017_track2 = subparser.add_parser(
        '2017-track2',
        description='Evaluation of the 2017 track2 part of the challenge')
    _add_common_arguments(
        parser_2017_track2, add_dataset=False, add_njobs=False)
    parser_2017_track2.add_argument(
        '-l', '--language', default=None,
        choices=['english', 'french', 'mandarin'],
        help='Choose language to evaluate, default is to evaluate all.')

    # parser for 2019 part of the challenge
    parser_2019 = subparser.add_parser(
        '2019',
        description='Evaluation of 2019 part of the challenge')
    _add_common_arguments(parser_2019)
    parser_2019.add_argument(
        '-d', '--distance', default='cosine',
        choices=['cosine', 'KL', 'levenshtein'],
        help='Choose metric for ABX score, default to %(default)s')
    parser_2019.add_argument(
        '-n', '--normalize', type=bool, default=True, metavar='<bool>',
        help="choose to normalize DTW distance, default to %(default)s.")

    # parser for all the parts of the challenge
    parser_all = subparser.add_parser(
        'all',
        description='Evaluation of all the parts of the challenge at once, '
        'this assumes a complete submission')
    _add_common_arguments(parser_all)

    parser_all.add_argument(
        '-d17', '--distance-2017', default='cosine', choices=['cosine', 'KL'],
        help='Choose metric for 2017 track1 ABX, default to %(default)s.')
    parser_all.add_argument(
        '-n17', '--normalize_2017', type=bool, metavar='<bool>', default=True,
        help="""choose to normalize DTW distance for 2017 track1,
        default to %(default)s.""")
    parser_all.add_argument(
        '-d19', '--distance-2019', default='cosine',
        choices=['cosine', 'KL', 'levenshtein'],
        help='Choose metric for 2019 ABX score, default to %(default)s')
    parser_all.add_argument(
        '-n19', '--normalize-2019', type=bool, default=True, metavar='<bool>',
        help="""choose to normalize DTW distance for 2019,
        default to %(default)s.""")

    return parser.parse_args()


def main():
    """Entry point of the evalaution program"""
    # parse arguments
    args = _parse_arguments()

    # seutp logger verbosity
    if args.verbose:
        log.setLevel(logging.DEBUG)

    # complain if the output file already exists
    if args.output and os.path.isfile(args.output):
        log.warning(
            'output file %s already exists, will be overwritten', args.output)

    # dataset folder
    try:
        dataset = args.dataset or os.environ['ZEROSPEECH2020_DATASET']
    except AttributeError:
        dataset = None
    except KeyError:
        raise ValueError(
            'path to ZeroSpeech dataset not specified, '
            'please use the --dataset argument or the '
            'ZEROSPEECH2020_DATASET environment variable.')
    if dataset and not os.path.isdir(dataset):
        raise ValueError(f'path to dataset not found: {dataset}')

    # unzip the submission if needed
    submission = utils.unzip_if_needed(args.submission, log)

    # launch evaluation
    try:
        if args.track == '2017-track1':
            languages = (
                [args.language] if args.language
                else ['english', 'french', 'mandarin'])
            durations = (
                [args.duration] if args.duration else ['1s', '10s', '120s'])

            score = evaluation_2017_track1.evaluate(
                submission,
                dataset,
                languages,
                durations,
                args.distance,
                args.normalize,
                njobs=args.njobs,
                log=log)

        elif args.track == '2017-track2':
            languages = (
                [args.language] if args.language
                else ['english', 'french', 'mandarin'])

            score = evaluation_2017_track2.evaluate(
                submission,
                languages,
                log=log)

        elif args.track == '2019':
            score = evaluation_2019.evaluate(
                submission,
                dataset,
                ['english'],
                args.distance,
                args.normalize,
                njobs=args.njobs,
                log=log)

        else:  # args.track == 'all'
            score_2019 = evaluation_2019.evaluate(
                submission,
                dataset,
                ['english'],
                args.distance_2019,
                args.normalize_2019,
                njobs=args.njobs,
                log=log)

            score_2017_track1 = evaluation_2017_track1.evaluate(
                submission,
                dataset,
                ['english', 'french', 'mandarin'],
                ['1s', '10s', '120s'],
                args.distance_2017,
                args.normalize_2017,
                njobs=args.njobs,
                log=log)

            score_2017_track2 = evaluation_2017_track2.evaluate(
                submission,
                ['english', 'french', 'mandarin'],
                log=log)

            score = {
                '2019': score_2019['2019'],
                '2017-track1': score_2017_track1['2017-track1'],
                '2017-track2': score_2017_track2['2017-track2']}

        _write_output(score, args.output or sys.stdout)
    except ValueError as err:
        log.error(f'fatal error: {err}')
        log.error(
            'please fix the error and try again, '
            'or contact zerospeech2020@gmail.com if you need assistance')
        sys.exit(1)


if __name__ == "__main__":
    main()
