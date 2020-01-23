"""Usefull abstractions to validate a submission for the ZRC2020"""

import logging
import os
import shutil
import tempfile
import zipfile

from .submission_2017 import Submission2017
from .submission_2019 import Submission2019
from .utils import validate_directory, validate_yaml


class Submission2020:
    def __init__(self, submission, njobs=1, log=logging.getLogger()):
        self._log = log
        self._njobs = njobs

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

        self._is_open_source = False

    def __del__(self):
        # delete the uncompressed zipfile if needed
        if self._is_zipfile:
            shutil.rmtree(self._submission)

    def is_valid(self):
        """Returns True if the submission is valid, False otherwise"""
        try:
            self.validate()
            return True
        except ValueError:
            return False

    def validate(self):
        """Raises a ValueError if the submission is not valid"""
        dir_2017, dir_2019 = self._validate_root()
        if dir_2017:
            self._validate_2017()
        if dir_2019:
            self._validate_2019()
            self._log.info('success, the submission is valid!')

    def _validate_root(self):
        existing = validate_directory(
            self._submission, 'top-level',
            ['metadata.yaml'], self._log, optional_entries=['2017', '2019'])

        if '2017' not in existing and '2019' not in existing:
            raise ValueError(
                'submission must contain at least a 2017 or 2019 directory')

        self._validate_root_metadata()
        return '2017' in existing, '2019' in existing

    def _validate_root_metadata(self):
        """Checks if the `metadata` file of a submission is valid"""
        # load the metadata YAML
        self._log.info('validating top-level metadata.yaml ...')
        filename = os.path.join(self._submission, 'metadata.yaml')
        metadata = validate_yaml(
            filename, 'metadata.yaml',
            {'author': str, 'affiliation': str, 'open source': bool})

        self._is_open_source = metadata['open source']
        self._log.info(
            '    submission declared as%s open source',
            '' if self._is_open_source else ' NOT')

    def _validate_2017(self):
        """Checks if submission for 2017 subset is valid"""
        Submission2017(
            os.path.join(self._submission, '2017'),
            self._is_open_source,
            njobs=self._njobs, log=self._log).validate()

    def _validate_2019(self):
        """Checks if submission for 2019 subset is valid"""
        Submission2019(
            os.path.join(self._submission, '2019'),
            self._is_open_source,
            log=self._log).validate()
