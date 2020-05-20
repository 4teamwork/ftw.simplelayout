from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from unittest import TestCase


class TestAliasBlockRendering(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

    @browsing
    def test_create_aliasblock(self, browser):
        alias = create(Builder('sl aliasblock')
                       .titled(u'\xc4lias Block')
                       .within(self.page))
        title = browser.visit(alias).css('.sl-alias-block h2').first.text

        self.assertEqual(u'\xc4lias Block', title)

    @browsing
    def test_add_aliasblock_using_factoriesmenu(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('AliasBlock')
        browser.fill({'Title': u'\xc4lias Block'}).save()
        self.assertTrue(browser.css('.sl-alias-block'))
