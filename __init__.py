# -*- coding: utf-8 -*-
"""
/***************************************************************************
 manual_sec_builder
                                 A QGIS plugin
 tool for building routes
                             -------------------
        begin                : 2019-07-23
        copyright            : (C) 2019 by drew
        email                : drew.bennett@ptsinternational.co.uk
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load manual_sec_builder class from file manual_sec_builder.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .manual_sec_builder import manual_sec_builder
    return manual_sec_builder(iface)
