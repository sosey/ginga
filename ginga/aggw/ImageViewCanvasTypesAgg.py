#
# ImageViewCanvasTypesAgg.py -- drawing classes for ImageViewCanvas widget
#
# Eric Jeschke (eric@naoj.org)
#
# Copyright (c) Eric R. Jeschke.  All rights reserved.
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.

import aggdraw as agg
from . import AggHelp
from itertools import chain

# TODO: this line is for backward compatibility with files importing
# this module--to be removed
from ginga.canvas.CanvasObject import *

class RenderContext(object):

    def __init__(self, viewer):
        self.viewer = viewer

        # TODO: encapsulate this drawable
        self.cr = AggHelp.AggContext(self.viewer.get_surface())

        self.pen = None
        self.brush = None
        self.font = None

    def set_line_from_shape(self, shape):
        # TODO: support line width and style
        alpha = getattr(shape, 'alpha', 1.0)
        self.pen = self.cr.get_pen(shape.color, alpha=alpha)

    def set_fill_from_shape(self, shape):
        fill = getattr(shape, 'fill', False)
        if fill:
            if hasattr(shape, 'fillcolor') and shape.fillcolor:
                color = shape.fillcolor
            else:
                color = shape.color
            alpha = getattr(shape, 'alpha', 1.0)
            alpha = getattr(shape, 'fillalpha', alpha)
            self.brush = self.cr.get_brush(color, alpha=alpha)
        else:
            self.brush = None

    def set_font_from_shape(self, shape):
        if hasattr(shape, 'font'):
            if hasattr(shape, 'fontsize') and shape.fontsize is not None:
                fontsize = shape.fontsize
            else:
                fontsize = shape.scale_font(self.viewer)
            alpha = getattr(shape, 'alpha', 1.0)
            self.font = self.cr.get_font(shape.font, fontsize, shape.color,
                                         alpha=alpha)
        else:
            self.font = None

    def initialize_from_shape(self, shape, line=True, fill=True, font=True):
        if line:
            self.set_line_from_shape(shape)
        if fill:
            self.set_fill_from_shape(shape)
        if font:
            self.set_font_from_shape(shape)

    def set_line(self, color, alpha=1.0, linewidth=1, style='solid'):
        # TODO: support line width and style
        self.pen = self.cr.get_pen(color, alpha=alpha)

    def set_fill(self, color, alpha=1.0):
        if color is None:
            self.brush = None
        else:
            self.brush = self.cr.get_brush(color, alpha=alpha)

    def set_font(self, fontname, fontsize):
        self.font = self.cr.get_font(fontname, fontsize, 'black',
                                     alpha=1.0)

    def text_extents(self, text):
        return self.cr.text_extents(text, self.font)


    ##### DRAWING OPERATIONS #####

    def draw_text(self, cx, cy, text):
        self.cr.canvas.text((cx, cy), text, self.font)

    def draw_polygon(self, cpoints):
        self.cr.canvas.polygon(list(chain.from_iterable(cpoints)),
                               self.pen, self.brush)

    def draw_circle(self, cx, cy, cradius):
        self.cr.canvas.ellipse((cx-cradius, cy-cradius, cx+cradius, cy+cradius),
                               self.pen, self.brush)

    def draw_bezier_curve(self, cp):
        # TODO: currently there is a bug in aggdraw paths
        path = agg.Path()
        path.moveto(cp[0][0], cp[0][1])
        path.curveto(cp[1][0], cp[1][1], cp[2][0], cp[2][1], cp[3][0], cp[3][1])
        self.cr.canvas.path(path.coords(), path, self.pen, self.brush)

    def draw_ellipse_bezier(self, cp):
        # draw 4 bezier curves to make the ellipse
        # TODO: currently there is a bug in aggdraw paths
        path = agg.Path()
        path.moveto(cp[0][0], cp[0][1])
        path.curveto(cp[1][0], cp[1][1], cp[2][0], cp[2][1], cp[3][0], cp[3][1])
        path.curveto(cp[4][0], cp[4][1], cp[5][0], cp[5][1], cp[6][0], cp[6][1])
        path.curveto(cp[7][0], cp[7][1], cp[8][0], cp[8][1], cp[9][0], cp[9][1])
        path.curveto(cp[10][0], cp[10][1], cp[11][0], cp[11][1], cp[12][0], cp[12][1])
        self.cr.canvas.path(path.coords(), path, self.pen, self.brush)

    def draw_line(self, cx1, cy1, cx2, cy2):
        self.cr.canvas.line((cx1, cy1, cx2, cy2), self.pen)

    def draw_path(self, cpoints):
        # TODO: see if the path type in aggdraw can be used for this
        for i in range(len(cpoints) - 1):
            cx1, cy1 = cpoints[i]
            cx2, cy2 = cpoints[i+1]
            self.cr.canvas.line((cx1, cy1, cx2, cy2), self.pen)


class CanvasRenderer(object):

    def __init__(self, viewer):
        self.viewer = viewer

    def setup_cr(self, shape):
        cr = RenderContext(self.viewer)
        cr.initialize_from_shape(shape, font=False)
        return cr

    def get_dimensions(self, shape):
        cr = self.setup_cr(shape)
        cr.set_font_from_shape(shape)
        return cr.text_extents(shape.text)

#END
