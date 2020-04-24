"""Evaluation of the 2017 track2 part of the Zerospeech2020 challenge"""

from tdev2.measures.ned import Ned
from tdev2.measures.boundary import Boundary
from tdev2.measures.grouping import Grouping
from tdev2.measures.coverage import Coverage
from tdev2.measures.token_type import TokenType
from tdev2.readers.gold_reader import Gold
from tdev2.readers.disc_reader import Disc

import logging
import signal
import os
import pkg_resources
import sys


_VALID_LANGUAGES = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']


def evaluate(submission, languages, log=logging.getLogger(), njobs=1):
    """Evaluation of the 2017 track2: term discovery

    Compute all the term discovery metrics on the specified languages.

    Parameters
    ----------
    submission (str): the directory of the submission to evaluate

    languages (list): elements must be 'french', 'english', 'mandarin',
        'LANG1' or 'LANG2'. Note that gold files are not provided to
        participants for 'LANG1' and 'LANG2', evaluation for those languages
        will require an official submission to the challenge.

    log (logging.Logger): where to send log messages

    njobs (int): number of parallel jobs to compute grouping

    Raises
    ------
    ValueError if the method fails to load classes file or gold file for
    the specified `language`, or if the `language` is not valid.

    Returns
    -------
    score (dict): A dictionary with the following entries for each language:
        scores/ned, scores/coverage, scores/words and details. The 'details'
        entry contains the precision, recall and fscore for all the metrics.

    """
    score = {
        language: _evaluate_single(submission, language, log, njobs)
        for language in languages}
    return {'2017-track2': score}


def _evaluate_single(submission, language, log, njobs):
    log.info('evaluating 2017 track2 for %s', language)

    # ensure the language is valid
    if language not in _VALID_LANGUAGES:
        raise ValueError(
            f'invalid language {language}, must be in '
            f'{", ".join(_VALID_LANGUAGES)}')

    if not os.path.isdir(submission):
        raise ValueError(f'directory not found: {submission}')

    # load the gold data (raise on error)
    gold = _read_gold(language, log)

    # ensure the input class file exists and load the discovered classes
    class_file = os.path.join(
        submission, '2017', 'track2', f'{language}.txt')
    if not os.path.isfile(class_file):
        raise ValueError(f'file not found: {class_file}')
    disc = _read_discovered(class_file, language, gold, log)

    ned, coverage, details = _evaluate_lang(gold, disc, log, njobs)

    return {
        'scores': {
            'ned': ned,
            'coverage': coverage,
            'words': details['words']},
        'details': details}


def _read_gold(language, log):
    """Returns the gold for the given `language`

    Raises ValueError on error.

    """
    log.debug('reading track2 gold for %s', language)
    wrd_path = pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('tdev2'),
        'tdev2/share/{}.wrd'.format(language))
    phn_path = pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('tdev2'),
        'tdev2/share/{}.phn'.format(language))

    # on the challenge evaluation server, we add the gold for the surprise
    # languages (those are not available for participants)
    if language in ('LANG1', 'LANG2') and 'ZS2020_EVALUATION_SERVER' in os.environ:
        wrd_path = os.path.join(
            os.environ['ZS2020_EVALUATION_SERVER'], '2017', f'{language}.wrd')

        phn_path = os.path.join(
            os.environ['ZS2020_EVALUATION_SERVER'], '2017', f'{language}.phn')

    if not os.path.isfile(wrd_path) or not os.path.isfile(phn_path):
        raise ValueError(f'failed to load gold files for {language}')

    return Gold(wrd_path=wrd_path, phn_path=phn_path)


def _read_discovered(class_file, language, gold, log):
    log.debug('reading discovered classes for %s', language)
    sys.stdout = open(os.devnull, 'w')
    try:
        return Disc(class_file, gold)
    finally:
        sys.stdout = sys.__stdout__


def _evaluate_lang(gold, disc, log, njobs):
    """Compute all metrics on requested language"""
    details = {}

    log.debug('computing boundary...')
    boundary = Boundary(gold, disc)
    boundary.compute_boundary()
    details['boundary_precision'] = boundary.precision
    details['boundary_recall'] = boundary.recall
    details['boundary_fscore'] = boundary.fscore

    # put timeout, if grouping takes too long, just continue
    def handler(signum, frame):
        print('grouping takes too long, continuing')
        raise Exception('timeout')

    signal.signal(signal.SIGALRM, handler)
    signal.alarm(7200)
    try:
        log.debug('computing grouping...')
        grouping = Grouping(disc)
        grouping.compute_grouping()
        details['grouping_precision'] = grouping.precision
        details['grouping_recall'] = grouping.recall
        details['grouping_fscore'] = grouping.fscore
    except Exception as exc:
        details['grouping_precision'] = 'NA'
        details['grouping_recall'] = 'NA'
        details['grouping_fscore'] = 'NA'

    log.debug('computing token and type...')
    token_type = TokenType(gold, disc)
    token_type.compute_token_type()
    details['token_precision'], details['type_precision'] = (
        token_type.precision)
    details['token_recall'], details['type_recall'] = token_type.recall
    details['token_fscore'], details['type_fscore'] = token_type.fscore
    details['words'] = len(token_type.type_seen)

    log.debug('computing coverage...')
    coverage = Coverage(gold, disc)
    coverage.compute_coverage()
    details['coverage'] = coverage.coverage

    log.debug('computing ned...')
    ned = Ned(disc)
    ned.compute_ned()
    details['ned'] = ned.ned
    details['pairs'] = ned.n_pairs

    return ned.ned, coverage.coverage, details
