from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IBlockModifier
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from unittest2 import TestCase
from zope.component import getMultiAdapter


class TestSampleTypes(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestSampleTypes, self).setUp()

        self.portal = self.layer['portal']

    @browsing
    def test_add_page(self, browser):
        browser.login().visit()
        factoriesmenu.add('ContentPage')
        browser.fill({'Title': u'This is a ContentPage'})
        browser.find_button_by_label('Save').click()
        self.assertEquals(u'This is a ContentPage', plone.first_heading())

    @browsing
    def test_add_textblock(self, browser):
        contentpage = create(Builder('sl content page').titled(u'A page'))

        browser.login().visit(contentpage)
        factoriesmenu.add('TextBlock')
        browser.fill({'Title': u'This is a ContentPage',
                      'Text': u'Some text'})
        browser.find_button_by_label('Save').click()
        browser.visit(contentpage)

        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')

    def test_textblock_modified(self):
        contentpage = create(Builder('sl content page').titled(u'A page'))
        block = create(Builder('sl textblock').within(contentpage))

        data = {'scale': 'mini'}
        modifier = getMultiAdapter((block, block.REQUEST), IBlockModifier)
        modifier.modify(data)

        conf = IBlockConfiguration(block).load()
        self.assertEquals('mini', conf.get('scale'))

    @browsing
    def test_contentpage_without_show_title_behavior(self, browser):
        page = create(Builder('sl content page')
                      .titled(u'A page')
                      .within(self.portal))

        browser.login().visit(page)

        self.assertEqual(
            ['A page'],
            browser.css('.documentFirstHeading').text)
