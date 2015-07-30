from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import IS_PLONE_5
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import skipIf
import transaction


@skipIf(not IS_PLONE_5, 'requires plone < 5')
class TestLeadImage(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.block_without_image = create(Builder('sl textblock')
                                          .within(self.page))

        self.block_with_image = create(Builder('sl textblock')
                                       .within(self.page)
                                       .with_dummy_image())

        self.page_state = {
            "default": [
                {
                    "cols": [
                        {
                            "blocks": [
                                {
                                    "uid": IUUID(self.block_with_image)
                                }
                            ]
                        }
                    ]
                },
                {
                    "cols": [
                        {
                            "blocks": [
                                {
                                    "uid": IUUID(self.block_without_image)
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        self.page_config = IPageConfiguration(self.page)
        self.page_config.store(self.page_state)
        transaction.commit()

    @browsing
    def test_use_first_image_in_page_state(self, browser):
        browser.login().visit(self.page, view='@@leadimage')
        self.assertTrue(
            browser.css('img').first.attrib['src'].startswith(
                self.block_with_image.absolute_url()))

    @browsing
    def test_default_scale_is_mini(self, browser):
        browser.login().visit(self.page, view='@@leadimage')
        self.assertEquals(
            '200',
            browser.css('img').first.attrib['width'])

    @browsing
    def test_render_image_with_other_scale(self, browser):
        browser.login().visit(self.page,
                              view='@@leadimage',
                              data={'scale': 'preview'})
        self.assertEquals(
            '400',
            browser.css('img').first.attrib['width'])

    @browsing
    def test_only_get_image_from_block_in_default_container(self, browser):
        second_block_with_image = create(Builder('sl textblock')
                                         .within(self.page)
                                         .with_dummy_image())

        self.page_state.update({"other": [
            {
                "cols": [
                    {
                        "blocks": [
                            {
                                "uid": IUUID(second_block_with_image)
                            }
                        ]
                    }
                ]
            }
        ]})

        self.page_config.store(self.page_state)
        transaction.commit()

        browser.login().visit(self.page, view='@@leadimage')
        self.assertTrue(
            browser.css('img').first.attrib['src'].startswith(
                self.block_with_image.absolute_url()))
