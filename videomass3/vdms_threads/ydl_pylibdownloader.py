# -*- coding: UTF-8 -*-

#########################################################
# Name: ydl_pylibrary.py
# Porpose: long processing task with youtube_dl python library
# Compatibility: Python3, wxPython4 Phoenix
# Author: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2018/2020 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Rev: April.06.2020 *PEP8 compatible*
#########################################################
# This file is part of Videomass.

#    Videomass is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Videomass is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Videomass.  If not, see <http://www.gnu.org/licenses/>.

#########################################################
import wx
from threading import Thread
import time
from pubsub import pub

# get videomass wx.App attribute
get = wx.GetApp()
OS = get.OS
DIR_CONF = get.DIRconf  # path to the configuration directory:
FFMPEG_URL = get.FFMPEG_url
pylibYdl = get.pylibYdl

if pylibYdl is None:  # youtube-dl is installed
    import youtube_dl


class MyLogger(object):
    """
    Intercepts youtube-dl's output by setting a logger object;
    * Log messages to a logging.Logger instance.
    https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#embedding-youtube-dl
    """
    def debug(self, msg):
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_FROM_IMPORT_EVT",
                     output=msg,
                     duration='',
                     status='DEBUG',
                     )
        self.msg = msg

    def warning(self, msg):
        msg = 'WARNING: %s' % msg
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_FROM_IMPORT_EVT",
                     output=msg,
                     duration='',
                     status='WARNING',
                     )

    def error(self, msg):
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_FROM_IMPORT_EVT",
                     output=msg,
                     duration='',
                     status='ERROR',
                     )
# -------------------------------------------------------------------------#


def my_hook(d):
    """
    progress_hooks is A list of functions that get called on
    download progress. See  help(youtube_dl.YoutubeDL)
    """
    if d['status'] == 'downloading':
        percent = float(d['_percent_str'].strip().split('%')[0])
        duration = ('Downloading... {} of {} '
                    'at {} ETA {}'.format(d['_percent_str'],
                                          d['_total_bytes_str'],
                                          d['_speed_str'],
                                          d['_eta_str'],),
                    percent
                    )
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_FROM_IMPORT_EVT",
                     output='',
                     duration=duration,
                     status='DOWNLOAD',)

    if d['status'] == 'finished':
        wx.CallAfter(pub.sendMessage,
                     "COUNT_EVT",
                     count='',
                     duration='',
                     fname='',
                     end='ok',
                     )
        wx.CallAfter(pub.sendMessage,
                     "UPDATE_YDL_FROM_IMPORT_EVT",
                     output='',
                     duration='Done downloading, now converting ...',
                     status='FINISHED',
                     )
# -------------------------------------------------------------------------#


class Ydl_DL_Pylib(Thread):
    """
    Embed youtube-dl as module into a separated thread in order
    to get output in real time during downloading and conversion .
    For a list of available options see:

    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/YoutubeDL.py#L129-L279>
    <https://github.com/ytdl-org/youtube-dl/blob/master/youtube_dl/options.py>

    or by help(youtube_dl.YoutubeDL)
    """
    def __init__(self, varargs, logname):
        """
        Attributes defined here:
        self.stop_work_thread:  process terminate value
        self.urls:          urls list
        self.opt:           option dict data type to adding
        self.outputdir:     pathname destination
        self.count:         increases progressive account elements
        self.countmax:      length of self.urls items list
        self.logname:       file name to log messages for logging
        """
        Thread.__init__(self)
        """initialize"""
        self.stop_work_thread = False  # process terminate
        self.urls = varargs[1]
        self.opt = varargs[4]
        self.outputdir = varargs[3]
        self.count = 0
        self.countmax = len(varargs[1])
        self.logname = logname
        if OS == 'Windows':
            self.nocheckcertificate = True
        else:
            self.nocheckcertificate = False

        self.start()  # start the thread (va in self.run())

    def run(self):
        """
        """
        for url in self.urls:
            self.count += 1
            count = 'URL %s/%s' % (self.count, self.countmax,)
            wx.CallAfter(pub.sendMessage,
                         "COUNT_EVT",
                         count=count,
                         duration=100,
                         fname=url,
                         end='',
                         )

            if self.stop_work_thread:
                break

            ydl_opts = {'format': self.opt['format'],
                        'extractaudio': self.opt['format'],
                        'outtmpl': '{}/{}'.format(self.outputdir,
                                                  self.opt['outtmpl']),
                        'writesubtitles': self.opt['writesubtitles'],
                        'addmetadata': self.opt['addmetadata'],
                        'restrictfilenames': True,
                        'ignoreerrors': True,
                        'no_warnings': False,
                        'writethumbnail': self.opt['writethumbnail'],
                        'noplaylist': self.opt['noplaylist'],
                        'no_color': True,
                        'nocheckcertificate': self.nocheckcertificate,
                        'ffmpeg_location': '{}'.format(FFMPEG_URL),
                        'postprocessors': self.opt['postprocessors'],
                        'logger': MyLogger(),
                        'progress_hooks': [my_hook],
                        }

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download(["{}".format(url)])

        wx.CallAfter(pub.sendMessage, "END_EVT")

    def stop(self):
        """
        Sets the stop work thread to terminate the process
        """
        self.stop_work_thread = True
