"""Evaluation of the 2017 part of the ZRC2020"""

import pkg_resources 

from tdev2.measures.ned import *
from tdev2.measures.boundary import *
from tdev2.measures.grouping import *
from tdev2.measures.coverage import *
from tdev2.measures.token_type import *
from tdev2.readers.gold_reader import *
from tdev2.readers.disc_reader import *

#class Evaluation2017:
#    def __init__(self, submission
#                 njobs=1, log=logging.getLogger()):
#        self._log = log
#        self._njobs = njobs
#
#        if not os.path.isdir(submission):
#            raise ValueError('2017 submission not found')
#        self._submission = submission

class Evaluation2017_track2():
    def __init__(self, submission
                 log=logging.getLogger()):
        self._log = log

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')
        self._submission = submission

        self.gold = None
        self.disc = None

    def _read_gold(self, language):
        self._log.info('reading track2 '
                       'gold for {}'.format(language))
        wrd_path = pkg_resources.resource_filename(
                pkg_resources.Requirement.parse('tdev2'),
                'tdev2/share/{}.wrd'.format(language))
        phn_path = pkg_resources.resource_filename(
                pkg_resources.Requirement.parse('tdev2'),
                'tdev2/share/{}.phn'.format(language))
        self.gold = Gold(wrd_path=wrd_path, 
                    phn_path=phn_path)

    def _read_discovered(self, class_file, language):
        self._log.info('reading discovered '
                        'classes for {}'.format(language))
        if not self.gold:
            raise ValueError('Trying to evaluate track2 without reading the gold')

        self.disc = Track2Reader(submission, self.gold)
 
    def _evaluate_lang(self):
        """Compute all metrics on requested language"""
        try:
            self._log.info('Computing Boundary...')
            boundary = Boundary(gold, disc, output)
            boundary.compute_boundary()
            boundary.write_score()
        except:
            self._log.warning('Was unable to compute boundary')

        try:
            self._log.info('Computing Grouping...')
            grouping = Grouping(disc, output)
            grouping.compute_grouping()
            grouping.write_score()
        except:
            self._log.warning('Was unable to compute grouping')

        try:
            self._log.info('Computing Token and Type...')
            token_type = TokenType(gold, disc, output)
            token_type.compute_token_type()
            token_type.write_score()
        except:
            self._log.warning('Was unable to compute Token/Type')

        try:
            self._log.info('Computing Coverage...')
            coverage = Coverage(gold, disc, output)
            coverage.compute_coverage()
            coverage.write_score()
        except:
            self._log.warning('Was unable to compute coverage')

        try:
            self._log.info('Computing ned...')
            ned = Ned(disc, output)
            ned.compute_ned()
            ned.write_score()
        except:
            self._log.warning('Was unable to compute ned')


    def evaluate(self):
        """Compute metrics on all languages"""
        all_languages = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']

        for language in all_languages:
            class_file = os.path.join(self._submission, "track2",
                         "{}.txt".format(language))
            # check if class  file exists and evaluate it
            if os.path.isfile(class_file):
                self._read_discovered(class_file, language)
                self._read_gold(language)
                self._eval_lang()


#class Evaluation2017_track1(Evaluation2017):
#    def __init__():
#
#    def _get_task(self, language, duration):
#        task_file = pkg_resources.resource_filename(
#           pkg_resources.Requirement.parse('zerospeech2020'),
#           os.path.join('zerospeech2020',
#                        'share', '2017',
#                        'tasks', language,
#                        '{}s'.format(duration)))
#
#    def _convert_to_h5(
#
