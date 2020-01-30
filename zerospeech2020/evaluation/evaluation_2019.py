from read_2019_features import *


class Evaluation2019():
    def __init__(self, submission
                 log=logging.getLogger(),
                 task=None):
        self._log = log

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')

        self._submission = submission
        if task is not None:
            self.task = task
        else:
            raise ValueError("No ABX task folder given, can't compute ABX")
        
        #self.all_languages = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']

    def _entropy_symbols(nbr_lines, d_symbol2occ):
        """Calculate the entropy for all different symbols in the file
    
        Argument(s);
        nbr_lines : number of symbols in the file (number of lines)
        d_symbol2occ : contains all different type of symbols and how many
        time they appear in the file
    
        Returns :
        ent_s : the entropy for all symbols
        """
        ent_s = 0
        for s in d_symbol2occ.keys():
            # Number of times symbol s was observed in the file
            s_occ = d_symbol2occ[s]
            # Probability of apparition of symbol s
            p_s = s_occ/nbr_lines
            if p_s > 0:
                ent_s += -(p_s * math.log(p_s, 2))
        return ent_s


    def _bitrate(sym,  nbr_lines, total_duration):
        """Calculate bitrate
    
        Argument(s);
        nbr_lines : number of duration in the file (e.g number of lines)
        total_duration : total time duration of file
    
        Returns :
        bitrate : the bitrate for encoding given file as :
        B = (N/D) *  (H(s))
        Where N is the number of segmentation in the document (lines)
        D is the totel length of the audio file (sum of all durations)
        H(s) is the entropy for all symbols s that appears in the document
        """
        bitrate = None
        if len(sym) > 0:
            bitrate = nbr_lines*_entropy_symbols(nbr_lines, sym)/total_duration
        return bitrate
    
    def bitrate(features):
        symbol_counts, n_lines, total_duration = \
            read_all(
                args.file_list,
                args.folder,
                not args.dont_complain_about_missing_files,
                log=False)

    def evaluate_2019():
        """Run ABX evaluation and bitrate"""
        # compute abx
        feature_folder = os.path.join(self._submission, "2019",
                                               language)
        task = get_tasks(self.task_folder, 2019)["english"]
        if os.path.isdir(feature_folder):
            run_abx(feature_folder, tasks, load_feat_2019)
        else:
            raise ValueError("Trying to evaluate feature that doesn't exist for 2019 corpus")
        bitrate(features)

