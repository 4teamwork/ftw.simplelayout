from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import IS_PLONE_5
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
from unittest2 import skipUnless
import re
import transaction


@skipUnless(not IS_PLONE_5, 'requires plone < 5')
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
    def test_default_scale_is_preview(self, browser):
        browser.login().visit(self.page, view='@@leadimage')
        self.assertEquals(
            '400',
            browser.css('img').first.attrib['width'])

    @browsing
    def test_render_image_with_other_scale(self, browser):
        browser.login().visit(self.page,
                              view='@@leadimage',
                              data={'scale': 'mini'})
        self.assertEquals(
            '200',
            browser.css('img').first.attrib['width'])

    @browsing
    def test_get_image_from_block_in_any_container(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').with_dummy_image().within(page))
        IPageConfiguration(page).store(
            {"portletright": [{"cols": [{"blocks": [
                {"uid": IUUID(block)},
            ]}]}]})
        transaction.commit()

        browser.login().visit(page, view='@@leadimage')
        src_url = browser.css('img').first.attrib['src']
        self.assertRegexpMatches(src_url, r'^{}'.format(
            re.escape(block.absolute_url())))

    @browsing
    def test_support_images_in_gallery_blocks(self, browser):
        page = create(Builder('sl content page'))
        gallery = create(Builder('sl galleryblock').within(page))
        image = create(Builder('image').with_dummy_content().within(gallery))
        page_config = IPageConfiguration(page)
        page_config.store(
            {"default": [{"cols": [{"blocks": [
                {"uid": IUUID(gallery)},
            ]}]}]})
        transaction.commit()

        browser.login().visit(page, view='@@leadimage')
        src_url = browser.css('img').first.attrib['src']
        self.assertRegexpMatches(src_url, r'^{}'.format(
            re.escape(image.absolute_url())))
