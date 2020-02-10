import ast
import atexit
import logging
import numexpr
import numpy as np
import os
import pandas
import shutil
import sys
import tempfile

from ABXpy.misc.any2h5features import convert
from ABXpy.score import score
from ABXpy.analyze import analyze
from ABXpy.distances import distances
from ABXpy.distance import default_distance, edit_distance, dtw_kl_distance


def make_temporary():
    """ Create temporary folder for ABX files"""
    def remove_directory(d):
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)

    tmpdir = tempfile.mkdtemp()
    atexit.register(remove_directory, tmpdir)
    return tmpdir


def empty_tmp_dir(tmp):
    """ Remove ABX files from temporary folder"""
    for fn in os.listdir(tmp):
        file_path = os.path.join(tmp, fn)
        try:
            os.remove(file_path)
        except Exception:
            pass


def abx_average(filename, task_type):
    """ Compute ABX averaged score from ABX analyze file.
        To compute average, first average on context, then average on
        speaker, and finally average on phone.

        Output
        average - error rate between 0 and 100 - the lower the better

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

    average = (1.0-average)*100
    return (average)


def run_abx(features_path, task, temp, load, n_cpu,
            distance, normalized, task_type, log=logging.getLogger()):
    """ Run ABX pipeline
        Input
        features_path: folder containing features
        task :         path to ABX task file
        temp:          temporary folder to store ABX files
        load:          function to load the features
        n_cpu:         number of cpus to use
        distance:      name of the distance to use
        normalized:    choose to normalize or not DTW distance
        task_type:     specify if task is across or within

        Output
        abx_score:     ABX error rate
    """
    dist2fun = {'cosine': default_distance,
                'KL': dtw_kl_distance,
                'levenshtein': edit_distance}
    # convert
    features = os.path.join(temp, 'features.h5')

    if not os.path.isfile(features):
        convert(features_path,
                h5_filename=features,
                load=load)

    # switch depending on distances
    log.info('computing ABX score (%s distance)', distance)

    numexpr.set_num_threads(n_cpu)

    # ABX Distances prints some messages we do not want to display
    sys.stdout = open(os.devnull, 'w')
    distance_file = os.path.join(temp, 'distance_{}.h5'.format(task_type))
    distances.compute_distances(
        features,
        'features',
        task,
        distance_file,
        dist2fun[distance],
        normalized,
        n_cpu=n_cpu)
    sys.stdout = sys.__stdout__

    # score
    score_file = os.path.join(temp, 'score_{}.h5'.format(task_type))
    score(task, distance_file, score_file)

    # analyze
    analyze_file = os.path.join(temp, 'analyze_{}.csv'.format(task_type))
    analyze(task, score_file, analyze_file)

    # average
    abx_score = abx_average(analyze_file, task_type)
    return abx_score


def write_scores_17(across, within, language, duration, output):
    out_score = os.path.join(
        output, '{}_{}_abx.txt'.format(language, duration))
    with open(out_score, 'w') as fout:
        fout.write(u'across: {}\n'.format(across))
        fout.write(u'within: {}\n'.format(within))


def write_scores_19(abx_score, bitrate_score, language,
                    distance, output):
    out_score = os.path.join(output, '{}.txt'.format(language))
    with open(out_score, 'w') as fout:
        fout.write(u'ABX_distance: {}\n'.format(distance))
        fout.write(u'ABX_score: {}\n'.format(abx_score))
        fout.write(u'bitrate: {}\n'.format(bitrate_score))


def load_feat_2017(file_path):
    # read file, get features and return dict giving time and features
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


def load_feat_2019(file_path):
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


def get_tasks(task_folder, year):
    """Return the paths to the ABX tasks file"""
    if year == 2019:
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
