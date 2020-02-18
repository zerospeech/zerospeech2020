"""ABX evaluation code for ZeroSpeech2020"""

import ast
import logging
import numexpr
import numpy as np
import os
import pandas
import shutil
import sys
import tempfile
import warnings

import ABXpy
from ABXpy.distance import default_distance, dtw_kl_distance, edit_distance
from ABXpy.misc.any2h5features import convert
from ABXpy.score import score
from ABXpy.analyze import analyze


def get_tasks(dataset, year):
    """Return the paths to the ABX tasks file

    Parameters
    ----------
    dataset (str): path to the ZeroSpeech2020 dataset

    year (str): must be '2017' or '2019'

    Returns
    -------
    A dictionary of ABX task files related to the specified year (as abslotute
    paths).

    """
    task_folder = os.path.join(dataset, str(year), 'ABXTasks')
    if not os.path.isdir(task_folder):
        raise ValueError(f'directory not found: {task_folder}')

    if str(year) == '2019':
        return {"english": os.path.join(task_folder, 'byCtxt_acSpkr.abx')}
    else:
        return {
            ("english", "1s", "across"): os.path.join(
                task_folder, "english", '1s', '1s_byCtxt_acSpkr.abx'),
            ("english", "10s", "across"): os.path.join(
                task_folder, "english", '10s', '10s_byCtxt_acSpkr.abx'),
            ("english", "120s", "across"): os.path.join(
                task_folder, "english", '120s', '120s_byCtxt_acSpkr.abx'),
            ("french", "1s", "across"): os.path.join(
                task_folder, "french", '1s', '1s_byCtxt_acSpkr.abx'),
            ("french", "10s", "across"): os.path.join(
                task_folder, "french", '10s', '10s_byCtxt_acSpkr.abx'),
            ("french", "120s", "across"): os.path.join(
                task_folder, "french", '120s', '120s_byCtxt_acSpkr.abx'),
            ("mandarin", "1s", "across"): os.path.join(
                task_folder, "mandarin", '1s', '1s_byCtxt_acSpkr.abx'),
            ("mandarin", "10s", "across"): os.path.join(
                task_folder, "mandarin", '10s', '10s_byCtxt_acSpkr.abx'),
            ("mandarin", "120s", "across"): os.path.join(
                task_folder, "mandarin", '120s', '120s_byCtxt_acSpkr.abx'),
            ("english", "1s", "within"): os.path.join(
                task_folder, "english", '1s', '1s_byCtxtSpkr.abx'),
            ("english", "10s", "within"): os.path.join(
                task_folder, "english", '10s', '10s_byCtxtSpkr.abx'),
            ("english", "120s", "within"): os.path.join(
                task_folder, "english", '120s', '120s_byCtxtSpkr.abx'),
            ("french", "1s", "within"): os.path.join(
                task_folder, "french", '1s', '1s_byCtxtSpkr.abx'),
            ("french", "10s", "within"): os.path.join(
                task_folder, "french", '10s', '10s_byCtxtSpkr.abx'),
            ("french", "120s", "within"): os.path.join(
                task_folder, "french", '120s', '120s_byCtxtSpkr.abx'),
            ("mandarin", "1s", "within"): os.path.join(
                task_folder, "mandarin", '1s', '1s_byCtxtSpkr.abx'),
            ("mandarin", "10s", "within"): os.path.join(
                task_folder, "mandarin", '10s', '10s_byCtxtSpkr.abx'),
            ("mandarin", "120s", "within"): os.path.join(
                task_folder, "mandarin", '120s', '120s_byCtxtSpkr.abx')}


def _load_features_2017(file_path):
    """Get features and return dict giving time and features"""
    time = []
    features = []
    with open(file_path, 'r') as fin:
        data = fin.readlines()
        for line in data:
            unit_data = line.strip('\n').split(' ')
            if len(unit_data) == 1:
                continue
            time.append(float(unit_data[0]))
            features.append([float(x) for x in unit_data])
    return {'time': np.array(time), 'features': np.array(features)}


def _load_features_2019(file_path):
    # read file, get features and return dict giving time and features
    time = []
    features = []
    with open(file_path, 'r') as fin:
        data = fin.readlines()
        for i, line in enumerate(data):
            unit_data = line.strip('\n').split(' ')
            if len(unit_data) == 1:
                continue
            time.append(i/(len(data)))
            features.append([float(x) for x in unit_data])
    time = np.array(time)
    features = np.array(features)
    return {'time': np.array(time), 'features': np.array(features)}


def _average(filename, task_type):
    """Compute ABX averaged score from ABX analyze file

    To compute average, first average on context, then average on speaker, and
    finally average on phone.

    Parameters
    ----------
    filename (str): path to the ABX analyze file to average
    task_type (str) : must be within' or 'across'

    Returns
    -------
    average (float): the averaged error rate between 0 and 100 - the lower the
        better

    """
    df = pandas.read_csv(filename, sep='\t')
    if task_type == 'across':
        # aggregate on context
        groups = df.groupby(
            ['speaker_1', 'speaker_2', 'phone_1', 'phone_2'], as_index=False)
        df = groups['score'].mean()
    elif task_type == 'within':
        arr = np.array(list(map(ast.literal_eval, df['by'])))

        df['speaker'] = [e for e, f, g in arr]
        df['context'] = [f for e, f, g in arr]

        # aggregate on context
        groups = df.groupby(['speaker', 'phone_1', 'phone_2'], as_index=False)
        df = groups['score'].mean()
    else:
        raise ValueError('Unknown task type: {0}'.format(task_type))

    # aggregate on talker
    groups = df.groupby(['phone_1', 'phone_2'], as_index=False)
    df = groups['score'].mean()
    average = df.mean()['score']

    return (1.0 - average) * 100


def _abx(features_path, temp_dir, task, task_type, load_fun,
         distance, normalized, njobs, log):
    """Runs the ABX pipeline"""
    dist2fun = {
        'cosine': default_distance,
        'KL': dtw_kl_distance,
        'levenshtein': edit_distance}

    # convert
    log.debug('loading features ...')
    features = os.path.join(temp_dir, 'features.h5')
    if not os.path.isfile(features):
        convert(features_path, h5_filename=features, load=load_fun)

    # avoid annoying log message
    numexpr.set_num_threads(njobs)

    log.debug('computing %s distances ...', distance)
    # ABX Distances prints some messages we do not want to display
    sys.stdout = open(os.devnull, 'w')
    distance_file = os.path.join(temp_dir, 'distance_{}.h5'.format(task_type))
    with warnings.catch_warnings():
        # inhibit some useless warnings about complex to float conversion
        warnings.filterwarnings("ignore", category=np.ComplexWarning)

        # compute the distances
        ABXpy.distances.distances.compute_distances(
            features,
            'features',
            task,
            distance_file,
            dist2fun[distance],
            normalized,
            n_cpu=njobs)
    sys.stdout = sys.__stdout__

    log.debug('computing abx score ...')
    # score
    score_file = os.path.join(temp_dir, 'score_{}.h5'.format(task_type))
    score(task, distance_file, score_file)

    # analyze
    analyze_file = os.path.join(temp_dir, 'analyze_{}.csv'.format(task_type))
    analyze(task, score_file, analyze_file)

    # average
    abx_score = _average(analyze_file, task_type)
    return abx_score


def abx(features_path, year, task, task_type, distance, normalized,
        njobs=1, log=logging.getLogger()):
    """Run the ABX pipeline on the specified features

    Parameters
    ----------
    features_path (str): folder containing the features to evaluate.

    year (str): must be '2017' or '2019' according to evaluated part of the
        challenge.

    task (str): path to the ABX task file

    task_type (str): must be 'across' or 'within'.

    distance (str): name of the distance to use

    normalized (bool): choose to normalize or not DTW distance.

    njobs (int): the number of CPU cores to use.

    log (logging.Logger): where to send log messages.

    Raises
    ------
    ValueError if anything goes wrong.

    Returns
    -------
    abx_score (float): ABX error rate in [0, 100], lower is better

    """
    # get the features loading function according to year
    try:
        load_fun = {
            '2017': _load_features_2017,
            '2019': _load_features_2019}[str(year)]
    except KeyError:
        raise ValueError(f'year must be 2017 or 2019, it is {year}')

    # compute the ABX score, work in a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        return _abx(
            features_path,
            temp_dir,
            task,
            task_type,
            load_fun,
            distance,
            normalized,
            njobs,
            log)
    finally:
        shutil.rmtree(temp_dir)
