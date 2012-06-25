from ftw.simplelayout.interfaces import IBlockProperties
from zope.interface import implements


class SingleViewBlockProperties(object):
    """Block properties adapter for blocks which only support one single
    view and do not support selecting other view.

    The default view name is "block_view".
    """

    implements(IBlockProperties)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_current_view_name(self):
        return 'block_view'

    def get_available_views(self):
        return None

    def set_view(self, name):
        raise RuntimeError('SingleViewBlockProperties adapter does not '
                           'support setting the view.')
