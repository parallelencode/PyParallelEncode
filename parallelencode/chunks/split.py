#!/bin/env python

import os
import subprocess
from pathlib import Path
from subprocess import PIPE, STDOUT
from typing import List

from parallelencode.args import Args
from parallelencode.scenedetection import ffmpeg, time, pyscene
from parallelencode.callbacks import Callbacks


def split_routine(args: Args, resuming: bool, cb: Callbacks) -> List[int]:
    """
    Performs the split routine. Runs pyscenedetect/aom keyframes and adds in extra splits if needed

    :param args: the Args
    :param resuming: if the encode is being resumed
    :param cb: Callbacks
    :return: A list of frames to split on
    """
    scene_file = args.temp / 'scenes.txt'

    # if resuming, we already have the split file, so just read that
    if resuming:
        return read_scenes_from_file(scene_file)

    # determines split frames with pyscenedetect or aom keyframes
    split_locations = calc_split_locations(args, cb)

    # write scenes for resuming later if needed
    write_scenes_to_file(split_locations, scene_file)

    return split_locations


def write_scenes_to_file(scenes: List[int], scene_path: Path):
    """
    Writes a list of scenes to the a file

    :param scenes: the scenes to write
    :param scene_path: the file to write to
    :return: None
    """
    with open(scene_path, 'w') as scene_file:
        scene_file.write(','.join([str(x) for x in scenes]))


def read_scenes_from_file(scene_path: Path) -> List[int]:
    """
    Reads a list of split locations from a file

    :param scene_path: the file to read from
    :return: a list of frames to split on
    """
    with open(scene_path, 'r') as scene_file:
        scenes = scene_file.readline().strip().split(',')
        return [int(scene) for scene in scenes]


def segment(video: Path, temp: Path, frames: List[int], cb: Callbacks):
    """
    Uses ffmpeg to segment the video into separate files.
    Splits the video by frame numbers or copies the video if no splits are needed

    :param video: the source video
    :param temp: the temp directory
    :param frames: the split locations
    :param cb: Callback reference
    :return: None
    """

    cb.run_callback("log", 'Split Video\n')
    cmd = [
        "ffmpeg", "-hide_banner", "-y",
        "-i", video.absolute().as_posix(),
        "-map", "0:v:0",
        "-an",
        "-c", "copy",
        "-avoid_negative_ts", "1",
        "-vsync", "0"
    ]

    if len(frames) > 0:
        cmd.extend([
            "-f", "segment",
            "-segment_frames", ','.join([str(x) for x in frames])
        ])
        cmd.append(os.path.join(temp, "split", "%05d.mkv"))
    else:
        cmd.append(os.path.join(temp, "split", "0.mkv"))
    pipe = subprocess.Popen(cmd, stdout=PIPE, stderr=STDOUT)
    while True:
        line = pipe.stdout.readline().strip()
        if len(line) == 0 and pipe.poll() is not None:
            break

    cb.run_callback("log", 'Split Done\n')


def calc_split_locations(args: Args, cb: Callbacks) -> List[int]:
    """
    Determines a list of frame numbers to split on with pyscenedetect or aom keyframes

    :param args: the Args
    :param cb: Callback reference for log/failure
    :return: A list of frame numbers
    """
    # inherit video params from aom encode unless we are using a different encoder, then use defaults

    if args.split_method == 'none':
        cb.run_callback("log", 'Skipping scene detection\n')
        return []

    sc = []

    # Split from file
    if args.split_method == 'file':
        if args.scenes.exists():
            # Read stats from CSV file opened in read mode:
            cb.run_callback("log", 'Using Saved Scenes\n')
            return read_scenes_from_file(args.scenes)

    # Splitting using PySceneDetect
    elif args.split_method == 'pyscene':
        cb.run_callback("log", f'Starting scene detection Threshold: {args.threshold}\n')
        try:
            sc = pyscene(args.input, args.threshold, args.is_vs, args.temp, cb)
        except Exception as e:
            cb.run_callback("log", f'Error in PySceneDetect: {e}\n')
            print(f'Error in PySceneDetect{e}\n')

    # Splitting based on aom keyframe placement
    elif args.split_method == 'ffmpeg':
        stat_file = args.temp / 'keyframes.log'
        sc = ffmpeg(args.input, args.threshold, args.is_vs, args.temp, cb)
    elif args.split_method == "time":
        sc = time(args.input, args.time_split_interval, cb)
    else:
        print(f'No valid split option: {args.split_method}\nValid options: "pyscene", "aom_keyframes"')
        cb.run_callback("terminate", 1)

    # Write scenes to file

    if args.scenes:
        write_scenes_to_file(sc, args.scenes)

    return sc
