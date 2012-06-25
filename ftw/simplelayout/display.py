
from ftw.simplelayout.interfaces import IDisplaySettings
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts
from zope.app.annotation.interfaces import IAttributeAnnotatable
from zope.app.annotation.interfaces import IAnnotations
from Persistence import PersistentMapping

DISPLAY_SETTINGS_KEY = 'ftw.simplelayout.display_settings'


class DisplaySeetings(object):
    """Adapter for storing display settings on a
    blockish object."""

    implements(IDisplaySettings)
    adapts(IAttributeAnnotatable, Interface)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.annotations = IAnnotations(context)

    def get_storage(self):
        if DISPLAY_SETTINGS_KEY not in self.annotations:
            storage = self.annotations[DISPLAY_SETTINGS_KEY] = PersistentMapping()
            storage['position'] = PersistentMapping()
            storage['size'] = PersistentMapping()
            return storage
        return self.annotations[DISPLAY_SETTINGS_KEY]

    def set_position(self, value):
        if 'top' not in value and 'left' not in value:
            raise ValueError('Expected a dict with top and left as key')

        self.get_storage()['position'] = PersistentMapping(value)

    def get_position(self):
        return self.get_storage()['position']

    def set_size(self, value):
        if 'width' not in value and 'height' not in value:
            raise ValueError('Expected a dict with top and left as key')

        self.get_storage()['size'] = PersistentMapping(value)

    def get_size(self):
        return self.get_storage()['size']
