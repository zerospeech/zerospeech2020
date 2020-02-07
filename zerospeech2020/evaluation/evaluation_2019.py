"""Evaluation for the 2019 data"""

import math
import glob
import shutil
import logging
import pkg_resources

from .utils import *
from zerospeech2020.read_2019_features import *

class Evaluation2019():
    def __init__(self, submission,
                 log=logging.getLogger(),
                 task=None,
                 language=['english', 'french'],
                 n_cpu=1,
                 normalize=1,
                 distance="cosine",
                 output=None):
        self._log = log
        self.n_cpu = n_cpu
        self.language = language
        self.output = output
        self.distance = distance
        self.normalize = normalize
        self.all_distances = ['cosine', 'KL', 'levenshtein']

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')

        self._submission = submission
        if task is not None:
            self.task_folder = task
        else:
            raise ValueError("No ABX task folder given, can't compute ABX")
        

    @staticmethod
    def _entropy_symbols(n_lines, symbol_counts):
        """Calculate the entropy for all different symbols in the file
    
        Argument(s);
        n_lines : number of symbols in the file (number of lines)
        symbol_counts : contains all different type of symbols and how many
        time they appear in the file
    
        Returns :
        ent_s : the entropy for all symbols
        """
        ent_s = 0
        for s in symbol_counts.keys():
            # Number of times symbol s was observed in the file
            s_occ = symbol_counts[s]
            # Probability of apparition of symbol s
            p_s = s_occ/n_lines
            if p_s > 0:
                ent_s += -(p_s * math.log(p_s, 2))
        return ent_s

    def _bitrate(self, symbol_counts,  n_lines, total_duration):
        """Calculate bitrate
    
        Argument(s);
        n_lines : number of duration in the file (e.g number of lines)
        total_duration : total time duration of file
    
        Returns :
        bitrate : the bitrate for encoding given file as :
        B = (N/D) *  (H(s))
        Where N is the number of segmentation in the document (lines)
        D is the totel length of the audio file (sum of all durations)
        H(s) is the entropy for all symbols s that appears in the document
        """
        bitrate = None
        if len(symbol_counts) > 0:
            bitrate = n_lines * self._entropy_symbols(n_lines,
                                                 symbol_counts)/total_duration
        return bitrate
    
    def bitrate(self, features, bitrate_file_list):
        symbol_counts, n_lines, total_duration = \
            read_all(
                bitrate_file_list,
                features,
                True,
                log=False)
        return self._bitrate(symbol_counts,  n_lines, total_duration)

    @staticmethod
    def _get_features(feature_folder, feat_tmp):
        for file_path in glob.iglob(feature_folder + "/*.txt"):
            filename = file_path.split('/')[-1]
            shutil.copyfile(file_path, os.path.join(feat_tmp, filename))


    def evaluate(self):
        """Run ABX evaluation and bitrate"""
        details_abx = dict()
        details_bitrate = dict()
        scores = dict()
        results_2019 = dict()
        # compute abx
        for lang in self.language:

            # Create temp folder for intermediary ABX files
            tmp = make_temporary()
            
            # extract auxiliary if they exist
            for folder in ['test', 'auxiliary1', 'auxiliary2']:

                # Create temp folder for features
                feat_tmp = make_temporary()
                feature_folder = os.path.join(self._submission, "2019",
                        lang, folder)

                # check if folder exist, otherise don't evaluate
                if not os.path.isdir(feature_folder):
                    continue
                self._get_features(feature_folder, feat_tmp)

                # Get ABX task
                task = get_tasks(self.task_folder, 2019)[lang]

                # Compute ABX score
                output = os.path.join(self.output)
                if os.path.isdir(feature_folder):
                    for distance_fun in self.all_distances:
                        if distance_fun == "cosine":
                            normalize = self.normalize
                        else:
                            normalize = None
                        print(folder)
                        print(distance_fun)
                        abx_score = run_abx(feat_tmp, task, tmp, 
                                load_feat_2019, self.n_cpu, distance_fun,
                                normalize,'across', self._log)
                        empty_tmp_dir(tmp)

                        details_abx['{}_{}_abx_{}'.format(lang, folder,
                            distance_fun)] = abx_score
                else:
                    raise ValueError("Trying to evaluate feature that"
                                     " doesn't exist for 2019 corpus")
                bitrate_file_list = pkg_resources.resource_filename(
                    pkg_resources.Requirement.parse('zerospeech2020'),
                    f'zerospeech2020/share/2019/{lang}/bitrate_filelist.txt')

                bitrate_score = self.bitrate(feat_tmp, bitrate_file_list)
                details_bitrate['{}_{}_bitrate'.format(lang,
                    folder)] = bitrate_score
                write_scores_19(abx_score, bitrate_score, lang, self.distance,
                                output)
            scores['{}_abx'.format(lang)] = details_abx['{}_test_abx_{}'.format(
                lang, self.distance)]
            scores['{}_bitrate'.format(lang)] = details_bitrate['{}_test_bitrate'.format(lang)]
        results_2019['scores'] = scores
        results_2019['details_bitrate'] = details_bitrate
        results_2019['details_abx'] = details_abx
        return results_2019

