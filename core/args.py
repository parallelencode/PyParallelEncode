#!/bin/env python
from pathlib import Path

from .commandtypes import Command
from encoders import ENCODERS


class Args(object):

    # noinspection PyTypeChecker
    def __init__(self, initial_data):
        # Input/Output/Temp
        self.input: Path = None
        self.temp: Path = None
        self.output_file: Path = None
        self.mkvmerge: bool = False

        # Splitting
        self.chunk_method: str = "hybrid"
        self.scenes: Path = None
        self.split_method: str = None
        self.extra_split: int = None
        self.min_scene_len: int = None

        # PySceneDetect split
        self.threshold: float = 35.0

        # AOM Keyframe split
        self.reuse_first_pass: bool = False

        # Encoding
        self.passes = None
        self.video_params: Command = None
        self.encoder: str = "aom"
        self.workers: int = None

        # FFmpeg params
        self.ffmpeg_pipe: Command = None
        self.ffmpeg: str = None
        self.audio_params = ['-c:a', 'copy']
        self.pix_format: str = "yuv420p"

        # Misc
        self.resume: bool = False
        self.no_check: bool = False
        self.keep: bool = False
        self.force: bool = False

        # Vmaf
        self.vmaf: bool = False
        self.vmaf_path: str = None
        self.vmaf_res: str = "1920x1080"

        # Target Vmaf
        self.vmaf_target: float = None
        self.vmaf_steps: int = 4
        self.min_q: int = 0
        self.max_q: int = 63
        self.vmaf_rate: int = 4
        self.n_threads: int = None
        self.vmaf_filter: str = None

        # VVC
        self.vvc_conf: Path = None
        self.video_dimensions = (None, None)
        self.video_framerate = None

        # Inner
        self.counter = None

        # Vapoursynth
        self.is_vs: bool = None

        for key in initial_data:
            setattr(self, key, initial_data[key])

        self.video_params = ENCODERS[self.encoder].default_args if self.video_params is None \
            else self.video_params

        self.ffmpeg_pipe = [*self.ffmpeg, '-strict', '-1', '-pix_fmt', self.pix_format,
                            '-bufsize', '50000K', '-f', 'yuv4mpegpipe', '-']
