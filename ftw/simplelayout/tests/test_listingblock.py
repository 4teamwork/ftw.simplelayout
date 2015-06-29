from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.contents.interfaces import IListingBlockColumns
from ftw.simplelayout.contents.filelistingblock import listing_block_columns
from ftw.simplelayout.contents.filelistingblock import ListingBlockDefaultColumns
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing import TEST_USER_ID
from unittest2 import skip
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

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestListingBlock, self).setUp()
        self.portal = self.layer['portal']
        self.page = create(Builder('sl content page').titled(u'A page'))

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

    @browsing
    def test_columns_vocabulary_on_listingblock_add_form(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('FileListingBlock')

        self.assertEquals(
            ['creater', 'size', 'Review State', 'ID'],
            browser.css('#form-widgets-columns-from option').text)

        self.assertEquals(
            ['Type', 'Title', 'modified'],
            browser.css('#form-widgets-columns-to option').text)

    @skip('How do I use this ordered multi select widget without js?')
    @browsing
    def test_adding_listingblock(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('FileListingBlock')
        browser.fill(
            {'Title': 'My listingblock', 'Show title': True}).submit()
        self.assertEquals(self.page.absolute_url(), browser.url)

    @browsing
    def test_listingblock_rendering(self, browser):
        create(Builder('sl listingblock')
               .titled('My listingblock')
               .having(show_title=True)
               .within(self.page))

        browser.login().visit(self.page)

        self.assertTrue(browser.css('.sl-block'))

        self.assertEquals(u'My listingblock',
                          browser.css('.sl-block h2').first.text)

        self.assertEquals(['Type', 'Title', 'modified'],
                          browser.css('.sl-block table th').text)

    @browsing
    def test_listingblock_table_contents(self, browser):
        block = create(Builder('sl listingblock')
                       .titled('My listingblock')
                       .having(show_title=True)
                       .within(self.page))

        file_ = create(Builder('file')
                       .titled('Test file')
                       .having(creators=(TEST_USER_ID.decode('utf-8'), ))
                       .with_dummy_content()
                       .within(block))

        modified = file_.modified().strftime('%d.%m.%Y')
        browser.login().visit(self.page)
        self.assertEquals([['Type', 'Title', 'modified'],
                           ['', 'Test file', modified]],
                          browser.css('.sl-block table').first.lists())
