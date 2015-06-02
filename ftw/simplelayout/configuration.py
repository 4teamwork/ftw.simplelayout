from copy import deepcopy
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.interface import implements


SL_ANNOTATION_KEY = 'ftw.simplelayout.pageconfiguration'
BLOCK_ANNOTATION_KEY = 'ftw.simplelayout.blockconfiguration'


def make_resursive_persistent(conf):
    """Convert the given layout configuration to a rows/columns/blocks
       mapping.
    """
    # TODO: validate data

    def persist(data):
        if isinstance(data, dict):
            data = PersistentMapping(data)

            for key, value in data.items():
                data[key] = persist(value)

        elif isinstance(data, list):
            return PersistentList(map(persist, data))

        else:
            # Usually we got basestrings, or integer here, so do nothing.
            pass

        return data

    return persist(conf)


class PageConfiguration(object):
    """Adapter for storing simplelayout page configuration.
    """
    implements(IPageConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, conf):
        annotations = IAnnotations(self.context)
        annotations[SL_ANNOTATION_KEY] = make_resursive_persistent(conf)

    def load(self):
        annotations = IAnnotations(self.context)
        return deepcopy(annotations.setdefault(SL_ANNOTATION_KEY,
                                               PersistentMapping()))


class BlockConfiguration(object):
    """Adapter for storing block configuration.
    """
    implements(IBlockConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, data):
        annotations = IAnnotations(self.context)
        annotations[BLOCK_ANNOTATION_KEY] = PersistentMapping(data)

    def load(self):
        annotations = IAnnotations(self.context)
        return annotations.setdefault(BLOCK_ANNOTATION_KEY,
                                      PersistentMapping())
