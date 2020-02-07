"""Get options and launch dispatch evaluation for 2017 or 2019 data"""

import logging
import zipfile
import tempfile

from .utils import *
from .evaluation_2019 import Evaluation2019
from zerospeech2020.validation.utils import validate_directory
from .evaluation_2017 import Evaluation2017_track1, Evaluation2017_track2


class Evaluation2020:
    def __init__(self, submission, njobs=1,
                 output=None,
                 log=logging.getLogger(),
                 edition=None,
                 track=None, language_choice=None,
                 tasks=None, distance="default",
                 normalize=1,
                 duration=['1s', '10s', '120s']):
        self._log = log
        self.edition = edition
        self.njobs = njobs
        self.output = output

        # make sure the submission is either a directory or a zip
        self._is_zipfile = zipfile.is_zipfile(submission)
        if not self._is_zipfile and not os.path.isdir(submission):
            raise ValueError(f'{submission} is not a directory or a zip file')

        # unzip the submission if this is a zip archive
        if self._is_zipfile:
            # unzip the submission into a temp directory
            self._submission = tempfile.mkdtemp()
            log.info('Unzip submission to %s', self._submission)
            zipfile.ZipFile(submission, 'r').extractall(self._submission)
        else:
            self._submission = submission

        self.track = track
        self.tasks = tasks
        self.normalize = normalize
        self.duration = duration

        # set distances for 17 and 19
        if edition == "both":
            self.distance17 = distance[0]
            self.distance19 = distance[1]
        else:
            self.distance17 = distance
            self.distance19 = distance

        # set language choices for 17 and 19
        self.language_choice = language_choice

    def _evaluate_abx(self):
        # launch ABX evaluation on existing folders
        results_2017 = dict()
        results_2019 = dict()
        existing = validate_directory(
            self._submission, 'top-level',
            ['metadata.yaml'], self._log, optional_entries=['2017', '2019'])
        if (
                self.edition == '2017'
                or self.edition == 'both') and self.track == 'track1':
            results_2017 = Evaluation2017_track1(self._submission,
                 self._log,
                 self.language_choice,
                 self.tasks,
                 self.njobs,
                 self.normalize,
                 self.distance17,
                 self.output,
                 self.duration).evaluate()
        if (self.edition == '2019' or self.edition == 'both'):
            results_2019 = Evaluation2019(self._submission,
                 self._log,
                 self.tasks,
                 self.language_choice,
                 self.njobs,
                 self.normalize,
                 self.distance19,
                 self.output).evaluate()
        return results_2017, results_2019

    def _evaluate_tde(self):
        results_2017 = Evaluation2017_track2(self._submission,
                 self._log,
                 self.language_choice,
                 self.output).evaluate()
        return results_2017

    def evaluate(self):
        if self.track == "track2" or self.edition == "both":
            return self._evaluate_tde()
        if self.track == "track1" or self.edition == "2019" or self.edition == "both":
            return self._evaluate_abx()
