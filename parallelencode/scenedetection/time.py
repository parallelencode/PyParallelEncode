from numpy import linspace

from parallelencode.callbacks import Callbacks
from parallelencode.core.utils import frame_probe_fast


def time(video, split_frames, cb: Callbacks):
    """
    Running Time splitting on source video.
    """
    frames = frame_probe_fast(video)
    to_add = frames // split_frames
    splits = None
    splits = list(linspace(split_frames, frames - split_frames - (frames % split_frames), to_add, dtype=int))
    newsplits = []
    for i in splits:
        newsplits.append(i.item())
    cb.run_callback("log", f'Found scenes: {len(splits)}\n')

    return newsplits
