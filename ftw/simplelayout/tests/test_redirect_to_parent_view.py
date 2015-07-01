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
