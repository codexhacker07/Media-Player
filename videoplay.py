import time
import thread
import gobject
import pygst
pygst.require("0.10")
import gst
import os

class VideoPlayer:
    """
    Simple Video player that just 'plays' a valid input Video file.
    """
    def __init__(self):
        self.use_parse_launch = False
        self.decodebin = None
        self.inFileLocation="root/Downloads/2.mp4"

        self.constructPipeline()
        self.is_playing = False
        self.connectSignals()

    def constructPipeline(self):
        """
        Add and link elements in a GStreamer pipeline.
        """
        # Create the pipeline instance
        self.player = gst.Pipeline()

        # Define pipeline elements
        self.filesrc = gst.element_factory_make("filesrc")
        self.filesrc.set_property("location",
                                  self.inFileLocation)
        self.decodebin = gst.element_factory_make('decodebin')

        # audioconvert for audio processing pipeline
        self.audioconvert = gst.element_factory_make("audioconvert")

        # Autoconvert element for video processing
        self.autoconvert = gst.element_factory_make("autoconvert")

        self.audiosink = gst.element_factory_make("autoaudiosink")

        self.videosink = gst.element_factory_make("autovideosink")

        # As a precaution add videio capability filter
        # in the video processing pipeline.
        videocap = gst.Caps("video/x-raw-yuv")
        self.filter = gst.element_factory_make("capsfilter")
        self.filter.set_property("caps", videocap)
        # Converts the video from one colorspace to another
        self.colorSpace = gst.element_factory_make("ffmpegcolorspace")

        self.queue1 = gst.element_factory_make("queue")
        self.queue2 = gst.element_factory_make("queue")

        # Add elements to the pipeline
        self.player.add(self.filesrc,
                        self.decodebin,
                        self.autoconvert,
                        self.audioconvert,
                        self.queue1,
                        self.queue2,
                        self.filter,
                        self.colorSpace,
                        self.audiosink,
                        self.videosink)

        # Link elements in the pipeline.
        gst.element_link_many(self.filesrc, self.decodebin)
        gst.element_link_many(self.queue1, self.autoconvert,
                              self.filter, self.colorSpace,
                              self.videosink)
        gst.element_link_many(self.queue2, self.audioconvert,
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
        queue elements, when the decodebin "pad-added" signal
        is generated.
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
        Play the media file
        """
        self.is_playing = True
        self.player.set_state(gst.STATE_PLAYING)
        while self.is_playing:
            time.sleep(1)
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
            print "\n Unable to play Video. Error: ", \
            message.parse_error()
        elif msgType == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
            self.is_playing = False

# Run the program
player = VideoPlayer()
thread.start_new_thread(player.play, ())
gobject.threads_init()
evt_loop = gobject.MainLoop()
evt_loop.run()







