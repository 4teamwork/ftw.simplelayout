from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.utils import IS_PLONE_5
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from unittest import skipIf
from unittest import TestCase


class TestSampleTypes(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestSampleTypes, self).setUp()

        self.page = create(Builder('sl content page').titled(u'A page'))

    @browsing
    def test_add_page(self, browser):
        # Page
        browser.login().visit()
        factoriesmenu.add('ContentPage')
        browser.fill({'Title': u'A test page'})
        browser.find_button_by_label('Save').click()

        self.assertEquals('A test page', plone.first_heading())

    @browsing
    def test_add_textblock_with_title(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('TextBlock')
        browser.fill({'Title': u'A test textblock',
                      'Text': u'Some text',
                      'Show title': True})
        browser.find_button_by_label('Save').click()

        self.assertIn('Some text',
                      browser.css('body').first.text)
        self.assertEquals('A test textblock',
                          browser.css('h2').first.text)

    @browsing
    def test_add_textblock_without_title(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('TextBlock')
        browser.fill({'Title': u'A test textblock',
                      'Text': u'Some text',
                      'Show title': False})
        browser.find_button_by_label('Save').click()

        self.assertIn('Some text',
                      browser.css('body').first.text)
        self.assertEquals(0,
                          len(browser.css('h2')),
                          'Expect no textblock title')

    @browsing
    def test_nested_contentpages(self, browser):
        nested = create(Builder('sl content page')
                        .titled(u'Nested')
                        .within(self.page))

        browser.login().visit(self.page)

        self.assertFalse(browser.css('.sl-block'),
                         'Expect no block, also the contentpage should not be '
                         'visible as block')

        browser.visit(nested)
        self.assertEquals('Nested', plone.first_heading())

    @browsing
    def test_add_file_to_listingblock(self, browser):
        listingblock = create(Builder('sl listingblock')
                              .titled('ListingBlock')
                              .within(self.page))

        browser.login().visit(listingblock, view='folder_contents')
        factoriesmenu.add('File')
        browser.fill(
            {'File': ('Some Data', 'file.txt', 'text/plain')})
        browser.find_button_by_label('Save').click()

        self.assertEquals(
            '{0}/file.txt/view'.format(listingblock.absolute_url()),
            browser.url)


    @skipIf(IS_PLONE_5, 'No mapblock on plone 5.1')
    @browsing
    def test_adding_mapblock(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('MapBlock')
        browser.fill({'form.widgets.IBlockCoordinates.coordinates': 'POINT(7.444608499999999 46.9479222)'})
        browser.find_button_by_label('Save').click()
        self.assertEquals(1, len(browser.css('.ftw-simplelayout-mapblock')))

    @skipIf(IS_PLONE_5, 'No mapblock on plone 5.1')
    @browsing
    def test_mapblock_id_based_on_block_id(self, browser):
        mapblock = create(Builder('sl mapblock').within(self.page))
        browser.login().visit(self.page)
        self.assertTrue(browser.css('#geo-{0}'.format(mapblock.id)),
                        'Did not found any mablock')
