from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from Products.CMFPlone.utils import _createObjectByType
from unittest2 import TestCase
import transaction
from plone.app.textfield.value import RichTextValue


class TestSimplelayoutView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()

        self.contentpage = create(Builder('sl content page'))

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD, ))

        self.url = self.contentpage.absolute_url() + '/@@simplelayout'

    @browsing
    def test_view_renders(self, browser):
        textblock = create(Builder('sl textblock')
                           .titled('TextBlock title')
                           .within(self.contentpage)
                           .having(text=RichTextValue('The text'))
                           .having(show_title=False))

        textblock.reindexObject()

        browser.login().visit(self.contentpage, view='@@simplelayout')

        self.assertEqual(browser.url, self.url)
        self.assertEquals('The text', browser.css(
            '.block-view-wrapper').first.text)
        self.assertFalse(len(browser.css('.block-view-wrapper h2')))

        textblock.show_title = True
        transaction.commit()

        self.browser.open(self.url)
        browser.visit(self.contentpage)
        self.assertEquals('TextBlock title',
                          browser.css('.block-view-wrapper h2').first.text)
