# -*- coding: UTF-8 -*-
"""
Name: filter_crop.py
Porpose: Show dialog to get video crop values based on FFmpeg syntax
Compatibility: Python3, wxPython Phoenix
Author: Gianluca Pernigotto <jeanlucperni@gmail.com>
Copyleft - 2023 Gianluca Pernigotto <jeanlucperni@gmail.com>
license: GPL3
Rev: Feb.20.2023
Code checker: flake8, pylint

This file is part of Videomass.

   Videomass is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   Videomass is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Videomass.  If not, see <http://www.gnu.org/licenses/>.
"""
import os
import wx
# import wx.lib.masked as masked  # does not work on macOSX
import wx.lib.statbmp
from videomass.vdms_threads.generic_task import FFmpegGenericTask
from videomass.vdms_utils.utils import get_milliseconds
from videomass.vdms_utils.utils import milliseconds2clocksec


def make_bitmap(width, height, image):
    """
    Resize the image to the given size and convert it to a
    bitmap object.

    Returns a wx.Bitmap object

    """
    bitmap = wx.Bitmap(image)
    img = bitmap.ConvertToImage()
    img = img.Scale(int(width), int(height), wx.IMAGE_QUALITY_NORMAL)
    bmp = img.ConvertToBitmap()

    return wx.Bitmap(bmp)


class Actor(wx.lib.statbmp.GenStaticBitmap):
    """
    From an explanation by Robin Dunn, where he discusses
    how to rotate images with DC:
    <https://discuss.wxpython.org/t/questions-about-rotation/34064>

    Actor uses the GenStaticBitmap which is a generic implementation
    of wx.StaticBitmap, for display larger images portably.

    This class is useful for drawing a selection rectangle on the image
    given a position specified by the X and Y coordinates and the size
    by the W (width) and H (height) lines.

    """
    def __init__(self, parent, bitmap, idNum, imgFile, **kwargs):
        """
        Attributes defines the rectangle dimensions and coordinates,
        a parent and a current_bmp. First make sure you scale the
        image to fit on parent, e.g. a panel.
        """
        self.h = 0  # rectangle height
        self.w = 0  # rectangle width
        self.x = 0  # rectangle x axis
        self.y = 0  # rectangle y axis

        wx.lib.statbmp.GenStaticBitmap.__init__(self, parent, -1,
                                                bitmap, **kwargs)
        self.parent = parent  # if needed
        self.current_bmp = bitmap

        self.Bind(wx.EVT_PAINT, self.OnPaint)
    # ------------------------------------------------------------------#

    def OnPaint(self, event=None):
        """
        When instantiating the Actor class, this event is
        executed last.

        """
        dc = wx.PaintDC(self)  # draw window boundary
        dc.DrawBitmap(self.current_bmp, 0, 0, True)
        dc.SetPen(wx.Pen('red', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('green', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(int(self.x + 1),
                         int(self.y + 1),
                         int(self.w + 2),
                         int(self.h + 2),
                         )
    # ------------------------------------------------------------------#

    def onRedraw(self, x, y, w, h):
        """
        Update Drawing: A transparent background rectangle in a
        bitmap object. To compensate for the PEN thickness offset,
        the sizes are increased by 2 and the positions decreased
        by 1 (even on OnPaint)

        NOTE dc.SetBrush(wx.Brush(wx.Colour(30, 30, 30, 128))) would set
        a useful transparent gradation color but it doesn't work on windows
        and gtk2.

        """
        self.h, self.w, self.x, self.y = h, w, x, y
        dc = wx.ClientDC(self)
        dc.Clear()  # needed if image has trasparences
        dc.DrawBitmap(self.current_bmp, 0, 0, True)
        dc.SetPen(wx.Pen('red', 2, wx.PENSTYLE_SOLID))
        dc.SetBrush(wx.Brush('green', wx.BRUSHSTYLE_TRANSPARENT))
        dc.DrawRectangle(int(self.x + 1),
                         int(self.y + 1),
                         int(self.w + 2),
                         int(self.h + 2),
                         )


class Crop(wx.Dialog):
    """
    A dialog tool to get video crop values based on FFmpeg syntax.
    See ``av_conversions.py`` -> ``on_Set_crop`` method for
    how to use this class.
    """
    get = wx.GetApp()
    OS = get.appset['ostype']
    TMPROOT = os.path.join(get.appset['cachedir'], 'tmp', 'Crop')
    TMPSRC = os.path.join(TMPROOT, 'tmpsrc')
    os.makedirs(TMPSRC, mode=0o777, exist_ok=True)
    BACKGROUND = '#1b0413'
    # ------------------------------------------------------------------#

    def __init__(self, parent, fcrop, v_width,
                 v_height, fname, timeformat):
        """
        Attributes defined here:

            self.width_dc   width size for DC (aka monitor width)
            self.height_dc   height size for DC (aka monitor height)
            self.x_dc       horizontal axis for DC
            self.y_dc       vertical axis for DC
            self.v_height   height of the source video
            self.v_width    width of the source video
            self.thr        threshold for set aspect ratio
            self.h_ratio    height ratio
            self.w_ratio    width ratio

        The images (also the panel and the DC) are resized keeping
        the aspect ratio according to a threshold established at 360
        pixels or at 180 pixels. 180 pixels are needed to avoid oversizing
        when video height is greater than width.

        """
        # cropping values for monitor preview
        self.width_dc = 0
        self.height_dc = 0
        self.y_dc = 0
        self.x_dc = 0
        # current video size
        self.v_width = v_width
        self.v_height = v_height
        # resizing values preserving aspect ratio for monitor
        self.thr = 180 if self.v_height >= self.v_width else 270
        self.h_ratio = int((self.v_height
                            / self.v_width) * self.thr)  # height
        self.w_ratio = int((self.v_width
                            / self.v_height) * self.h_ratio)  # width
        self.video = fname  # selected filename on queued list
        name = os.path.splitext(os.path.basename(self.video))[0]
        self.frame = os.path.join(f'{Crop.TMPSRC}', f'{name}.png')  # image
        self.filetime = os.path.join(Crop.TMPROOT, f'{name}.clock')
        if os.path.exists(self.filetime):
            with open(self.filetime, "r", encoding='utf8') as atime:
                self.clock = atime.read().strip()
        else:
            self.clock = '00:00:00'

        if os.path.exists(self.frame):
            self.image = self.frame
        else:  # make empty
            self.image = wx.Bitmap(self.w_ratio, self.h_ratio)

        wx.Dialog.__init__(self, parent, -1, style=wx.DEFAULT_DIALOG_STYLE)
        sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.panelrect = wx.Panel(self, wx.ID_ANY,
                                  size=(self.w_ratio, self.h_ratio)
                                  )
        bmp = make_bitmap(self.w_ratio, self.h_ratio, self.image)
        self.bob = Actor(self.panelrect, bmp, 1, "")
        sizerBase.Add(self.panelrect, 0, wx.ALL | wx.CENTER, 5)
        sizersize = wx.BoxSizer(wx.VERTICAL)
        sizerBase.Add(sizersize, 0, wx.ALL | wx.CENTER, 5)
        msg = _("Source size: {0} x {1} pixels").format(self.v_width,
                                                        self.v_height)
        label1 = wx.StaticText(self, wx.ID_ANY, msg)
        sizersize.Add(label1, 0, wx.CENTER)
        msg = _("Search for a specific frame")
        sizer_load = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, (msg)),
                                       wx.HORIZONTAL)
        sizerBase.Add(sizer_load, 0, wx.ALL | wx.EXPAND, 5)
        self.slider = wx.Slider(self, wx.ID_ANY,
                                get_milliseconds(self.clock),
                                0,
                                get_milliseconds(timeformat),
                                size=(250, -1),
                                style=wx.SL_HORIZONTAL,
                                )
        sizer_load.Add(self.slider, 0, wx.ALL | wx.CENTER, 5)
        self.txttime = wx.StaticText(self, wx.ID_ANY, self.clock)
        sizer_load.Add(self.txttime, 0, wx.ALL | wx.CENTER, 10)
        self.btn_load = wx.Button(self, wx.ID_ANY, _("Load"))
        self.btn_load.Disable()
        sizer_load.Add(self.btn_load, 1, wx.ALL | wx.EXPAND, 10)
        boxs = wx.StaticBox(self, wx.ID_ANY, (_("Cropping area selection ")))
        sizerLabel = wx.StaticBoxSizer(boxs, wx.VERTICAL)
        sizerBase.Add(sizerLabel, 0, wx.ALL | wx.EXPAND, 5)
        boxctrl = wx.BoxSizer(wx.VERTICAL)
        sizerLabel.Add(boxctrl, 0, wx.CENTRE)
        label_height = wx.StaticText(self, wx.ID_ANY, (_("Height")))
        boxctrl.Add(label_height, 0, wx.ALL | wx.CENTRE, 0)
        self.crop_height = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                       min=0, max=self.v_height, size=(-1, -1),
                                       style=wx.TE_PROCESS_ENTER
                                       | wx.SP_ARROW_KEYS
                                       )
        boxctrl.Add(self.crop_height, 0, wx.CENTRE)
        grid_sizerBase = wx.FlexGridSizer(1, 5, 0, 0)
        boxctrl.Add(grid_sizerBase, 0, wx.CENTRE, 0)
        label_X = wx.StaticText(self, wx.ID_ANY, ("X"))
        grid_sizerBase.Add(label_X, 0, wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        self.axis_X = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                  min=-1, max=self.v_width, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  | wx.SP_ARROW_KEYS
                                  )
        grid_sizerBase.Add(self.axis_X, 0, wx.ALL | wx.CENTRE, 5)

        self.btn_centre = wx.Button(self, wx.ID_ANY, _("Center"))
        grid_sizerBase.Add(self.btn_centre, 0, wx.ALL
                           | wx.ALIGN_CENTER_VERTICAL, 5)
        self.crop_width = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                      min=0, max=self.v_width,
                                      size=(-1, -1),
                                      style=wx.TE_PROCESS_ENTER
                                      | wx.SP_ARROW_KEYS
                                      )
        grid_sizerBase.Add(self.crop_width, 0, wx.ALL | wx.CENTRE, 5)

        label_width = wx.StaticText(self, wx.ID_ANY, (_("Width")))
        grid_sizerBase.Add(label_width, 0, wx.RIGHT
                           | wx.ALIGN_CENTER_VERTICAL, 5)
        self.axis_Y = wx.SpinCtrl(self, wx.ID_ANY, "0",
                                  min=-1, max=self.v_height, size=(-1, -1),
                                  style=wx.TE_PROCESS_ENTER
                                  | wx.SP_ARROW_KEYS
                                  )
        boxctrl.Add(self.axis_Y, 0, wx.CENTRE)
        label_Y = wx.StaticText(self, wx.ID_ANY, ("Y"))
        boxctrl.Add(label_Y, 0, wx.BOTTOM | wx.CENTRE, 5)
        # bottom layout for buttons
        gridBtn = wx.GridSizer(1, 2, 0, 0)
        gridexit = wx.BoxSizer(wx.HORIZONTAL)
        btn_reset = wx.Button(self, wx.ID_CLEAR, _("Reset"))
        gridBtn.Add(btn_reset, 0, wx.ALL, 5)
        btn_close = wx.Button(self, wx.ID_CANCEL, "")
        gridexit.Add(btn_close, 0, wx.ALL, 5)
        self.btn_ok = wx.Button(self, wx.ID_OK, _("Apply"))
        gridexit.Add(self.btn_ok, 0, wx.ALL, 5)
        gridBtn.Add(gridexit, 0, wx.ALL | wx.ALIGN_RIGHT | wx.RIGHT, 0)
        sizerBase.Add(gridBtn, 0, wx.EXPAND)

        self.SetSizer(sizerBase)
        sizerBase.Fit(self)
        self.Layout()
        # ----------------------Properties-----------------------#
        self.panelrect.SetBackgroundColour(wx.Colour(Crop.BACKGROUND))
        if Crop.OS == 'Darwin':
            label1.SetFont(wx.Font(11, wx.SWISS, wx.NORMAL, wx.NORMAL))
        else:
            label1.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL))

        self.SetTitle(_("Crop Filter"))
        self.crop_width.SetToolTip(_('Crop to width'))
        self.axis_Y.SetToolTip(_('Move vertically - set to -1 to center '
                                 'the vertical axis'))
        self.axis_X.SetToolTip(_('Move horizontally - set to -1 to center '
                                 'the horizontal axis'))
        self.crop_height.SetToolTip(_('Crop to height'))

        # ----------------------Binding (EVT)------------------------#
        self.Bind(wx.EVT_SPINCTRL, self.onWidth, self.crop_width)
        self.Bind(wx.EVT_SPINCTRL, self.onHeight, self.crop_height)
        self.Bind(wx.EVT_SPINCTRL, self.onX, self.axis_X)
        self.Bind(wx.EVT_SPINCTRL, self.onY, self.axis_Y)
        self.Bind(wx.EVT_BUTTON, self.onCentre, self.btn_centre)
        self.Bind(wx.EVT_COMMAND_SCROLL, self.on_Seek, self.slider)
        self.Bind(wx.EVT_BUTTON, self.image_loader, self.btn_load)

        self.Bind(wx.EVT_BUTTON, self.on_close, btn_close)
        self.Bind(wx.EVT_BUTTON, self.on_ok, self.btn_ok)
        self.Bind(wx.EVT_BUTTON, self.on_reset, btn_reset)
        # self.Bind(wx.EVT_BUTTON, self.on_help, btn_help)

        if timeformat == '00:00:00.000':
            self.slider.Disable()
        if not os.path.exists(self.frame):
            self.image_loader(self)

        if fcrop:  # previusly values
            self.default(fcrop)
    # ------------------------------------------------------------------#

    def default(self, fcrop):
        """
        Set controls to previous settings

        """
        s = fcrop.split(':')
        s[0] = s[0][5:]  # removing `crop=` word on first item
        self.crop_width.SetValue(int(s[0][2:]))
        self.crop_height.SetValue(int(s[1][2:]))

        x, y = None, None
        for i in s:
            if i.startswith('x'):
                x = i[2:]
            if i.startswith('y'):
                y = i[2:]
        if x:
            self.axis_X.SetValue(int(x))
        else:
            self.axis_X.SetValue(-1)

        if y:
            self.axis_Y.SetValue(int(y))
        else:
            self.axis_Y.SetValue(-1)

        self.onWidth(self)  # set min/max horizontal axis
        self.onHeight(self)  # set min/max vertical axis
    # ------------------------------------------------------------------#

    def on_Seek(self, event):
        """
        gets value from time slider, converts it to clock format
        e.g (00:00:00), and sets the label with the converted value.
        """
        seek = self.slider.GetValue()
        clock = milliseconds2clocksec(seek, rounds=True)  # to 24-hour
        self.txttime.SetLabel(clock)  # update StaticText
        if not self.btn_load.IsEnabled():
            self.btn_load.Enable()
    # ------------------------------------------------------------------#

    def image_loader(self, event):
        """
        Load in a wx.dc (device context) image frame
        at a given time clock point

        """
        seek = self.slider.GetValue()
        self.clock = milliseconds2clocksec(seek, rounds=True)  # to 24-hour
        arg = (f'-ss {self.clock} -i "{self.video}" '
               f'-vframes 1 -y "{self.frame}"'
               )
        thread = FFmpegGenericTask(arg)
        thread.join()  # wait end thread
        error = thread.status
        if error:
            wx.MessageBox(f'{error}', 'ERROR', wx.ICON_ERROR)
            return
        with open(self.filetime, "w", encoding='utf8') as atime:
            atime.write(self.clock)
        self.btn_load.Disable()
        self.image = self.frame  # update with new frame
        bmp = make_bitmap(self.w_ratio, self.h_ratio, self.image)
        self.bob.current_bmp = bmp
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onDrawing(self):
        """
        Updating computation and call onRedraw to update
        rectangle position of the bob actor

        """
        h_crop = self.crop_height.GetValue()
        w_crop = self.crop_width.GetValue()
        x_crop = self.axis_X.GetValue()
        y_crop = self.axis_Y.GetValue()

        self.height_dc = (h_crop / self.v_width) * self.thr
        self.width_dc = (w_crop / self.v_height) * self.h_ratio

        if y_crop == -1:
            self.y_dc = (self.h_ratio / 2) - (self.height_dc / 2)
        else:
            self.y_dc = (y_crop / self.v_width) * self.thr

        if x_crop == -1:
            self.x_dc = (self.thr / 2) - (self.width_dc / 2)
        else:
            self.x_dc = (x_crop / self.v_height) * self.h_ratio

        self.bob.onRedraw(self.x_dc,
                          self.y_dc,
                          self.width_dc,
                          self.height_dc,
                          )
    # ------------------------------------------------------------------#

    def onWidth(self, event):
        """
        Sets the limit to the minimum and maximum values for the
        horizontal X axis in relation to the values set for the
        width of the crop.
        If the maximum allowed value is set to the width of the crop,
        the X axis will be set to `min, max = 0, 0` i.e. disabled.

        The maximum allowed value for the width of the crop is
        established in the `self.v_width` attribute

        """
        if self.crop_width.GetValue() == self.v_width:
            self.axis_X.SetMax(0)
            self.axis_X.SetMin(0)
        else:
            self.axis_X.SetMax(self.v_width - self.crop_width.GetValue())
            self.axis_X.SetMin(-1)

        self.onDrawing()
    # ------------------------------------------------------------------#

    def onHeight(self, event):
        """
        Sets the limit to the minimum and maximum values for the
        vertical Y axis in relation to the values set for the
        height of the crop.
        If the maximum allowed value is set to the height of the crop,
        the Y axis will be set to `min, max = 0, 0` i.e. disabled.

        The maximum allowed value for the height of the crop is
        established in the `self.v_height` attribute

        """
        if self.crop_height.GetValue() == self.v_height:
            self.axis_Y.SetMax(0), self.axis_Y.SetMin(0)
        else:
            self.axis_Y.SetMax(self.v_height - self.crop_height.GetValue())
            self.axis_Y.SetMin(-1)

        self.onDrawing()
    # ------------------------------------------------------------------#

    def onX(self, event):
        """
        self.axis_X callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onY(self, event):
        """
        self.axis_Y callback
        """
        self.onDrawing()
    # ------------------------------------------------------------------#

    def onCentre(self, event):
        """
        Sets coordinates X, Y to center if not `GetMax == 0` .
        `GetMax == 0` means that the maximum size of the crop
        has been setted and the X or Y axes cannot be setted anymore.

        """
        if self.axis_Y.GetMax() != 0:
            self.axis_Y.SetValue(-1)

        if self.axis_X.GetMax() != 0:
            self.axis_X.SetValue(-1)

        if self.axis_Y.GetMax() or self.axis_X.GetMax():
            self.onDrawing()
    # ------------------------------------------------------------------#

    def on_reset(self, event):
        """
        Reset all control values
        """
        self.axis_Y.SetMin(-1)
        self.axis_Y.SetMax(self.v_height)
        self.axis_X.SetMin(-1)
        self.axis_X.SetMax(self.v_width)
        self.crop_width.SetValue(0)
        self.axis_X.SetValue(0)
        self.crop_height.SetValue(0)
        self.axis_Y.SetValue(0)
        self.onDrawing()
    # ------------------------------------------------------------------#

    def on_close(self, event):
        """
        Close this dialog without saving anything
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def on_ok(self, event):
        """
        Don't use self.Destroy() in this dialog
        """
        event.Skip()
    # ------------------------------------------------------------------#

    def getvalue(self):
        """
        This method return values via the interface getvalue()
        by the caller. See the caller for more info and usage.
        Note: -1 for X and Y coordinates means center, which are
        empty values for FFmpeg syntax.
        """
        w = self.crop_width.GetValue()
        h = self.crop_height.GetValue()
        x = self.axis_X.GetValue()
        y = self.axis_Y.GetValue()

        if w and h:
            x_axis = f"x={x if x > -1 else ''}:"
            y_axis = f"y={y if y > -1 else ''}:"
            val = f'w={w}:h={h}:{x_axis}{y_axis}'
            return val[:len(val) - 1]  # remove last ':' string

        return None