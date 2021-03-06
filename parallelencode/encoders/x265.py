import os
import re

from parallelencode.args import Args
from parallelencode.chunks.chunk import Chunk
from parallelencode.core.commandtypes import MPCommands, CommandPair, Command
from parallelencode.encoders.encoder import Encoder
from parallelencode.core.utils import list_index_of_regex
from parallelencode.callbacks import Callbacks


class X265(Encoder):

    def __init__(self):
        super().__init__(
            encoder_bin='x265',
            encoder_help='x265 --fullhelp',
            default_args=['-p', 'slow', '--crf', '23', '-D', '10'],
            default_passes=1,
            default_q_range=(20, 40),
            output_extension='mkv'
        )

    def compose_1_pass(self, a: Args, c: Chunk, output: str) -> MPCommands:
        return [
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['x265', '--y4m', '--frames', str(c.frames), *a.video_params, '-', '-o', output]
            )
        ]

    def compose_2_pass(self, a: Args, c: Chunk, output: str) -> MPCommands:
        return [
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['x265', '--log-level', 'error', '--no-progress', '--pass', '1', '--y4m', '--frames', str(c.frames), *a.video_params, '--stats', f'{c.fpf}.log',
                 '-', '-o', os.devnull]
            ),
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['x265', '--log-level', 'error', '--pass', '2', '--y4m', '--frames', str(c.frames), *a.video_params, '--stats', f'{c.fpf}.log',
                 '-', '-o', output]
            )
        ]

    def man_q(self, command: Command, q: int) -> Command:
        """Return command with new cq value

        :param command: old command
        :param q: new cq value
        :return: command with new cq value"""

        adjusted_command = command.copy()

        i = list_index_of_regex(adjusted_command, r"--crf")
        adjusted_command[i + 1] = f'{q}'

        return adjusted_command

    def match_line(self, line: str, cb: Callbacks):
        """Extract number of encoded frames from line.

        :param line: one line of text output from the encoder
        :param cb: Callbacks reference in case error (not implemented)
        :return: match object from re.search matching the number of encoded frames"""

        return re.search(r"^\[.*\]\s(\d+)\/\d+", line)
