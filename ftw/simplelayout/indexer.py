from collective.dexteritytextindexer import indexer
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.utils import is_trashed
from zope.component import adapts


class BlockSearchableTextIndexer(object):
    adapts(ISimplelayout)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        searchable_text = ''
        for content in self.context.objectValues():
            if ISimplelayoutBlock.providedBy(content) and not is_trashed(content):
                searchable_text += indexer.dynamic_searchable_text_indexer(
                    content)()
        return searchable_text
