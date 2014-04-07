from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from unittest2 import TestCase


class TestSimplelayoutInfoPage(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    @browsing
    def test_informations_on_info_page(self, browser):
        page = create(Builder('sl content page'))

        browser.login().visit(page, view='simplelayout_info')

        self.assertEquals(['You can arrange blocks in 4 column/s.',
                           'The minimal size of an image is 0.5 column/s.',
                           'The content width is set to 960 pixel. This means'
                           ' one column is 240 pixel.',
                           'The grid has a margin right of 10 pixel.'],
                          browser.css('#content li').text)
