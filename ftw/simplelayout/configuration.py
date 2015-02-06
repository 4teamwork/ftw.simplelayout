from ftw.simplelayout.interfaces import IPageConfiguration
from zope.interface import implements
from zope.annotation import IAnnotations
from copy import deepcopy

ANNOTATION_KEY = 'ftw.simplelayout.pageconfiguration'


def convert_to_rows(conf):
    """Convert the given layout configuration to a rows/columns/blocks
       mapping.
    """
    # TODO: validate data
    rows = []
    for layout in conf['layouts']:
        row = {'cols': []}
        for i in range(layout):
            col = {'blocks': []}
            row['cols'].append(col)
        rows.append(row)

    for block in conf['blocks']:
        rows[block['layoutPos']]['cols'][block['columnPos']][
            'blocks'].append({'uid': block['uid']})

    return rows


class PageConfiguration(object):
    """Adapter for storing simplelayout page configuration.
    """
    implements(IPageConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, conf):
        annotations = IAnnotations(self.context)
        annotations[ANNOTATION_KEY] = convert_to_rows(conf)

    def load(self):
        annotations = IAnnotations(self.context)
        return deepcopy(annotations.setdefault(ANNOTATION_KEY, []))
