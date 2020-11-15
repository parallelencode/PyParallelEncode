<h1 align="center">
    <br>
    PyParallelEncode
    </br>
</h1>

<h2 align="center">Framework to split and encode videos</h2>

<h4 align="center">
</h4>
<h2 align="center">Easy, powerful, all-in-one encoding based on Av1an</h2>

<h3 align="center">Supported Formats</h3>
Input Containers: mkv, webm, mp4

Input Video Codecs: h264, hevc, vp8, vp9, av1, mpeg-4, ffv1

Input Audio Codecs: opus, mp3, flac, LPCM (wav)

Other input containers, codecs, will probably work, depening on what your ffmpeg supports,
but any combination of the above are officially supported.
If you have any errors open a github issue.

Output video codecs: AV1 / HEVC / H264 / VP9 / VP8.

Encoders supported: AOM, RAV1E, x265, x264, VPX.

Python example with default parameters:

    from pathlib import Path
    from parallelencode import run
    params = {"input": Path("input.mp4")}
    run(params)

<h2 align="center">Parameters</h2>

    input                   Path: Input file (default: None) Required. Either a video or vapoursynth file.
                            Note that while vapoursynth files are supported, using them will generate massive
                            temporary y4m files with some splitting algos, like ffmpeg and pyscenedetect.

    output_file             Path: output file to create (default: (input file name)_(encoder).mkv)
                            Recommended to end with .mkv to avoid errors.

    encoder                 str: Encoder to use 
                            (`aom`,`rav1e`,`vpx`,`x265`, `x264`)
                            (default: "aom")

    video_params            list[str]: It's strongly recommended to use shlex.split to generate
                            from a string.
                            (If not set, default encoder parameters will be used.)
                            (Example: 'video_params': shlex.split("--rt -t 12 --kf-max-dist=240")

    passes                  int: Number of passes for encoding. most encoders only support 1/2
                            (default: aomenc: 2, rav1e: 1, vpx: 2, x265: 1, x264: 1)

    workers                 int: Number of encoding workers. More means more instances of
                            encoder running at once. (default: half the system threads)
                                
    resume                  bool: If encode was stopped/quit resumes, redoing all partial chunks.
                            but skipping any chunks which have already been completed.
                            Does nothing if temp folder cannot be found. If found it automatically
                            skips scenedetection, audio encoding/copy, spliting, so it only works
                            after actual encoding has started. (default: False)

    no_check                bool: Skip checking numbers of frames for source and encoded chunks.
                            Needed if framerate changes are added in ffmpeg options. Not recommended
                            By default any differences in frames of encoded files will be reported
                            and will likely result in corrupted video. (default: False)

    keep                    bool: If true, do not delete temporary folder after completion.
                            (default: False)

    temp                    Path: path for temporally folders. (default: .temp)

    mkvmerge                bool: Use mkvmerge for concatenating instead of ffmpeg.
                            Recommended if concatenation fails. (default: False)

<h3 align="center">FFmpeg options</h3>

    audio_params            list[str]: FFmpeg audio args (Default: ['-c:a', 'copy'])
                            (Example: 'audio_params': shlex.split("-c:a libopus -b:a  64k")

    ffmpeg                  list[str]: FFmpeg video params. Run on each chunk before encoding.
                            (Warning: Cropping doesn't work with Target VMAF mode)
                            (default: None)
                            (Example: 'ffmpeg': shlex.split("-vf scale=320:240")

    pix_format              str: pixel/bit format for piping. This should match your
                            input video (default: 'yuv420p')
                            (Example for 10 bit source: 'pix_format': 'yuv420p10le')
                            Ensure your encoder supports this format and knows about it.

<h3 align="center">Segmenting</h3>

    split_method            str: Method used for generating splits.
                            (`ffmpeg`, `pyscene`, `time`, `file`, `none`) (default: 'ffmpeg')
                            `ffmpeg` - Content based scenedetection via built in computer vision
                            and iframe detection. (the best option in most cases for optimal splits)
                            `pyscene` - Content based scenedetection via opencv/pyscenedetect
                            (may drop frames with any NON intra-frame based format)
                            `time` - create regular interval splits from the 
                            `file` - read from file specified by 'scenes'
                            `none` - do not split the video. The only benefit of this is to use
                            pyparallelencode exclusively for target vmaf/per title encoding.

    chunk_method            str: How chunks are made for encoding.
                            (`vs_lsmash`, `segment`)
                            (default: `vs_lsmash`)
                            `vs_lsmash` - Consumes more ram (up to 0.1-1GB extra per worker) and more
                            cpu but is actually reliable when splitting non-intraframe video without
                            using the ffmpeg split method.
                            GREATLY reduces disk space needed as videos are not actually chunked.
                            Requires vapoursynth.
                            `segment` - The traditional method of splitting video. This splits
                            the video into numerous segments which take up disk space and are read
                            in and piped into.

    threshold               float: Scene detection threshold. Larger values make the scene detection algo
                            less sensitive while smaller provide more sensitivity. Ranges from 0-1 with ffmpeg
                            with values from 0.1-0.4 recommended. Ranges from 1-100 with pyscenedetect with
                            values of around 35 recommended. (default: 0.3)

    scenes                  Path: Path to file with scenes timestamps. If existing file
                            specified and split_method is file, acts as alternative split
                            method. Needed for file splitting.
                            Otherwise csv file will be generated with splits data.
                            (default: None)

    time_split_interval     int: If using regular interval splitting, split every
                            n frames. (default: 240)
                            Example: imagine a 950 frame video, 'time_split_interval': 200
                            will split into 5 chunks of 0-199,200-399,400-599,600-799,800-949.


<h3 align="center">Target VMAF</h3>

    vmaf_target             float: Vmaf value to target. Supports all except vvc.
                            Setting this will enable target vmaf mode.
                            Requires crf or q mode or whatever equivalent the
                            encoder has and an explicit "default" crf value.
                            
                            
    min_q, max_q            Min,Max Q values limits for Target VMAF
                            If not set by user, encoder default will be used.
                            
    vmaf                    bool: Calculate vmaf after encode is done. showing vmaf values for all frames,
                            mean, 1,25,75 percentile. Invokes "plotvmaffile" callback with results.

    vmaf_path               str: Custom path to libvmaf models. Does NOT need to be set if ffmpeg
                            default path works. Path should point to .pkl file in same folder as
                            .model file. (default: None)

    vmaf_res                str: Optional scaling for vmaf calculation. Should match model resolution
                            vmaf_v0.6.1.pkl is 1920x1080 (by default), vmaf_4k_v0.6.1.pkl is 3840x2160
                            (default: "1920x1080"). Will preserve original aspect ratio

    vmaf_steps              int: Number of probes for interpolation in vmaf calculations.
                            1 and 2 probes have special mechanisms to make them slightly less bad.
                            Optimal is 4-6 probes. Default: 4
    
    vmaf_filter             str: Filter used for vmaf calculation with ffmpeg. Uses filter_complex.
                            (default: None). (example: 'vmaf_filter': "crop=200:1000:0:0")
    
    vmaf_rate               int: Framerate for vmaf testing. Set to 0 to use original video framerate
                            or to any other number to save cpu cycles at the cost of some accuracy
                            (default: 4)
    
    n_threads               Limit number of threads that used for vmaf calculation
                            (default: None) - Default has no thread limit for vmaf calculations


Register callbacks with ease using the built in callbacks tool:

    def run_on_newframes(frames):
        print("We just transcoded an extra " + frames + " frames")
        # TODO: add code here

    from parallelencode import Callbacks
    from parallelencode import run
    c = Callbacks()
    c.subscribe("newframes", run_on_newframes)
    params = {"input": Path("input.mp4")}
    run(params, run_on_log)
    


<h2 align="center">Main Features</h2>

**Spliting video by scenes for parallel encoding** because all encoders are currently not as good at multithreading as amd is at making threads, encoding is often limited to a few threads at the same time.

*  [PySceneDetect](https://pyscenedetect.readthedocs.io/en/latest/) used for spliting video by scenes and running multiple encoders.
*  Fastest way to transcode video into lossy formats.
*  Target VMAF mode. Saves tons of bitrate while generating good looking video.
*  Resuming encoding without loss of encoded progress.
*  Easy to use.
*  Automatic detection of the number of workers the host can handle.
*  Building encoding queue with bigger files first, minimizing waiting for the last scene to encode.
*  Supports audio transcoding through FFmpeg.

## Install

* Prerequisites:
  *  [Install Python3](https://www.python.org/downloads/) <br>
When installing under Windows, select the option `add Python to PATH` in the installer
  *  [Install FFmpeg](https://ffmpeg.org/download.html)
* At least one of these encoders:
  *  [Install AOMENC](https://aomedia.googlesource.com/aom/)
  *  [Install rav1e](https://github.com/xiph/rav1e)
  *  [Install vpx](https://chromium.googlesource.com/webm/libvpx/) VP9, VP8 encoding
* Optional:
  * [Vapoursynth](http://www.vapoursynth.com/)
  * [ffms2](https://github.com/FFMS/ffms2) 
  * [lsmash](https://github.com/VFR-maniac/L-SMASH-Works)
  * [mkvmerge](https://mkvtoolnix.download/)

* With a package manager:
  *  [pip](https://pypi.org/project/parallelencode/)

* Manually:
  *  Clone Repo or Download from Releases
  *  `pip3 install -r requirements.txt`
  *  `python setup.py install`
