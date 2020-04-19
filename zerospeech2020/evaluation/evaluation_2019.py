"""Evaluation for the 2019 part of the ZeroSpeech2020 challenge"""

import glob
import logging
import os
import shutil
import tempfile

from zerospeech2020.evaluation import abx, bitrate


_VALID_LANGUAGES = ['english', 'surprise']
_VALID_DISTANCES = ['cosine', 'KL', 'levenshtein']


def evaluate(submission, dataset, languages, distance, normalize,
             njobs=1, log=logging.getLogger()):
    """Evaluation of the 2019 track: bitrate and ABX score

    Compute the ABX score and bitrate on the specified languages and durations
    subsets.

    Parameters
    ----------
    submission (str): the directory of the submission to evaluate

    dataset (str): path to the ZeroSpeech2020 dataset (required for the ABX
        task files).

    languages (list): elements must be 'english' or 'surprise'. Note that ABX
        tasks are not provided to participants for 'surprise', evaluation for
        those languages will require an official submission to the challenge.

    distance (str): the distance to use, must be 'cosine', 'KL' or
        'levenshtein'.

    normalize (bool): when True, normalize the DTW path during distance
        computions.

    njobs (int): the number of CPU cores to use.

    log (logging.Logger): where to send log messages.

    Raises
    ------
    ValueError if the method fails.

    Returns
    -------
    score (dict): the bitrates and ABX scores in the format score[language] and
        for each language the following entries: 'scores' are the main results,
        'details_abx' and 'details_bitrate' expose all the intermediate scores.

    """
    if distance not in _VALID_DISTANCES:
        raise ValueError(
            f'invalid distance {distance}, must be in '
            f'{", ".join(_VALID_DISTANCES)}')

    score = {language: _evaluate_single(
        submission, dataset, language, distance, normalize, njobs, log)
             for language in languages}
    return {'2019': score}


def _get_features(feature_folder, feat_tmp):
    for file_path in glob.iglob(feature_folder + "/*.txt"):
        filename = file_path.split('/')[-1]
        shutil.copyfile(file_path, os.path.join(feat_tmp, filename))


def _evaluate_single(submission, dataset, language,
                     distance, normalize, njobs, log):
    # ensure the language is valid
    if language not in _VALID_LANGUAGES:
        raise ValueError(
            f'invalid language {language}, must be in '
            f'{", ".join(_VALID_LANGUAGES)}')

    if not os.path.isdir(submission):
        raise ValueError('2019 submission not found')

    # to store the results
    details_abx = {}
    details_bitrate = {}

    for folder in ['test', 'auxiliary_embedding1', 'auxiliary_embedding2']:
        # check if folder exist, otherise don't evaluate
        feature_folder = os.path.join(submission, "2019", language, folder)
        if not os.path.isdir(feature_folder):
            continue

        log.info('evaluating 2019 track for %s %s', language, folder)

        # Create temp folder for features
        feat_tmp = tempfile.mkdtemp()
        try:
            _get_features(feature_folder, feat_tmp)

            # compute bitrate
            log.debug('computing bitrate ...')
            bitrate_score = bitrate.bitrate(feat_tmp, language)
            details_bitrate[folder] = bitrate_score
            details_abx[folder] = {}

            # compute abx score
            for distance_fun in _VALID_DISTANCES:
                details_abx[folder][distance_fun] = abx.abx(
                    feat_tmp,
                    '2019',
                    abx.get_tasks(dataset, '2019')[language],
                    'across',
                    distance_fun,
                    normalize if distance_fun == "cosine" else None,
                    njobs=njobs,
                    log=log)
        finally:
            shutil.rmtree(feat_tmp)

    try:
        return {
            'scores': {
                'abx': details_abx['test'][distance],
                'bitrate': details_bitrate['test']},
            'details_bitrate': details_bitrate,
            'details_abx': details_abx}
    except KeyError:
        # the folder is not good, nothing found in test, auxiliary_embedding1
        # or auxiliary_embedding2
        raise ValurError(f'bad submission {submission}, fount no data to evaluate')
