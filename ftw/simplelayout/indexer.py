from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from zope.component import adapts
from collective.dexteritytextindexer import indexer


class BlockSearchableTextIndexer(object):
    adapts(ISimplelayout)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable_text = ''
        contents = self.context.getFolderContents(
            {'object_provides': ISimplelayoutBlock.__identifier__,
             'sort_order': 'getObjPositionInParent'},
            full_objects=True)
        for content in contents:
            searchable_text += indexer.dynamic_searchable_text_indexer(
                content)()
        return searchable_text
