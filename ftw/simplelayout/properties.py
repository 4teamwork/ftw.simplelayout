from ftw.simplelayout.interfaces import IBlockProperties
from Persistence import PersistentMapping
from zope.annotation import IAnnotations
from zope.interface import implements


BLOCK_PROPERTIES_KEY = 'ftw.simplelayout.block_properites'


class MultiViewBlockProperties(object):
    """Block properites adapter for blocks where the user can choose from
    multiple views.
    """

    implements(IBlockProperties)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_current_view_name(self):
        return self.get_storage().get('view-name', 'block_view')

    def set_view(self, name):
        if not self.is_view_available(name):
            raise ValueError('"{0}" is not in available views.'.format(name))

        self.get_storage()['view-name'] = name

    def get_storage(self):
        annotations = IAnnotations(self.context)
        if BLOCK_PROPERTIES_KEY not in annotations:
            annotations[BLOCK_PROPERTIES_KEY] = PersistentMapping()

        return annotations[BLOCK_PROPERTIES_KEY]

    def is_view_available(self, name):
        return self.context.restrictedTraverse(name, None) is not None
