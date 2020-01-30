
import logging
import os
import shutil
import tempfile

from zerospeech2020.validation.utils import validate_directory
from evaluation_2019 import Evaluation2019
from evaluation_2017 import Evaluation2017_track1, Evaluation2017_track2
from utils import *

class Evaluation2020:
    def __init__(self, submission, njobs=1, log=logging.getLogger(),
                 edition=None,
                 track=None, language_choice=None,
                 tasks=None, distance="default",
                 normalize=1):
        self._log = log
        self.edition = edition
        self.njobs = njobs
        self._submission = submission
        self.track = track
        self.tasks = tasks
        self.normalize = normalize
        self.distance = distance
        if language_choice is not None:
            self.language_choice = language_choice
        else:
            self.language_choice = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']



    def _evaluate_abx(self):
        # launch ABX evaluation on existing folders
        existing = validate_directory(
            self._submission, 'top-level',
            ['metadata.yaml'], self._log, optional_entries=['2017', '2019'])

        if (self.edition == '2017' or 'both')  and self.track == 'track1':
            Evaluation2017_track1(self._submission,
                 self._log,
                 self.language_choice,
                 self.tasks,
                 self.njobs,
                 self.normalize,
                 self.distance).evaluate()
        if  (self.edition == '2019' or 'both'):
            Evaluation2019_track1(self._submission,
                 self._log,
                 self.language_choice).evaluate()

    def _evaluate_tde(self):
        self._log.info('evaluating track2')

        Evaluation2017_track2(self._submission,
                 self._log,
                 self.language_choice).evaluate()

    def evaluate(self):
        if self.track == "track2":
            self._evaluate_tde()
        if self.track == "track1" or self.edition == "2019":
            self._evaluate_abx()

