#!/bin/env python
from pathlib import Path

from parallelencode.core.commandtypes import Command


class Args(object):

    # noinspection PyTypeChecker
    def __init__(self, initial_data):
        # Input/Output/Temp
        self.input: Path = None
        self.temp: Path = Path(".temp")
        self.output_file: Path = None
        self.mkvmerge: bool = False

        # Splitting
        self.chunk_method: str = "vs_lsmash"
        self.split_method: str = "ffmpeg"

        # Time splitting
        self.time_split_interval: int = 240

        # PySceneDetect/FFMPEG split
        self.threshold: float = 0.3

        # File Splitting
        self.scenes: Path = None

        # Encoding
        self.passes = None
        self.video_params: Command = None
        self.encoder: str = "aom"
        self.workers: int = 0

        # FFmpeg params
        self.ffmpeg_pipe: Command = None
        self.ffmpeg: str = ""
        self.audio_params = ['-c:a', 'copy']
        self.pix_format: str = "yuv420p"

        # Misc
        self.resume: bool = False
        self.no_check: bool = False
        self.keep: bool = False

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

        # Vapoursynth
        self.is_vs: bool = None

        for key in initial_data:
            setattr(self, key, initial_data[key])

        self.ffmpeg_pipe = [*self.ffmpeg, '-strict', '-1', '-pix_fmt', self.pix_format,
                            '-bufsize', '50000K', '-f', 'yuv4mpegpipe', '-']

        if isinstance(self.input, str):
            self.input = Path(self.input)

        if isinstance(self.temp, str):
            self.temp = Path(self.temp)

        if isinstance(self.output_file, str):
            self.output_file = Path(self.output_file)