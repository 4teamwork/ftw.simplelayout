from copy import deepcopy
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from zope.annotation import IAnnotations
from zope.interface import implements


SL_ANNOTATION_KEY = 'ftw.simplelayout.pageconfiguration'
BLOCK_ANNOTATION_KEY = 'ftw.simplelayout.blockconfiguration'


def convert_to_rows(conf):
    """Convert the given layout configuration to a rows/columns/blocks
       mapping.
    """
    # TODO: validate data

    containers = PersistentMapping()
    for container in conf:
        rows = PersistentList()
        for layout in container['layouts']:
            row = PersistentMapping({'cols': PersistentList()})
            for i in range(layout):
                col = PersistentMapping({'blocks': PersistentList()})
                row['cols'].append(col)
            rows.append(row)

        for block in container['blocks']:
            rows[block['layoutPos']]['cols'][block['columnPos']][
                'blocks'].append(PersistentMapping({'uid': block['uid']}))

        containers[container['containerid']] = rows

    return containers


class PageConfiguration(object):
    """Adapter for storing simplelayout page configuration.
    """
    implements(IPageConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, conf):
        annotations = IAnnotations(self.context)
        annotations[SL_ANNOTATION_KEY] = convert_to_rows(conf)

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
