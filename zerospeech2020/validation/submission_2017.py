"""Validation of the 2017 part of the ZRC2020"""

import logging
import os

from zerospeech2020.validation.utils import (
    validate_code, validate_yaml, validate_directory)


class Submission2017:
    def __init__(self, submission, is_open_source, log=logging.getLogger()):
        self._log = log
        self._is_open_source = is_open_source

        if not os.path.isdir(submission):
            raise ValueError('2017 submission not found')
        self._submission = submission


    def is_valid(self):
        """Returns True if the submission is valid, False otherwise"""
        try:
            self.validate()
            return True
        except ValueError:
            return False

    def validate(self):
        """Raises a ValueError if the submission is not valid"""
        validate_directory(
            self._submission, '2017',
            ['metadata.yaml', 'track1', 'track2'] +
            ['code'] if self._is_open_source else [],
            self._log)

        if 'track1' not in existing and 'track2' not in existing:
            raise ValueError(
                '2017 submission must contain at least '
                'a track1 or track2 directory')

        # check metadata.yaml file
        self._validate_metadata()

        # check 2017/code directory
        validate_code(
            os.path.join(self._submission, 'code'),
            '2017/code', self._is_open_source, self._log)

        # check the submission data
        if 'track1' in existing:
            self._validate_track1()
        if 'track2' in existing:
            self._validate_track2()

    def _validate_metadata(self):
        self._log.info('validating 2017/metadata.yaml')
        validate_yaml(
            os.path.join(self._submission, 'metadata.yaml'),
            '2017/metadata.yaml',
            {'system description': str,
             'hyperparameters': str})

    def _validate_track1(self):
        pass

    def _validate_track2(self):
        pass
