from zerospeech2020.read_2019_features import *
import math
import pkg_resources
from utils import *
import logging
import glob
import shutil

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

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')

        self._submission = submission
        if task is not None:
            self.task_folder = task
        else:
            raise ValueError("No ABX task folder given, can't compute ABX")
        
        #self.all_languages = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']

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
        # compute abx
        for lang in self.language:

            # Create temp folder for intermediary ABX files
            tmp = make_temporary()

            # Create temp folder for features
            feat_tmp = make_temporary()
            feature_folder = os.path.join(self._submission, "2019",
                    lang, 'test')

            # check if folder exist, otherise don't evaluate
            if not os.path.isdir(feature_folder):
                continue
            self._get_features(feature_folder, feat_tmp)

            # Get ABX task
            task = get_tasks(self.task_folder, 2019)[lang]

            # Compute ABX score
            output = os.path.join(self.output)
            if os.path.isdir(feature_folder):
                abx_score = run_abx(feat_tmp, task, tmp, 
                        load_feat_2019, self.n_cpu, self.distance,
                        self.normalize,'across')

            else:
                raise ValueError("Trying to evaluate feature that"
                                 " doesn't exist for 2019 corpus")
            bitrate_file_list = pkg_resources.resource_filename(
                pkg_resources.Requirement.parse('zerospeech2020'),
                f'zerospeech2020/share/2019/{lang}/bitrate_filelist.txt')

            bitrate_score = self.bitrate(feat_tmp, bitrate_file_list)
            write_scores_19(abx_score, bitrate_score, lang, self.distance,
                            output)

