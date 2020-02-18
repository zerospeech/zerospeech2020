"""Bitrate evaluation code for 2019 part of ZeroSpeech2020"""

import math
import pkg_resources

from zerospeech2020.read_2019_features import read_all


def _entropy_symbols(symbol_counts, nlines):
    """Calculate the entropy for all different symbols in the file

    Parameters
    ----------
    n_lines (int): number of symbols in the file (number of lines).
    symbol_counts (dict): contains all different type of symbols and how many
        time they appear in the file.

    Returns
    -------
    entropy : the entropy for all symbols

    """
    entropy = 0
    for s in symbol_counts.keys():
        # Number of times symbol s was observed in the file
        s_occ = symbol_counts[s]

        # Probability of apparition of symbol s
        p_s = s_occ / nlines

        if p_s > 0:
            entropy -= p_s * math.log(p_s, 2)

    return entropy


def _bitrate(symbol_counts,  nlines, duration):
    """Calculate bitrate

    Parameters
    ----------
    symbol_counts (dict): contains all different type of symbols and how many
        time they appear in the file.

    nlines (int): number of duration in the file (e.g number of lines)

    duration (float): total time duration of file in seconds

    Returns
    -------
    bitrate (float): the bitrate in bits/s

    """
    bitrate = 0
    if symbol_counts:
        bitrate = nlines * _entropy_symbols(symbol_counts, nlines) / duration
    return bitrate


def bitrate(features, lang):
    """Returns the bitrate of given `features`

    Parameters
    ----------
    features (str): the path to the 2019 features directory, formatted as
        specified at https://zerospeech.com/2020/instructions.html#format.
    lang (str) : must be 'english' or 'surprise'.

    Returns
    -------
    bitrate (float): the bitrate for encoding given file as B = (N/D) * H(s)
        Where N is the number of segmentation in the document (lines),
        D is the total length of the audio file (sum of all durations) and
        H(s) is the entropy for all symbols s that appears in the document

    """
    bitrate_file_list = pkg_resources.resource_filename(
        pkg_resources.Requirement.parse('zerospeech2020'),
        f'zerospeech2020/share/2019/{lang}/bitrate_filelist.txt')

    symbol_counts, nlines, duration = read_all(
        bitrate_file_list, features, True, log=False)

    return _bitrate(symbol_counts,  nlines, duration)
