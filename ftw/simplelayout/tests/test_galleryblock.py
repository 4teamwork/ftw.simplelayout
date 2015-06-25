from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestGalleryBlock(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestGalleryBlock, self).setUp()
        self.portal = self.layer['portal']
        self.page = create(Builder('sl content page').titled(u'A page'))

    @browsing
    def test_galleryblock_rendering(self, browser):
        create(Builder('sl galleryblock')
               .titled('My galleryblock')
               .having(show_title=True)
               .within(self.page))

        browser.login().visit(self.page)

        self.assertTrue(browser.css('.sl-block'))

        self.assertEquals(u'My galleryblock',
                          browser.css('.sl-block h2').first.text)
