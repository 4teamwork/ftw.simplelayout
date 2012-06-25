# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from zope.interface import Interface


class ISimplelayout(Interface):
    """Marker for Simplelayout content pages"""


class ISimplelayoutView(Interface):
    """@@simplelayout view interface.
    """


class IBlockProperties(Interface):
    """Adapter for getting and setting information such as the current
    selected view for the block or the available views.
    """

    def __init__(context, request):
        """Adapts context and request.
        """

    def get_current_view_name():
        """Returns the name of the simplelayout view for displaying the
        context.
        """

    def get_available_views():
        """Returns a list of available views. Each element contains the
        viewname and a human readable title
        """

    def set_view(name):
        """Sets the current view of the context to ``name``.
        """


class IDisplaySettings(Interface):
    """Adapter for storing display settings on a blockish object.
    """

    def __init__(context, request):
        """Adapts context and request.
        """

    def set_position(position):
        """Sets the position of the object.

        Arguments:
        position -- dict with "top" and "left" keys.
        """

    def get_position():
        """Returns the stored position information as dict with "top" and
        "left".
        Returns ``None`` when nothing is stored.
        """

    def set_size(size):
        """Sets the size of the object.

        Arguments:
        size -- dict with "width" and "height" keys.
        """

    def get_size():
        """Returns the stored size information as dict with "width" and
        "height".
        Returns ``None`` when nothing is stored.
        """
