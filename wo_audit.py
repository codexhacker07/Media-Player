import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import os

class AudioSeparator:
    """
    Utility that separates the audio and video tracks from
    an input video file.
    """
    def __init__(self):
        self.use_parse_launch = False
        self.decodebin = None
        self.error_msg = ''
        # Replace these paths with appropriate file paths on your
        # machine.
        self.inFileLocation="/root/Downloads/2.mp4"
        self.audioOutLocation="/root/1.mp3"
        self.videoOutLocation="/root/2.mp4"

        self.constructPipeline()
        self.is_playing = False
        self.connectSignals()

    def constructPipeline(self):
        """
        Create the pipeline, add and link elements.
        """
        # Create the pipeline instance
        self.player = gst.Pipeline()

        # Define pipeline elements
        self.filesrc = gst.element_factory_make("filesrc")

        self.filesrc.set_property("location", self.inFileLocation)

        self.decodebin = gst.element_factory_make("decodebin")

        self.autoconvert = gst.element_factory_make("autoconvert")

        self.audioconvert = gst.element_factory_make("audioconvert")
        self.audioresample = gst.element_factory_make("audioresample")
        self.audio_encoder = gst.element_factory_make("lame")
        self.audiosink = gst.element_factory_make("filesink")
        self.audiosink.set_property("location", self.audioOutLocation)

        self.video_encoder = gst.element_factory_make("ffenc_mpeg4")
        self.muxer = gst.element_factory_make("ffmux_mp4")

        self.videosink = gst.element_factory_make("filesink")
        self.videosink.set_property("location", self.videoOutLocation)

        self.queue1 = gst.element_factory_make("queue")
        self.queue2 = gst.element_factory_make("queue")
        self.queue3 = gst.element_factory_make("queue")

        # Add elements to the pipeline
        self.player.add(self.filesrc,
                        self.decodebin,
                        self.queue1,
                        self.autoconvert,
                        self.video_encoder,
                        self.muxer,
                        self.videosink,
                        self.queue2,
                        self.audioconvert,
                        self.audio_encoder,
                        self.audiosink,
                        self.queue3
                        )

        # Link elements in the pipeline.
        gst.element_link_many(self.filesrc, self.decodebin)

        gst.element_link_many(self.queue1,
                              self.autoconvert,
                              self.video_encoder,
                              self.muxer,
                              self.videosink)

        gst.element_link_many(self.queue2,
                              self.audioconvert,
                              self.audio_encoder,
                              self.audiosink)

    def connectSignals(self):
        """
        Connects signals with the methods.
        """
        # Capture the messages put on the bus.
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.message_handler)

        # Connect the decodebin signal
        if not self.decodebin is None:
            self.decodebin.connect("pad_added", self.decodebin_pad_added)

    def decodebin_pad_added(self, decodebin, pad):
        """
        Manually link the decodebin pad with a compatible pad on
        queue elements, when the decodebin element generated "pad_added" signal
        """
        compatible_pad = None
        caps = pad.get_caps()
        name = caps[0].get_name()
        print "\n cap name is = ", name
        if name[:5] == 'video':
            compatible_pad = self.queue1.get_compatible_pad(pad, caps)
        elif name[:5] == 'audio':
            compatible_pad = self.queue2.get_compatible_pad(pad, caps)

        if compatible_pad:
            pad.link(compatible_pad)


    def play(self):
        """
        Start streaming the media.
        @see: self.constructPipeline() which defines a
        pipeline that does the job of separating audio and
        video tracks.
        """
        starttime = time.clock()

        self.is_playing = True
        self.player.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
        endtime = time.clock()
        self.printFinalStatus(starttime, endtime)
        evt_loop.quit()

    def message_handler(self, bus, message):
        """
        Capture the messages on the bus and
        set the appropriate flag.
        """
        msgType = message.type
        if msgType == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False
            self.error_msg =  message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

    def printFinalStatus(self, starttime, endtime):
        """
        Print the final status message.
        """

        if self.error_msg:
            print self.error_msg
        else:
            print "\n Done!"
            print "\n Audio and video tracks separated and saved as "\
            "following files"
            print "\n audio:%s \n video:%s"%(self.audioOutLocation,
                                            self.videoOutLocation)
            print "\n Approximate time required :  \
            %.4f seconds" % (endtime - starttime)

# Run the program
player = AudioSeparator()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()

