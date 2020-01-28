

import pandas
import argparse
import ast
import tempfile
import numpy as np

def make_temporary(submission):
    return tempfile.mkdtemp

def abx_average(filename, task_type):
    """Return ABX Error Rate"""
    df = pandas.read_csv(filename, sep='\t')
    if task_type == 'across':
        # aggregate on context
        groups = df.groupby(
            ['speaker_1', 'speaker_2', 'phone_1', 'phone_2'], as_index=False)
        df = groups['score'].mean()
    elif task_type == 'within':
        #arr = np.array(map(ast.literal_eval, df['by']))
        arr = np.array(list(map(ast.literal_eval, df['by'])))

        df['speaker']  = [e for e, f, g in arr]
        df['context'] = [f for e, f, g in arr]
        #del df['by']

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

def run_abx(features, task, temp_dir, output):
    """Run ABX pipeline"""
    # convert
    convert(features_path, 
            h5_filenames=os.path.join(temp, 'features.h5'), 
            load=_load_feat)
    # distance
    # switch depending on distances
    distances.compute_distances(os.path.join(temp, 'features.h5'),
                                'features', 
                                self.task,
                                os.path.join(temp, 'distance.h5'),
                                distance_fun,
                                normalized=normalized,
                                n_cpu = self.n_cpu)
    # score
    score(self.task,
          distance_file,
          score_file)

    # analyze
    analyze.analyze(self.task,
                    score_file,
                    analyze_file)
    # average
    abx_average(analyze_file)

def load_feat_2017(file_path):
    ### TODO PUT IN UTILS
    # read file, get features and return dict giving time and features
    with open(file_path, 'r') as fin:
        data = fin.readlines()
        for line in data:
            unit_data = line.strip('\n').split(' ')
            if len(unit_data) == 1:
                continue
            time.append(float(unit_data[0]))
            features.append([float(x) for x in unit_data])
    return {'time': times, 'features': features}

def load_feat_2019(file_path):
    ### TODO PUT IN UTILS
    # read file, get features and return dict giving time and features
    with open(file_path, 'r') as fin:
        data = fin.readlines()
        for line in data:
            unit_data = line.strip('\n').split(' ')
            if len(unit_data) == 1:
                continue
            time.append(float(unit_data[0]))
            features.append([float(x) for x in unit_data])
    return {'time': times, 'features': features}

def get_tasks(task_folder, year):
    """Return the paths to the ABX tasks file"""
    if year == 2019:
        return {"english": os.path.join(task_folder, 'by-context-across-speakers.abx')}
    else:
        return {("english", "1s", "across"): os.path.join(task_folder, "english", '1s_byCtxt_acSpkr.abx'),
                ("english", "10s", "across"): os.path.join(task_folder, "english",'10s_byCtxt_acSpkr.abx'),
                ("english", "120s", "across"): os.path.join(task_folder, "english",'120s_byCtxt_acSpkr.abx'),
                ("french", "1s", "across"): os.path.join(task_folder, "french", '1s_byCtxt_acSpkr.abx'),
                ("french", "10s", "across"): os.path.join(task_folder, "french",'10s_byCtxt_acSpkr.abx'),
                ("french", "120s", "across"): os.path.join(task_folder, "french",'120s_byCtxt_acSpkr.abx'),
                ("mandarin", "1s", "across"): os.path.join(task_folder, "mandarin", '1s_byCtxt_acSpkr.abx'),
                ("mandarin", "10s", "across"): os.path.join(task_folder, "mandarin",'10s_byCtxt_acSpkr.abx'),
                ("mandarin", "120s", "across"): os.path.join(task_folder, "mandarin",'120s_byCtxt_acSpkr.abx'),
                ("english", "1s", "within"): os.path.join(task_folder, "english", '1s_byCtxtSpkr.abx'),
                ("english", "10s", "within"): os.path.join(task_folder, "english",'10s_byCtxtSpkr.abx'),
                ("english", "120s", "within"): os.path.join(task_folder, "english",'120s_byCtxtSpkr.abx'),
                ("french", "1s", "within"): os.path.join(task_folder, "french", '1s_byCtxtSpkr.abx'),
                ("french", "10s", "within"): os.path.join(task_folder, "french",'10s_byCtxtSpkr.abx'),
                ("french", "120s", "within"): os.path.join(task_folder, "french",'120s_byCtxtSpkr.abx'),
                ("mandarin", "1s", "within"): os.path.join(task_folder, "mandarin", '1s_byCtxtSpkr.abx'),
                ("mandarin", "10s", "within"): os.path.join(task_folder, "mandarin",'10s_byCtxtSpkr.abx'),
                ("mandarin", "120s", "within"): os.path.join(task_folder, "mandarin",'120s_byCtxtSpkr.abx')}

