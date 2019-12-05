from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from unittest import TestCase


class TestBlocks(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def test_blocks_not_searchable(self):
        """
        This test makes sure the blocks are not
        searchable.
        """
        plone_utils = getToolByName(getSite(), 'plone_utils')
        user_friendly_types = plone_utils.getUserFriendlyTypes()

        interface_name = 'ftw.simplelayout.interfaces.ISimplelayoutBlock'
        block_types = filter(
            lambda x: interface_name in getattr(x, 'behaviors', ()),
            getToolByName(getSite(), 'portal_types').objectValues()
        )
        searchable_blocks = filter(
            lambda x: x.__name__ in user_friendly_types,
            block_types
        )
        self.assertEqual(
            [],
            searchable_blocks,
            'Some blocks are searchable. This should not be the case. '
            'Please make them not searchable.'
        )
