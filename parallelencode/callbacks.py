
class Callbacks(object):
    def __init__(self):
        # All callbacks pass back the name as their first argument if assigned a name. this is done so that
        # a program can distinguish between callbacks it registers.
        #
        # log - Called when logging is requested - str: message to log
        #
        # newtask - Called whenever task changes
        # str: Current pc task name - int: total datums to complete task (eg frames, percent, etc)
        #
        # newframes - Called when new frames are rendered - int: Number of completed frames since last call.
        # eg if there were 4 frames done before and now 7 frames, this will pass 3.
        #
        # terminate - Called when task fails or when complete - int: 0 if success, otherwise error code.
        #
        # plotvmaf - Called when vmaf is calculated so frontend can do plots - int: target vmaf - int: min_q
        # int: max_q - path: tempdir - List[Tuple[Float, Int]]: plot data - str: name of chunk - int: number of frames
        #
        # startencode - Called when encode starts - int: total frames - int: start frames
        #
        # plotvmaffile - Called when vmaf file ready to be plotted - Path: input file - Path: expected output file
        self.subscriptions = {'log': {}, 'newtask': {}, 'newframes': {}, 'terminate': {}, 'plotvmaf': {},
                              'startencode': {}, 'plotvmaffile': {}}

    def subscribe(self, hook, function, name=""):
        if len(name) > 0:
            self.subscriptions[hook][name] = [function, name]
        else:
            self.subscriptions[hook][function.__name__] = function

    def unsubscribe(self, hook, function, name=""):
        if len(name) > 0:
            del(self.subscriptions[hook][name])
        else:
            del(self.subscriptions[hook][function.__name__])

    def run_callback(self, hook, *args):
        for key in self.subscriptions[hook]:
            v = self.subscriptions[hook][key]
            if isinstance(v, list):
                v[0](v[1], *args)
            else:
                v(*args)
