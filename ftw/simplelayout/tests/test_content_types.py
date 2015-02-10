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
