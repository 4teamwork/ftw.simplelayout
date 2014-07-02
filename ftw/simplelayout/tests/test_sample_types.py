from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from unittest2 import TestCase


class TestSampleTypes(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSampleTypes, self).setUp()

        self.page = create(Builder('sl content page').titled(u'A page'))

    @browsing
    def test_add_page(self, browser):
        # Page
        browser.login().visit()
        factoriesmenu.add('ContentPage')
        browser.fill({'Title': u'A test page'}).submit()

        self.assertEquals('A test page', plone.first_heading())

    @browsing
    def test_add_textblock_with_title(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('TextBlock')
        browser.fill({'Title': u'A test textblock',
                      'Text': u'Some text',
                      'Show title': True}).submit()

        self.assertIn('Some text',
                      browser.css('.block-view-wrapper').first.text)
        self.assertEquals('A test textblock',
                          browser.css('.block-view-wrapper h2').first.text)

    @browsing
    def test_add_textblock_without_title(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('TextBlock')
        browser.fill({'Title': u'A test textblock',
                      'Text': u'Some text',
                      'Show title': False}).submit()

        self.assertIn('Some text',
                      browser.css('.block-view-wrapper').first.text)
        self.assertEquals(0,
                          len(browser.css('.block-view-wrapper h2')),
                          'Expect no textblock title')

    @browsing
    def test_nested_contentpages(self, browser):
        nested = create(Builder('sl content page')
                        .titled(u'Nested')
                        .within(self.page))

        browser.login().visit(self.page)

        self.assertFalse(browser.css('.sl-block'),
                         'Expect no block, also the contentpage should no be '
                         'visible as block')

        browser.visit(nested)
        self.assertEquals('Nested', plone.first_heading())

    @browsing
    def test_add_simplelayout_file(self, browser):
        listingblock = create(Builder('sl listingblock')
                              .titled('ListingBlock')
                              .within(self.page))

        browser.login().visit(listingblock, view='folder_contents')
        factoriesmenu.add('File')
        browser.fill(
            {'File': ('Some Data', 'file.txt', 'text/plain')}).submit()

        self.assertEquals(
            '{0}/file.txt/view'.format(listingblock.absolute_url()),
            browser.url)

    @browsing
    def test_simplelayout_file_view(self, browser):
        listingblock = create(Builder('sl listingblock')
                              .titled('ListingBlock')
                              .within(self.page))

        browser.login().visit(listingblock, view='folder_contents')
        factoriesmenu.add('File')
        browser.fill(
            {'File': ('1' * 1024, 'file.txt', 'text/plain')}).submit()

        self.assertEquals('file.txt', plone.first_heading())

        self.assertEquals(
            '{0}/file.txt/@@download/file/file.txt'.format(
                listingblock.absolute_url()),
            browser.css('#content-core a').first.attrib['href'])

        self.assertEquals(u'\u2014 1 KB',
                          browser.css('#content-core .discreet').first.text)

        self.assertEquals('txt.png',
                          browser.css('#content-core img').first.attrib['src'])
