#!/usr/bin/python3
# alt_az.py
# -*- coding: utf-8 -*-
#
# The python script in this file makes the various parts of a model planisphere.
#
# Copyright (C) 2014-2019 Dominic Ford <dcf21-www@dcford.org.uk>
#
# This code is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# You should have received a copy of the GNU General Public License along with
# this file; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA  02110-1301, USA

# ----------------------------------------------------------------------------

"""
Render the optional alt-az grid of the planisphere.
"""

from math import atan2

from constants import unit_deg, unit_rev, unit_mm, central_hole_size, r_1
from constants import radius, transform, pos
from graphics_context import BaseComponent
from numpy import arange
from settings import fetch_command_line_arguments
from text import text


class AltAzGrid(BaseComponent):
    """
    Render the optional alt-az grid of the planisphere.
    """

    def default_filename(self):
        """
        Return the default filename to use when saving this component.
        """
        return "alt_az_grid"

    def bounding_box(self, settings):
        """
        Return the bounding box of the canvas area used by this component.

        :param settings:
            A dictionary of settings required by the renderer.
        :return:
         Dictionary with the elements 'x_min', 'x_max', 'y_min' and 'y_max' set
        """

        latitude = abs(settings['latitude'])

        bounding_box = {
            'x_min': 0,
            'x_max': 0,
            'y_min': 0,
            'y_max': 0
        }

        # Trace around horizon, keeping track of minimum and maximum coordinates
        alt = -12
        path = [transform(alt=alt, az=az, latitude=latitude) for az in arange(0, 360.5, 1)]

        for p in path:
            r_b = radius(dec=p[1] / unit_deg, latitude=latitude)
            p = pos(r_b, p[0])
            bounding_box['x_min'] = min(bounding_box['x_min'], p['x'])
            bounding_box['x_max'] = max(bounding_box['x_max'], p['x'])
            bounding_box['y_min'] = min(bounding_box['y_min'], p['y'])
            bounding_box['y_max'] = max(bounding_box['y_max'], p['y'])

        return bounding_box

    def do_rendering(self, settings, context):
        """
        This method is required to actually render this item.

        :param settings:
            A dictionary of settings required by the renderer.
        :param context:
            A GraphicsContext object to use for drawing
        :return:
            None
        """

        latitude = abs(settings['latitude'])
        language = settings['language']

        context.set_font_size(0.9)

        # Draw horizon, and line to cut around edge
        for alt in (-10, 0):
            path = [transform(alt=alt, az=az, latitude=latitude) for az in arange(0, 360.5, 1)]

            context.begin_path()
            for i, p in enumerate(path):
                r_b = radius(dec=p[1] / unit_deg, latitude=latitude)
                if i == 0:
                    context.move_to(**pos(r_b, p[0]))
                else:
                    context.line_to(**pos(r_b, p[0]))
            context.stroke()

            if alt == -10:
                # Create clipping area, excluding central hole
                context.begin_sub_path()
                context.circle(centre_x=0, centre_y=0, radius=central_hole_size)
                context.stroke()
                context.clip()

        # Draw lines of constant altitude
        context.begin_path()
        for alt in range(10, 85, 10):
            path = [transform(alt=alt, az=az, latitude=latitude) for az in arange(0, 360.5, 1)]
            for i, p in enumerate(path):
                r_b = radius(dec=p[1] / unit_deg, latitude=latitude)
                if i == 0:
                    context.move_to(**pos(r_b, p[0]))
                else:
                    context.line_to(**pos(r_b, p[0]))
        context.stroke(color=(0.5, 0.5, 0.5, 1))

        # Draw lines marking S,SSE,SE,ESE,E, etc
        context.begin_path()
        for az in arange(0, 359, 22.5):
            path = [transform(alt=alt, az=az, latitude=latitude) for alt in arange(0, 90.1, 1)]
            for i, p in enumerate(path):
                r_b = radius(dec=p[1] / unit_deg, latitude=latitude)
                if i == 0:
                    context.move_to(**pos(r_b, p[0]))
                else:
                    context.line_to(**pos(r_b, p[0]))
        context.stroke(color=(0.5, 0.5, 0.5, 1))

        # Gluing labels
        def make_gluing_label(azimuth):
            pp = transform(alt=0, az=azimuth - 0.01, latitude=latitude)
            r = radius(dec=pp[1] / unit_deg, latitude=latitude)
            p = pos(r, pp[0])

            pp2 = transform(alt=0, az=azimuth + 0.01, latitude=latitude)
            r2 = radius(dec=pp2[1] / unit_deg, latitude=latitude)
            p2 = pos(r2, pp2[0])

            p3 = [p2[i] - p[i] for i in ('x', 'y')]
            tr = -unit_rev/4 - atan2(p3[0], p3[1])

            context.text(text=text[language]["glue_here"],
                         x=p['x'], y=p['y'],
                         h_align=0, v_align=1, gap=unit_mm, rotation=tr)

        context.set_font_style(bold=True)
        context.set_color(r=0, g=0, b=0)
        make_gluing_label(azimuth=0)
        make_gluing_label(azimuth=90)
        make_gluing_label(azimuth=180)
        make_gluing_label(azimuth=270)


# Do it right away if we're run as a script
if __name__ == "__main__":
    # Fetch command line arguments passed to us
    arguments = fetch_command_line_arguments(default_filename=AltAzGrid().default_filename())

    # Render the alt-az grid
    AltAzGrid(settings={
        'latitude': arguments['latitude'],
        'language': 'en'
    }).render_to_file(
        filename=arguments['filename'],
        img_format=arguments['img_format']
    )
