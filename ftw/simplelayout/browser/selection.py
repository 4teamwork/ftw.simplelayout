from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.app.content.browser.selection import DefaultPageSelectionView


def filter_simplelayout_blocks(brain):
    _catalog = brain.portal_catalog._catalog
    ifaces = _catalog.indexes['object_provides']._unindex.get(brain.getRID())
    return ISimplelayoutBlock.__identifier__ not in ifaces


class SimplelayoutDefaultPageSelectionView(DefaultPageSelectionView):

    def get_selectable_items(self):
        result = super(SimplelayoutDefaultPageSelectionView,
                       self).get_selectable_items()

        return filter(filter_simplelayout_blocks, result)
