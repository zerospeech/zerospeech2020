"""Validation of the 2019 part of the ZRC2020"""

import logging
import os

from zerospeech2020 import read_2019_features
from zerospeech2020.validation.utils import (
    validate_code, validate_yaml, validate_directory)


class Submission2019:
    def __init__(self, submission, is_open_source, log=logging.getLogger()):
        self._log = log
        self._is_open_source = is_open_source

        if not os.path.isdir(submission):
            raise ValueError('2019 submission not found')
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
            self._submission, '2019',
            ['metadata.yaml', 'english', 'surprise'] +
            ['code'] if self._is_open_source else [],
            self._log, all_exist=True)

        validate_code(
            os.path.join(self._submission, 'code'),
            '2019/code', self._is_open_source, self._log)

        # detect if we have auxiliary 1 and 2 embeddings (because in this
        # case we must check they are described in metadata)
        do_aux1 = self._detect_auxiliary('auxiliary_embedding1')
        if do_aux1:
            self._log.info('found auxiliary_embedding1')
        do_aux2 = self._detect_auxiliary('auxiliary_embedding2')
        if do_aux2:
            self._log.info('found auxiliary_embedding2')
        if do_aux2 and not do_aux1:
            raise ValueError(
                'found auxiliary_embedding2 but not auxiliary_embedding1')

        # check metadata.yaml file
        self._validate_metadata(do_aux1, do_aux2)

        # check the submission data
        self._validate_language('english', do_aux1, do_aux2)
        self._validate_language('surprise', do_aux1, do_aux2)

    def _detect_auxiliary(self, name):
        aux_dirs = [os.path.isdir(os.path.join(
            self._submission, l, name)) for l in ['english', 'surprise']]
        if aux_dirs == [True] * 2:
            return True
        elif aux_dirs == [False] * 2:
            return False
        else:
            raise ValueError(
                f'{name} is present for one language but not for the other')

    def _validate_metadata(self, do_aux1, do_aux2):
        self._log.info('validating 2019/metadata.yaml')
        entries = {
            'abx distance': str,
            'system description': str,
            'using parallel train': bool,
            'using external data': bool}
        optional_entries = {}
        if do_aux1:
            entries['auxiliary1 description'] = str
        else:
            optional_entries['auxiliary1 description'] = str
        if do_aux2:
            entries['auxiliary2 description'] = str
        else:
            optional_entries['auxiliary2 description'] = str

        metadata = validate_yaml(
            os.path.join(self._submission, 'metadata.yaml'),
            '2019/metadata.yaml', entries, optional_entries)

        valid_distances = ['dtw_cosine', 'dtw_kl', 'levenshtein']
        if metadata['abx distance'] not in valid_distances:
            raise ValueError(
                f'entry "abx distance" in 2019/metadata.yaml must be in '
                f'{valid_distances} but is "{metadata["abx distance"]}"')

        return metadata

    def _validate_language(self, language, do_aux1, do_aux2):
        val = LanguageValidation(language, self._log)
        val.validate(self._submission, do_aux1, do_aux2)

        if val.errors:
            self._log.error(f'Validation errors detected for 2019/{language}:')
            for error in val.errors[:20]:
                self._log.error('    %s', error)
            if len(val.errors) > 20:
                self._log.error(f'    ... and {len(val.errors) - 20} more!')

            raise ValueError(
                f'invalid submission, found {len(val.errors)} errors '
                f'in 2019/{language}')


class LanguageValidation:
    def __init__(self, language, log):
        self._log = log
        # make sure the language is valid
        if language not in ['english', 'surprise']:
            raise ValueError(
                'language must be "english" or "surprise", it is "{}"'
                .format(language))
        self._language = language

        # get the files needed for the validation
        self.required_list = self._get_file('required')
        self.bitrate_list = self._get_file('bitrate')
        self.embedding_list = self._get_file('embedding')

        # the list of error must remains empty for the submission to
        # be validated
        self.errors = []

    def _get_file(self, name):
        filename = os.path.realpath(os.path.join(
            os.path.dirname(__file__), '..',
            'data', '2019', self._language, '{}_filelist.txt'.format(name)))

        if not os.path.isfile(filename):
            raise ValueError(f'file not found: {filename}')

        return filename

    def _check_exists(self, directory, files_list):
        if not os.path.isdir(directory):
            raise ValueError(f'directory {directory} does not exist')
        root_dir = os.path.basename(directory)
        existing_files = set(os.listdir(directory))
        expected_files = set(
            os.path.basename(f.strip().split(' ')[0])
            for f in open(files_list, 'r'))

        missing_files = expected_files - existing_files
        for f in missing_files:
            self.errors.append(
                f'missing file 2019/{self._language}/{root_dir}/{f}')

    def _check_embedding(self, directory, files_list):
        read_zrsc2019.read_all(files_list, directory, False, log=self._log)

    def _validate_directory(self, directory, exist_list, embedding_list):
        self._log.info(
            'validating "2019/%s/%s" directory...',
            self._language, os.path.basename(directory))
        self._check_exists(directory, exist_list)
        if not self.errors:
            self._check_embedding(directory, embedding_list)

    def validate(self, submission, do_aux1, do_aux2):
        self.errors = []

        # the submissions directories to validate
        test_dir = os.path.join(
            submission, self._language, 'test')
        aux1_dir = os.path.join(
            submission, self._language, 'auxiliary_embedding1')
        aux2_dir = os.path.join(
            submission, self._language, 'auxiliary_embedding2')

        # validate the test_dir with final embeddings
        self._validate_directory(
            test_dir, self.required_list, self.embedding_list)

        # validate aux1_dir and aux2_dir if needed
        if do_aux1:
            self._validate_directory(
                aux1_dir, self.embedding_list, self.bitrate_list)
        if do_aux2:
            self._validate_directory(
                aux2_dir, self.embedding_list, self.bitrate_list)
