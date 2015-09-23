from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase
import transaction


class TestGalleryBlock(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestGalleryBlock, self).setUp()
        self.portal = self.layer['portal']
        self.page = create(Builder('sl content page').titled(u'A page'))
        self.ptool = getToolByName(self.page, 'portal_properties')

    def test_scale_is_available(self):
        name = 'simplelayout_galleryblock'

        # the format of allowed_sizes is <name> <width>:<height>
        allowed_sizes = self.ptool.get('imaging_properties').allowed_sizes
        scale_found = False
        for size in allowed_sizes:
            size_name, sizes = size.split(' ')
            if size_name == name:
                scale_found = True

        self.assertTrue(
            scale_found,
            "The simplelayout_galleryblock scale is not available." +
            "Available scales: {0}".format(allowed_sizes))

    @browsing
    def test_rendering(self, browser):
        create(Builder('sl galleryblock')
               .titled('My galleryblock')
               .having(show_title=True)
               .within(self.page))

        browser.login().visit(self.page)

        self.assertTrue(browser.css('.sl-block'))

        self.assertEquals(u'My galleryblock',
                          browser.css('.sl-block h2').first.text)

    @browsing
    def test_all_the_images_will_be_displayed(self, browser):
        block = create(Builder('sl galleryblock')
                       .titled('My galleryblock')
                       .having(show_title=True)
                       .within(self.page))

        create(Builder('image')
               .titled('Test image')
               .with_dummy_content()
               .within(block))

        create(Builder('image')
               .titled('Test im\xc3\xa4ge')
               .with_dummy_content()
               .within(block))

        browser.login().visit(self.page)
        self.assertEquals(2, len(browser.css('.sl-block-content img')))

    @browsing
    def test_each_gallery_has_a_unique_rel_name(self, browser):
        gallerie_1 = create(Builder('sl galleryblock')
                            .titled('My galleryblock')
                            .having(show_title=True)
                            .within(self.page))

        create(Builder('image')
               .titled('Test image')
               .with_dummy_content()
               .within(gallerie_1))

        create(Builder('image')
               .titled('Test image')
               .with_dummy_content()
               .within(gallerie_1))

        gallerie_2 = create(Builder('sl galleryblock')
                            .titled('My galleryblock')
                            .having(show_title=True)
                            .within(self.page))

        create(Builder('image')
               .titled('Test image')
               .with_dummy_content()
               .within(gallerie_2))

        create(Builder('image')
               .titled('Test image')
               .with_dummy_content()
               .within(gallerie_2))

        browser.login().visit(self.page)

        # Should be two images in each gallery.
        # The rel is 'colorbox-{block-id}'

        self.assertEquals(
            2,
            len(browser.css('.sl-block-content a[rel="colorbox-{0}"]'.format(
                gallerie_1.getId()))))

        self.assertEquals(
            2,
            len(browser.css('.sl-block-content a[rel="colorbox-{0}"]'.format(
                gallerie_2.getId()))))

    @browsing
    def test_galleryblock_title_not_rendered_when_empty(self, browser):
        """
        This test makes sure that the title of the block is only rendered
        if there is a title. Otherwise we'll end up with an empty HTML
        tag in the template.
        """
        galleryblock = create(Builder('sl galleryblock')
                              .titled('My galleryblock')
                              .having(show_title=True)
                              .within(self.page))

        browser.login().visit(self.page)

        title_css_selector = '.ftw-simplelayout-galleryblock h2'

        # Make sure the title is here (in its tag).
        self.assertEqual('My galleryblock',
                         browser.css(title_css_selector).first.text)

        # Remove the title of the block and make sure the tag is no longer
        # there.
        galleryblock.title = ''
        transaction.commit()
        browser.login().visit(self.page)
        self.assertEqual([], browser.css(title_css_selector))
