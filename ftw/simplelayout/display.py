
from ftw.simplelayout.interfaces import IDisplaySettings
from zope.interface import implements
from zope.interface import Interface
from zope.component import adapts
from zope.annotation import IAttributeAnnotatable
from zope.annotation import IAnnotations
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
            storage = PersistentMapping()
            self.annotations[DISPLAY_SETTINGS_KEY] = storage
            return storage
        return self.annotations[DISPLAY_SETTINGS_KEY]

    def set_position(self, value):
        if not isinstance(value, int):
            raise ValueError('Expect a integer as value')

        self.get_storage()['position'] = value

    def get_position(self):
        return self.get_storage().get('position', None)

    def set_height(self, value):
        self.get_storage()['height'] = value

    def get_height(self):
        return self.get_storage().get('height', None)

    def set_layout(self, value):
        if not isinstance(value, int):
            raise ValueError('Expected a integer as value')

        self.get_storage()['layout'] = value

    def get_layout(self):
        return self.get_storage().get('layout', None)

    def set_column(self, value):
        if not isinstance(value, int):
            raise ValueError('Expected a integer as value')

        self.get_storage()['column'] = value

    def get_column(self):
        return self.get_storage().get('column', None)

    def set_total_columns(self, value):
        if not isinstance(value, int):
            raise ValueError('Expected a integer as value')

        self.get_storage()['total_columns'] = value

    def get_total_columns(self):
        return self.get_storage().get('total_columns', None)
