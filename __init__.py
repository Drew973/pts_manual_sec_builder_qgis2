# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load manual_sec_builder class from file manual_sec_builder.

    :param iface: A QGIS interface instance.
    :type iface: QgisInterface
    """
    #
    from .manual_sec_builder import manual_sec_builder#class
    return manual_sec_builder(iface)
