#!/usr/bin/env python3
import concurrent
import concurrent.futures
import json
import shutil
import sys
import time
import traceback
from pathlib import Path
from typing import List

import parallelencode.core.run_cmd
from parallelencode.VMAF.target_vmaf import target_vmaf_routine
from parallelencode.VMAF.vmaf import plot_vmaf
from parallelencode.args import Args
from parallelencode.callbacks import Callbacks
from parallelencode.chunks.chunk import Chunk
from parallelencode.chunks.chunk_queue import load_or_gen_chunk_queue
from parallelencode.chunks.resume import write_progress_file
from parallelencode.chunks.split import split_routine
from parallelencode.core.concat import concat_routine
from parallelencode.core.ffmpeg import extract_audio
from parallelencode.core.run_cmd import process_encoding_pipe, process_enc_debug_pipes
from parallelencode.core.setup import determine_resources, outputs_filenames, setup
from parallelencode.core.utils import frame_probe_fast, frame_probe
from parallelencode.encoders import ENCODERS


def encode_file(args: Args, cb: Callbacks):
    """
    Encodes a single video file on the local machine.

    :param args: The args for this encode
    :param cb: Callbacks
    :return: None
    """

    outputs_filenames(args)

    done_path = args.temp / 'done.json'
    resuming = args.resume and done_path.exists()

    # set up temp dir and logging
    setup(args.temp, args.resume)

    # find split locations
    split_locations = split_routine(args, resuming, cb)

    # create a chunk queue
    chunk_queue = load_or_gen_chunk_queue(args, resuming, split_locations, cb)

    # things that need to be done only the first time
    if not resuming:

        extract_audio(args.input, args.temp, args.audio_params, cb)

    # do encoding loop
    args.workers = determine_resources(args.workers)
    startup(args, chunk_queue, cb)
    encoding_loop(args, cb, chunk_queue)

    # concat
    concat_routine(args, cb)

    if args.vmaf:
        plot_vmaf(args.input, args.output_file, args, args.vmaf_path, args.vmaf_res, cb)

    # Delete temp folders
    if not args.keep:
        shutil.rmtree(args.temp)


def startup(args: Args, chunk_queue: List[Chunk], cb: Callbacks):
    """
    If resuming, open done file and get file properties from there
    else get file properties and

    """
    # TODO: move this out and pass in total frames and initial frames
    done_path = args.temp / 'done.json'
    if args.resume and done_path.exists():
        cb.run_callback("log", 'Resuming...\n')
        with open(done_path) as done_file:
            data = json.load(done_file)
        total = data['total']
        done = len(data['done'])
        initial = sum(data['done'].values())
        cb.run_callback("log", f'Resumed with {done} encoded clips done\n\n')
    else:
        initial = 0
        total = frame_probe_fast(args.input, args.is_vs)
        d = {'total': total, 'done': {}}
        with open(done_path, 'w') as done_file:
            json.dump(d, done_file)
    clips = len(chunk_queue)
    args.workers = min(args.workers, clips)
    cb.run_callback("log", f'\rQueue: {clips} Workers: {args.workers} Passes: {args.passes}\n'
                           f'Params: {" ".join(args.video_params)}')
    cb.run_callback("newtask", "Encoding video", total)
    cb.run_callback("startencode", total, initial)


def encoding_loop(args: Args, cb: Callbacks, chunk_queue: List[Chunk]):
    """Creating process pool for encoders, creating progress bar."""
    if args.workers != 0:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_cmd = {executor.submit(encode, cmd, args, cb): cmd for cmd in chunk_queue}
            for future in concurrent.futures.as_completed(future_cmd):
                try:
                    future.result()
                except Exception as exc:
                    _, _, exc_tb = sys.exc_info()
                    print(f'Encoding error {exc}\nAt line {exc_tb.tb_lineno}')
                    cb.run_callback("terminate", 1)


def encode(chunk: Chunk, args: Args, cb: Callbacks):
    """
    Encodes a chunk.

    :param chunk: The chunk to encode
    :param args: The cli args
    :param cb: The callback object
    :return: None
    """
    try:
        st_time = time.time()

        chunk_frames = chunk.frames

        cb.run_callback("log", f'Enc: {chunk.name}, {chunk_frames} fr\n\n')

        # Target Vmaf Mode
        if args.vmaf_target:
            target_vmaf_routine(args, chunk, cb)

        ENCODERS[args.encoder].on_before_chunk(args, chunk)

        # Run all passes for this chunk
        for current_pass in range(1, args.passes + 1):
            try:
                enc = ENCODERS[args.encoder]
                err = 1
                while err != 0:
                    pipe = enc.make_encode_pipes(args, chunk, args.passes, current_pass, chunk.output)

                    if not args.is_debug:
                        err = process_encoding_pipe(pipe, enc, cb)
                    else:
                        err = process_enc_debug_pipes(pipe, enc, cb)
                    if err != 0:
                        print("Error running encode on chunk: " + str(chunk) + "... Retrying...")

            except Exception as e:
                _, _, exc_tb = sys.exc_info()
                traceback.print_exc()
                print(f'Error at encode {e}. At line {exc_tb.tb_lineno}')

        ENCODERS[args.encoder].on_after_chunk(args, chunk)

        # get the number of encoded frames, if no check assume it worked and encoded same number of frames
        encoded_frames = chunk_frames if args.no_check else frame_check_output(chunk, chunk_frames)

        # write this chunk as done if it encoded correctly
        if encoded_frames == chunk_frames:
            write_progress_file(Path(args.temp / 'done.json'), chunk, encoded_frames)

        enc_time = round(time.time() - st_time, 2)
        cb.run_callback("log", f'Done: {chunk.name} Fr: {encoded_frames}\n'
            f'Fps: {round(encoded_frames / enc_time, 4)} Time: {enc_time} sec.\n\n')

    except Exception as e:
        _, _, exc_tb = sys.exc_info()
        print(f'Error in encoding loop {e}\nAt line {exc_tb.tb_lineno}')


def frame_check_output(chunk: Chunk, expected_frames: int) -> int:
    actual_frames = frame_probe_fast(chunk.output_path)
    if actual_frames != expected_frames:
        print(f'Frame Count Differ for Source {chunk.name}: {actual_frames}/{expected_frames}')
    return actual_frames
