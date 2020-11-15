#!/bin/env python

import os
import shutil
from pathlib import Path

from parallelencode.args import Args


def determine_resources(workers):
    """Returns number of workers that machine can handle with selected encoder."""

    # If set by user, skip
    if workers != 0:
        return workers

    cpu = os.cpu_count()
    workers = cpu // 2

    # fix if workers round up to 0
    if workers == 0:
        workers = 1

    return workers


def setup(temp: Path, resume):
    """Creating temporally folders when needed."""
    # Make temporal directories, and remove them if already presented
    if not resume:
        if temp.is_dir():
            shutil.rmtree(temp)

    (temp / 'split').mkdir(parents=True, exist_ok=True)
    (temp / 'encode').mkdir(exist_ok=True)


def outputs_filenames(args: Args):
    """
    Set output filename

    :param args: the Args
    """
    suffix = '.mkv'
    args.output_file = Path(args.output_file).with_suffix(suffix) if args.output_file \
        else Path(f'{args.input.stem}_{args.encoder}{suffix}')
