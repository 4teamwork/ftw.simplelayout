from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.contents.interfaces import IListingBlockColumns
from ftw.simplelayout.contents.listingblock import listing_block_columns
from ftw.simplelayout.contents.listingblock import ListingBlockDefaultColumns
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase
from zope.component import queryMultiAdapter
from zope.interface.verify import verifyClass
from zope.schema.vocabulary import SimpleVocabulary


def assert_ftw_table_column(column):
    assert 'column' in column, 'Expect column in {0}'.format(
        str(column))
    assert 'column_title' in column, 'Expect column_title in {0}'.format(
        str(column))


class TestListingBlock(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestListingBlock, self).setUp()
        self.portal = self.layer['portal']

    def test_listingblock_default_columns_adapter(self):
        verifyClass(IListingBlockColumns, ListingBlockDefaultColumns)

        adapter = queryMultiAdapter((self.portal, self.portal.REQUEST),
                                    IListingBlockColumns)

        self.assertIsNotNone(adapter)

        for column in adapter.columns():
            assert_ftw_table_column(column)

    def test_columns_context_source_binder(self):

        vocabulary = listing_block_columns(self.portal)
        self.assertTrue(isinstance(vocabulary, SimpleVocabulary),
                        'Expect a SimpleVocabulary instance.')
