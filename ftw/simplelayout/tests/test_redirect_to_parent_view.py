from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing


class RedirectToParentView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.setup_sample_ftis(self.layer['portal'])
        self.container = create(Builder('sample container'))
        self.block = create(Builder('sample block').within(self.container))

    @browsing
    def test_view_is_redirecting_to_parent_with_anchor(self, browser):
        browser.login().visit(self.block, view='@@redirect_to_parent')
        self.assertEquals(self.container.absolute_url() + '#' + self.block.id,
                          browser.url)

    @browsing
    def test_redirect_to_parent_if_anonymous(self, browser):
        browser.visit(self.container, view='@@redirect_to_parent')
        self.assertEquals(
            self.layer['portal'].absolute_url() + '#' + self.container.id,
            browser.url)

    @browsing
    def test_do_NOT_redirect_to_parent_if_NOT_anonymous(self, browser):
        browser.login().visit(self.container, view='@@redirect_to_parent')
        self.assertEquals(self.container.absolute_url() + '/folder_contents',
                          browser.url)
