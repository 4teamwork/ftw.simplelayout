# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from ftw.simplelayout.interfaces import ISimplelayoutPage
from zope.interface import Interface


class ITextBlock(Interface):
    """Marker interface for TextBlocks"""


class IListingBlock(Interface):
    """Marker interface for TextBlocks"""


class IFile(Interface):
    """Marker interface for TextBlocks"""


class IListingBlockColumns(Interface):
    """Marker interface for TextBlocks"""

    def columns():
        """Returns an ftw.table compatible list of columns"""


class IContentPage(ISimplelayoutPage):
    """Marker interface for ConetPages"""
