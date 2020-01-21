#!/usr/bin/env python
"""A script to convert a submission from ZRC2019 format to ZRC2020"""

import argparse
import os
import shutil
import yaml


def convert_2019_to_2020(zrc2019, zrc2020):
    if not os.path.isdir(zrc2019):
        raise ValueError(f'{zrc2019} is not a directory')

    if os.path.exists(zrc2020):
        raise ValueError(f'{zrc2020} already exists')
    os.makedirs(zrc2020)

    # create 2020/metadata.yaml
    metadata_2019 = yaml.safe_load(open(os.path.join(zrc2019, 'metadata.yaml'), 'r'))
    metadata_2020 = {}
    for k in ('author', 'affiliation', 'open source'):
        metadata_2020[k] = metadata_2019[k]
        del metadata_2019[k]
    yaml.safe_dump(
        metadata_2020,
        open(os.path.join(zrc2020, 'metadata.yaml'), 'w'))

    # copy submission from 2019 to 2020
    os.makedirs(os.path.join(zrc2020, '2019'))
    for k in ('code', 'english', 'surprise'):
        src = os.path.join(zrc2019, k)
        dst = os.path.join(zrc2020, '2019', k)
        if os.path.isdir(src):
            shutil.copytree(src, dst)

    # save 2020/2019/metadata.yaml
    yaml.safe_dump(
        metadata_2019,
        open(os.path.join(zrc2020, '2019', 'metadata.yaml'), 'w'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'zrc2019', help='input directory with the ZRC2019 submission')
    parser.add_argument(
        'zrc2020', help='output directory with the ZRC2020 submission')
    args = parser.parse_args()

    try:
        convert_2019_to_2020(args.zrc2019, args.zrc2020)
    except ValueError as err:
        print(f'fatal error: {str(err)}')


if __name__ == '__main__':
    main()
