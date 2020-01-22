"""Validation of the 2017 part of the ZRC2020"""

import logging
import numpy as np
import os
import pkg_resources

from zerospeech2020.validation.utils import (
    validate_code, validate_yaml, validate_directory, log_errors)


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
        existing = validate_directory(
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
             'hyperparameters': None})

    def _validate_track1(self):
        all_languages = ['english', 'french', 'mandarin', 'LANG1', 'LANG2']
        languages = validate_directory(
            os.path.join(self._submission, 'track1'),
            '2017/track1', [], self._log, optional_entries=all_languages)
        if not languages:
            raise ValueError('directory 2017/track1 is empty')

        missing = set(all_languages) - set(languages)
        if missing:
            self._log.warning(
                f'    missing optional languages for 2017/track1: {missing}')
        else:
            self._log.info(
                f'    found all the 5 languages {", ".join(all_languages)}')

        # ensure each submitted lang is valid
        for lang in languages:
            for duration in ('1s', '10s', '120s'):
                self._validate_track1_language(lang, duration)

    def _get_track1_filelist(self, lang, duration):
        filename = pkg_resources.resource_filename(
            pkg_resources.Requirement.parse('zerospeech2020'),
            f'zerospeech2020/share/2017/track1/{lang}_filelist.txt')
        return sorted(
            os.path.basename(f.strip()).replace('.wav', '.txt')
            for f in open(filename, 'r') if duration in f)

    def _validate_track1_language(self, lang, duration):
        # ensure the expected files are here
        expected_files = self._get_track1_filelist(lang, duration)
        validate_directory(
            os.path.join(self._submission, 'track1', lang, duration),
            f'2017/track1/{lang}/{duration}', expected_files, self._log)

        # ensure each file is correctly formatted TODO parallelize using joblib
        errors = []
        for f in expected_files:
            filename = os.path.join(
                self._submission, 'track1', lang, duration, f)

            # ensure the file is readable as a numpy array
            try:
                array = np.loadtxt(filename)
            except Exception:
                errors.append(
                    f'bad format for file 2017/track1/{lang}/{duration}/{f}')

            # ensure timestamps are valid TODO ensure this is working
            t0 = array[:-1, 0]
            t1 = array[1:, 0]
            if not (t0 < t1).all():
                errors.append(
                    f'bad timestamps for file '
                    f'2017/track1/{lang}/{duration}/{f}')

        if errors:
            log_errors(self._log, errors, f'2017/track1/{lang}/{duration}')

    def _validate_track2(self):
        pass
