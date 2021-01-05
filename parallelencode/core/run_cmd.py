#!/bin/env python
import subprocess
from collections import deque
from subprocess import PIPE

from parallelencode.core.commandtypes import Command, CommandPair
from parallelencode.callbacks import Callbacks


def process_debug_pipes(pipes):
    encoder_history = deque(maxlen=20)
    while True:
        line = pipes[2].stdout.readline().strip()

        stderr1 = pipes[0].stderr.readline().strip()
        while len(stderr1) != 0:
            print("ffgen: " + stderr1)
            stderr1 = pipes[0].stderr.readline().strip()

        stderr2 = pipes[1].stderr.readline().strip()
        while len(stderr2) != 0:
            print("input: " + stderr2)
            stderr2 = pipes[1].stderr.readline().strip()

        stderr3 = pipes[2].stderr.readline().strip()
        while len(stderr3) != 0:
            print("enc: " + stderr3)
            stderr3 = pipes[2].stderr.readline().strip()

        if len(line) == 0 and pipes[2].poll() is not None:
            break
        if len(line) == 0:
            continue
        if line:
            encoder_history.append(line)
    if pipes[2].returncode != 0 and pipes[2].returncode != -2:
        print(f"Error: {pipes[2].stdout}")
        print(f"stderr: {pipes[2].stderr}")
        print(f"\nEncoder encountered an error: {pipes[2].returncode}")
        print('\n'.join(encoder_history))
    if pipes[2].returncode != 0 or pipes[0].returncode != 0 or pipes[1].returncode != 0:
        return 1
    return 0




def process_pipe(pipes):
    pipe = pipes[len(pipes) - 1]
    encoder_history = deque(maxlen=20)
    while True:
        line = pipe.stdout.readline().strip()
        if len(line) == 0 and pipe.poll() is not None:
            break
        if len(line) == 0:
            continue
        if line:
            encoder_history.append(line)

    if pipe.returncode != 0 and pipe.returncode != -2:
        print(f"Error: {pipe.stdout}")
        print(f"stderr: {pipe.stderr}")
        print(f"\nEncoder encountered an error: {pipe.returncode}")
        print('\n'.join(encoder_history))
    if pipe.returncode != 0 or pipes[0].returncode != 0 or pipes[1].returncode != 0:
        return 1
    return 0

def process_enc_debug_pipes(pipes, encoder, cb: Callbacks):
    encoder_history = deque(maxlen=20)
    frame = 0
    while True:
        line = pipes[2].stdout.readline().strip()

        stderr1 = pipes[0].stderr.readline().strip()
        while len(stderr1) != 0:
            print("ffgen: " + stderr1)
            stderr1 = pipes[0].stderr.readline().strip()

        stderr2 = pipes[1].stderr.readline().strip()
        while len(stderr2) != 0:
            print("input: " + stderr2)
            stderr2 = pipes[1].stderr.readline().strip()

        stderr3 = pipes[2].stderr.readline().strip()
        while len(stderr3) != 0:
            print("enc: " + stderr3)
            stderr3 = pipes[2].stderr.readline().strip()

        if len(line) == 0 and pipes[2].poll() is not None:
            break

        if len(line) == 0:
            continue

        match = encoder.match_line(line, cb)

        if match:
            new = int(match.group(1))
            if new > frame:
                cb.run_callback("newframes", new - frame)
                # counter.update(new - frame)
                frame = new

        if line:
            encoder_history.append(line)

    if pipes[2].returncode != 0 and pipes[2].returncode != -2:  # -2 is Ctrl+C for aom
        print(f"\nEncoder encountered an error: {pipes[2].returncode}")
        print('\n'.join(encoder_history))
    if pipes[2].returncode != 0 or pipes[0].returncode != 0 or pipes[1].returncode != 0:
        return 1
    return 0

def process_encoding_pipe(pipes, encoder, cb: Callbacks):
    encoder_history = deque(maxlen=20)
    frame = 0
    pipe = pipes[2]
    while True:
        line = pipe.stdout.readline().strip()

        if len(line) == 0 and pipe.poll() is not None:
            break

        if len(line) == 0:
            continue

        match = encoder.match_line(line, cb)

        if match:
            new = int(match.group(1))
            if new > frame:
                cb.run_callback("newframes", new - frame)
                # counter.update(new - frame)
                frame = new

        if line:
            encoder_history.append(line)

    if pipe.returncode != 0 and pipe.returncode != -2:  # -2 is Ctrl+C for aom
        print(f"\nEncoder encountered an error: {pipe.returncode}")
        print('\n'.join(encoder_history))
    if pipe.returncode != 0 or pipes[0].returncode != 0 or pipes[1].returncode != 0:
        return 1
    return 0


def make_pipes(ffmpeg_gen_cmd: Command, ffmpeg_cmd, encode_cmd):

    ffmpeg_gen_pipe = subprocess.Popen(ffmpeg_gen_cmd, stdout=PIPE, stderr=subprocess.DEVNULL)
    ffmpeg_pipe = subprocess.Popen(ffmpeg_cmd, stdin=ffmpeg_gen_pipe.stdout, stdout=PIPE, stderr=subprocess.DEVNULL)
    pipe = subprocess.Popen(encode_cmd, stdin=ffmpeg_pipe.stdout, stdout=PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True)
    return [ffmpeg_gen_pipe, ffmpeg_pipe, pipe]


def debug_make_pipes(ffmpeg_gen_cmd: Command, command: CommandPair):
    ffmpeg_gen_pipe = subprocess.Popen(ffmpeg_gen_cmd, stdout=PIPE, stderr=PIPE)
    ffmpeg_pipe = subprocess.Popen(command[0], stdin=ffmpeg_gen_pipe.stdout, stdout=PIPE, stderr=PIPE)
    pipe = subprocess.Popen(command[1], stdin=ffmpeg_pipe.stdout, stdout=PIPE,
                            stderr=PIPE,
                            universal_newlines=True)
    return [ffmpeg_gen_pipe, ffmpeg_pipe, pipe]