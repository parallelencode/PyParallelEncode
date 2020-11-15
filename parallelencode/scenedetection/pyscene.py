#!/bin/env python

import sys
from subprocess import Popen

try:
    from scenedetect.detectors import ContentDetector
    from scenedetect.scene_manager import SceneManager
    from scenedetect.video_manager import VideoManager
    from scenedetect.frame_timecode import FrameTimecode
except ImportError as e:
    print("Scenedetect not found. Encoding may fail if it tries to use it.")

from parallelencode.core.utils import frame_probe
from parallelencode.core.vapoursynth import compose_vapoursynth_pipe
from parallelencode.callbacks import Callbacks

if sys.platform == "linux":
    from os import mkfifo


def pyscene(video, threshold, is_vs, temp, cb: Callbacks):
    """
    Running PySceneDetect detection on source video for segmenting.
    Optimal threshold settings 15-50
    """

    min_scene_len = 15

    cb.run_callback("log", f'Starting PySceneDetect:\nThreshold: {threshold}, Is Vapoursynth input: {is_vs}\n')

    if is_vs:
        if sys.platform == "linux":
            vspipe_fifo = temp / 'vspipe.y4m'
            mkfifo(vspipe_fifo)
        else:
            vspipe_fifo = None

        vspipe_cmd = compose_vapoursynth_pipe(video, vspipe_fifo)
        vspipe_process = Popen(vspipe_cmd)

        # Get number of frames from Vapoursynth script to pass as duration to VideoManager.
        # We need to pass the number of frames to the manager, otherwise it won't close the
        # receiving end of the pipe, and will simply sit waiting after vspipe has finished sending
        # the last frame.
    frames = frame_probe(video)

    video_manager = VideoManager([str(vspipe_fifo if is_vs else video)])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=threshold, min_scene_len=min_scene_len))
    base_timecode = video_manager.get_base_timecode()

    video_manager.set_duration(duration=FrameTimecode(frames, video_manager.get_framerate()) if is_vs else None)
    cb.run_callback("newtask", "Pyscenedetect", frames)

    # Set downscale factor to improve processing speed.
    video_manager.set_downscale_factor()

    # Start video_manager.
    video_manager.start()

    scene_manager.detect_scenes(frame_source=video_manager, show_progress=True)

    # If fed using a vspipe process, ensure that vspipe has finished.
    if is_vs:
        vspipe_process.wait()

    # Obtain list of detected scenes.
    scene_list = scene_manager.get_scene_list(base_timecode)

    scenes = [int(scene[0].get_frames()) for scene in scene_list]

    # Remove 0 from list
    if scenes[0] == 0:
        scenes.remove(0)
    cb.run_callback("log", f'Found scenes: {len(scenes)}\n')

    return scenes
