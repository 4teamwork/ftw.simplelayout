# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from ftw.simplelayout.interfaces import ISimplelayout
from zope.interface import Interface


class ITextBlock(Interface):
    """Marker interface for TextBlocks"""


class IVideoBlock(Interface):
    """Marker interface for VideoBlocks"""


class IFileListingBlock(Interface):
    """Marker interface for TextBlocks"""


class IListingBlockColumns(Interface):
    """Marker interface for TextBlocks"""

    def columns():
        """Returns an ftw.table compatible list of columns"""


class IGalleryBlock(Interface):
    """Marker interface for GalleryBlock"""


class IContentPage(ISimplelayout):
    """Marker interface for ConetPages"""
