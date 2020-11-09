<h1 align="center">
    <br>
    PyParallelEncode
    </br>
</h1>

<h2 align="center">Framework to split and encode videos</h2>

<h4 align="center">
</h4>
<h2 align="center">Easy, powerful, all-in-one encoding based on Av1an</h2>

Output to AV1 / VVC / HEVC / H264 / VP9 / VP8. Input from all formats supported by ffmpeg.

Encoders supported: AOM, RAV1E, SVT-AV1, VTM, x265, x264, SVT-VP9, VPX.

Python example with default parameters:

    from pathlib import Path
    from parallelencode import run
    params = {"input": Path("input.mp4")}
    run(params)

<h2 align="center">Parameters</h2>

    input                   Path: Input file (default: None) Required

    output_file             Path: output file to create (default: (input file name)_(encoder).mkv)
                            Recommended to end with .mkv to avoid errors.

    encoder                 str: Encoder to use 
                            (`aom`,`rav1e`,`svt_av1`,`svt_vp9`,`vpx`,`x265`, `x264`,`vvc`)
                            (default: "aom")

    video_params            list[str]: Strongly recommended to use shlex.split to generate
                            from a string.
                            (If not set, default encoder parameters will be used.)
                            (Example: 'video_params': shlex.split("--rt -t 12 --kf-max-dist=240")

    passes                  int: Number of passes for encoding. most encoders only support 1/2
                            (Default: AOMENC: 2, rav1e: 1, SVT-AV1: 1, SVT-VP9: 1, 
                            VPX: 2, x265: 1, x264: 1, VVC:1)

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
                            (`pyscene`, `aom_keyframes`, `file`, `none`) (default: 'pyscene')
                            `pyscene` - PyScenedetect, content based scenedetection
                            with threshold.
                            `aom_keyframes` - using stat file of 1 pass of aomenc encode
                            to get exact place where encoder will place new keyframes.
                            `file` - read from file specified by 'scenes'
                            (NOT recommended unless using aom encoder)
                            (Keep in mind that speed also depends on set aomenc parameters)

    chunk_method            str: How chunks are made for encoding.
                            ('hybrid', 'select', 'vs_ffms2', 'vs_lsmash')
                            (default: 'hybrid') vs_ffms2 is probably best but also beta

    threshold               float: PySceneDetect threshold for scene detection. Larger
                            values make it less sensitive, splitting less (default: 35.)

    scenes                  Path: Path to file with scenes timestamps. If existing file
                            specified and split_method is file, acts as alternative split
                            method. 
                            Otherwise csv file will be generated with splits data.
                            (default: None)

    extra_split             int: Adding extra splits if frame distance beetween splits bigger than
                            given value. (default: None)
                            Example: imagine a 1000 frame scene, 'extra_split': 200
                            will add splits at 200,400,600,800.


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
  *  [Install SVT-AV1](https://github.com/OpenVisualCloud/SVT-AV1)
  *  [Install SVT-VP9](https://github.com/OpenVisualCloud/SVT-VP9)
  *  [Install vpx](https://chromium.googlesource.com/webm/libvpx/) VP9, VP8 encoding
  *  [Install VTM](https://vcgit.hhi.fraunhofer.de/jvet/VVCSoftware_VTM) VVC encoding test model
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
