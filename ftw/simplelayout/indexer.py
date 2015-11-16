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
        for content in self.context.objectValues():
            if ISimplelayoutBlock.providedBy(content):
                searchable_text += indexer.dynamic_searchable_text_indexer(
                    content)()
        return searchable_text
