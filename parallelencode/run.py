import time

from parallelencode import Callbacks
from parallelencode.args import Args
from parallelencode.core.encode import encode_file
from parallelencode.core.vapoursynth import is_vapoursynth
from parallelencode.encoders import ENCODERS


# todo, saving and loading more info to the scenes data
def run(args, cb=Callbacks()):
    # Todo: Redo Queue
    if isinstance(args, dict):
        args = Args(args)

    args.video_params = ENCODERS[args.encoder].default_args if args.video_params is None \
        else args.video_params

    try:
        tm = time.time()
        is_vs = is_vapoursynth(args.input)
        args.is_vs = is_vs
        args.chunk_method = 'vs_lsmash' if is_vs else args.chunk_method
        encode_file(args, cb)

        print(f'Finished: {round(time.time() - tm, 1)}s\n')
        cb.run_callback("terminate", 0)
    except KeyboardInterrupt:
        print('Encoding stopped')
        cb.run_callback("terminate", 1)
