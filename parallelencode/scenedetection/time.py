from numpy import linspace

from parallelencode.callbacks import Callbacks
from parallelencode.core.utils import frame_probe


def time(video, split_frames, cb: Callbacks):
    """
    Running Time splitting on source video.
    """
    frames = frame_probe(video)
    to_add = frames // split_frames
    splits = None
    if frames % split_frames == 0:
        splits = list(linspace(split_frames, frames, to_add+1, dtype=int))
    else:
        splits = list(linspace(split_frames, frames - frames % split_frames, to_add + 1, dtype=int)) + [frames]
    cb.run_callback("log", f'Found scenes: {len(splits)}\n')

    return splits
