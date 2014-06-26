from Persistence import PersistentMapping
from ftw.simplelayout import _
from ftw.simplelayout.interfaces import IBlockProperties
from zope.annotation import IAnnotations
from zope.interface import implements


BLOCK_PROPERTIES_KEY = 'ftw.simplelayout.block_properites'


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


class MultiViewBlockProperties(object):
    """Block properites adapter for blocks where the user can choose from
    multiple views.
    """

    implements(IBlockProperties)

    available_views = (
        {'name': 'block_view',
         'label': _(u'view_label_block_view',
                    default=u'Default block view')}, )

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_current_view_name(self):
        return self.get_storage().get('view-name', 'block_view')

    def get_available_views(self):
        return self.available_views

    def set_view(self, name):
        if not self.is_view_available(name):
            raise ValueError('"unkown-view" is not in available views.')

        self.get_storage()['view-name'] = name

    def get_storage(self):
        annotations = IAnnotations(self.context)
        if BLOCK_PROPERTIES_KEY not in annotations:
            annotations[BLOCK_PROPERTIES_KEY] = PersistentMapping()

        return annotations[BLOCK_PROPERTIES_KEY]

    def is_view_available(self, name):
        for view in self.get_available_views():
            if view.get('name', None) == name:
                return True

        return False
