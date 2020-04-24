"""Utility functions for ZRC2020 validation"""

import atexit
import itertools
import os
import shutil
import tempfile
import zipfile

import joblib
import yaml


def validate_yaml(filename, name, entries, optional_entries={}):
    """Checks if a YAML metadata file have the expected format

    Parameters
    ----------
    filename (str): the YAML file to check

    name (str): nickname of the file to print error messages

    entries (dict): a dictionary of excepted entries to match in the YAML file.
        Each entry is in the form (name, type), where type can be None if no
        constraint on the expected type.

    optional_entries (dict): as the parameter `entries` but for optional
        entries. Can be present but not mandatory.

    Returns
    -------
    metadata (dict) : the entries parsed from the YAML file

    Raises
    ------
    ValueError if anything goes wrong

    """
    if not os.path.isfile(filename):
        raise ValueError(f'{name} file not found: {filename}')

    try:
        metadata = yaml.safe_load(open(filename, 'r', encoding='utf8').read().replace('\t', ' '))
    except yaml.YAMLError as err:
        raise ValueError(f'failed to parse {name}: {err}')

    if not metadata:
        raise ValueError(f'{name} file is empty')

    # ensure the mandatory entries are here
    mandatory = sorted(entries.keys())
    try:
        existing = sorted(metadata.keys())
    except AttributeError:  # yaml can load string only
        raise ValueError(f'failed to parse {name}')

    missing = [e for e in mandatory if e not in existing]
    if missing:
        raise ValueError(
            f'the following {name} entries are missing: {", ".join(missing)}')

    optional = sorted(optional_entries.keys())
    extra = [e for e in existing if e not in mandatory + optional]
    if extra:
        raise ValueError(
            f'the following {name} entries are forbidden: {", ".join(extra)}')

    # ensure all the entries are valid
    entries.update(optional_entries)
    for k, v in metadata.items():
        if v is None:
            raise ValueError(f'entry "{k}" is empty in {name}')
        if entries[k] and not isinstance(v, entries[k]):
            raise ValueError(
                f'entry "{k}" in {name} must be of type {entries[k]}')

    return metadata


def validate_code(directory, name, is_open_source, log):
    """Checks if a code directory is valid

    Parameters
    ----------
    directory (str): code directory to check

    name (str) : nickname of the dircetory for error message printing

    is_open_source (bool) : True if the flag "open source" is set in the
        submission, False otherwise

    log (logging.Logger) : where to send log messages

    Raises
    ------
    ValueError if anything goes wrong

    """
    log.info('validating directory %s ...', name)

    # if closed source, do not expect the directory to be present, but tolerate
    # an empty directory
    if not is_open_source and os.path.isdir(directory):
        if os.listdir(directory):
            raise ValueError(
                f'submission declared closed source but {name} directory '
                f'is not empty')

    # when declared opens source make sure the directory is not empty
    if is_open_source:
        if not os.path.isdir(directory):
            raise ValueError(
                f'submission declared open source but missing folder {name}')
        elif not os.listdir(directory):
            raise ValueError(
                f'submission declared open source but empty folder {name}')

        log.info(
            f'    non-empty directory, it will be manually '
            f'inspected to confirm the submission is open source')


def validate_directory(directory, name, entries, log, optional_entries=[]):
    """Checks if a directory contains the expected entries

    Parameters
    ----------
    directory (str) : the directory to check

    name (str) : nickname of the directory to print error messages

    entries (list) : a list of entries (files or directories) that must be
        fount in the directory

    log (logging.Logger) : to send log messages

    optional_entries (list) : a list of optional entries, may be here but not
        mandatory

    Returns
    -------
    existing (list) : The directory content

    Raises
    ------
    ValueError if anything goes wrong

    """
    log.info('validating directory %s ...', name)

    if not os.path.isdir(directory):
        raise ValueError(f'{name} directory not found')

    # ensure we have no extra entries
    existing = set(os.listdir(directory))
    extra = existing - (set(entries) | set(optional_entries))
    if extra:
        raise ValueError(
            f'{name} directory contains extra files or directories: '
            f'{resume(extra)}')

    # ensure all the required entries are here
    missing = set(entries) - existing
    if missing:
        raise ValueError(
            f'{name} directory has missing files or directories: '
            f'{resume(missing)}')

    return sorted(existing)


def resume(sequence, n=10):
    sequence = sorted(sequence)
    if len(sequence) > n:
        return ', '.join(sequence[:n]) + f' ... and {len(sequence) - n} more!'
    return ', '.join(sequence)


def log_errors(log, errors, name, n=20):
    """Log the first errors, a synthesis message and raise a ValueError"""
    log.error(f'validation errors for {name}:')
    for error in errors[:n]:
        log.error('    %s', error)
    if len(errors) > n:
        log.error(f'    ... and {len(errors) - n} more!')

    raise ValueError(
        f'invalid submission, found {len(errors)} errors in {name}')


def parallelize(function, njobs, args):
    return list(itertools.chain(
        *joblib.Parallel(n_jobs=njobs)(
            joblib.delayed(function)(*arg) for arg in args)))


def unzip_if_needed(submission, log):
    """Unzip the submission if this is a zip file

    The submission can be a directory or a zipfile, if zipfile it is
    uncompressed in a temporary folder that is destroyed at program exit.

    """
    # make sure the submission is either a directory or a zip
    if os.path.isdir(submission):
        return submission

    is_zipfile = zipfile.is_zipfile(submission)
    if not is_zipfile:
        raise ValueError(f'{submission} is not a directory or a zip file')

    # unzip the submission into a temp directory
    submission_unzip = tempfile.mkdtemp()
    log.info('Unzip submission to %s', submission_unzip)
    zipfile.ZipFile(submission, 'r').extractall(submission_unzip)

    # destroy the temp folder at program exit
    atexit.register(shutil.rmtree, submission_unzip)

    return submission_unzip
