from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from unittest import TestCase


class TestDefaultPageForm(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    @browsing
    def test_default_page_does_not_list_textblock(self, browser):
        page = create(Builder('sl content page'))
        create(Builder('sl textblock').within(page))
        create(Builder('sl content page').titled(u'subpage').within(page))

        browser.login()
        browser.visit(page, view='select_default_page')

        self.assertEquals(['subpage'], browser.css('#content-core label').text)
