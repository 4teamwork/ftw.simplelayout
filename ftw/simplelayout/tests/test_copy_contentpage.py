from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import Browser
from plone.uuid.interfaces import IUUID
import transaction


class TestCopySimplelayoutPage(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

        self.page = create(Builder('sample container'))
        self.block_left = create(Builder('sample block').within(self.page))
        self.block_right = create(Builder('sample block').within(self.page))
        self.block_below = create(Builder('sample block').within(self.page))

        self.page_state = {
            "default": [
                {"cols": [
                    {"blocks": [
                        {"uid": IUUID(self.block_left)}
                    ]},
                    {"blocks": [
                        {"uid": IUUID(self.block_right)}
                    ]},
                ]},
                {"cols": [
                    {"blocks": [
                        {"uid": IUUID(self.block_below)
                         }
                    ]}
                ]}
            ]
        }

        IPageConfiguration(self.page).store(self.page_state)
        transaction.commit()

    def assertPageLayout(self, page):
        browser = Browser()
        with browser(self.layer['app']):
            browser.login().visit(page)

            self.assertEquals(
                1,
                len(browser.css('.sl-layout:first-child > .sl-column:first-child > .sl-block')),
                'Expect one block in first column of the first layout.')

            self.assertEquals(
                1,
                len(browser.css('.sl-layout:first-child > .sl-column:nth-child(2) > .sl-block')),
                'Expect one block in second column of the first layout.')

            self.assertEquals(
                1,
                len(browser.css('.sl-layout:nth-child(2) .sl-block')),
                'Expect one block in second second layout.')

    def test_uids_in_block_state_are_updated_after_copy(self):
        copy = self.portal.manage_copyObjects([self.page.id])
        self.portal.manage_pasteObjects(copy)
        transaction.commit()
        self.assertPageLayout(self.page)

        newpage = self.portal.get('copy_of_' + self.page.id)
        self.assertPageLayout(newpage)
