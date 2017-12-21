from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
import transaction


class TestRemoveBlockPloneUI(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

        self.page = create(Builder('sample container'))
        self.block = create(Builder('sample block').within(self.page))

        self.page_state = {
            "default": [
                {"cols": [
                    {"blocks": [
                        {"uid": IUUID(self.block)}
                    ]}
                ]}
            ]
        }

        IPageConfiguration(self.page).store(self.page_state)
        transaction.commit()

    @browsing
    def test_page_state_is_updated_after_block_removal(self, browser):
        browser.login().visit(self.page, view='folder_contents')

        browser.visit(self.block, view='delete_confirmation')
        browser.find_button_by_label('Delete').click()
        browser.visit(self.page)
        self.assertFalse(browser.css('.sl-block'))
