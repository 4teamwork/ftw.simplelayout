from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing


class TestRemoveBlockPloneUI(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

    @browsing
    def test_parent_modified_date_has_changed(self, browser):
        page = create(Builder('sample container'))
        block = create(Builder('sample block').within(page))

        cached_date = page.modification_date

        browser.login().visit(block, view='edit')
        browser.find_button_by_label('Save').click()
        self.assertNotEquals(cached_date,
                             page.modification_date,
                             'Modification date of sl container should change')

    @browsing
    def test_modification_date_of_plone_root_has_changed(self, browser):
        block = create(Builder('sample block').within(self.portal))
        cached_date = self.portal.modified()

        browser.login().visit(block, view='edit')
        browser.find_button_by_label('Save').click()

        self.assertNotEquals(cached_date,
                             self.portal.modified(),
                             'Modification date of portal should change')
