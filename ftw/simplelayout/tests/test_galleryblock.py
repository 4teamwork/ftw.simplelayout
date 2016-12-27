from DateTime import DateTime
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

    @browsing
    def test_hidden_galleryblock_has_special_class(self, browser):
        """
        This test makes sure that a special class is available on the block
        if the block is hidden. This can be used to visually highlight
        hidden blocks.
        """
        galleryblock = create(Builder('sl galleryblock')
                              .titled('My galleryblock')
                              .having(show_title=True)
                              .having(is_hidden=True)
                              .within(self.page))

        browser.login()

        # The block must have a class "hidden".
        browser.visit(self.page)
        self.assertEqual(
            'sl-block ftw-simplelayout-galleryblock hidden',
            browser.css('.ftw-simplelayout-galleryblock').first.attrib['class']
        )

        # Edit the block and make appear again.
        browser.visit(galleryblock, view='edit.json')
        response = browser.json
        browser.open_html(response['content'])
        browser.fill({'Hide the block': False}).submit()

        # The block must no longer have a class "hidden".
        browser.visit(self.page)
        self.assertEqual(
            'sl-block ftw-simplelayout-galleryblock',
            browser.css('.ftw-simplelayout-galleryblock').first.attrib['class']
        )

    @browsing
    def test_hidden_galleryblock_not_visible_without_edit_permission(self,
                                                                     browser):
        """
        This test makes sure that users without edit permission, e.g. the
        anonymous user, do not see the hidden block.
        """
        create(Builder('sl galleryblock')
               .titled('My galleryblock')
               .having(show_title=True)
               .having(is_hidden=True)
               .within(self.page))

        # Make sure an anonymous user cannot see the block.
        browser.logout().visit(self.page)
        self.assertEqual(
            [],
            browser.css('.ftw-simplelayout-galleryblock')
        )

        # Login to make sure the block is visible for admin users.
        browser.login().visit(self.page)
        self.assertEqual(
            ['My galleryblock'],
            browser.css('.ftw-simplelayout-galleryblock h2').text
        )

    @browsing
    def test_sort_by_title_ascending(self, browser):
        gallery = create(Builder('sl galleryblock')
                         .titled('My galleryblock')
                         .having(sort_on='sortable_title')
                         .having(sort_order='ascending')
                         .within(self.page))

        create(Builder('image')
               .titled('a_img')
               .with_dummy_content()
               .within(gallery))

        create(Builder('image')
               .titled('b_img')
               .with_dummy_content()
               .within(gallery))

        create(Builder('image')
               .titled('c_img')
               .with_dummy_content()
               .within(gallery))

        browser.login().visit(self.page)

        img_list = browser.css('.gallery-item img')
        img_title_list = []

        for img in img_list:
            img_title_list.append(img.get('alt').split(',')[0])

        self.assertEqual(img_title_list, ['a_img', 'b_img', 'c_img'])

    @browsing
    def test_sort_by_title_descending(self, browser):
        gallery = create(Builder('sl galleryblock')
                         .titled('My galleryblock')
                         .having(sort_on='sortable_title')
                         .having(sort_order='descending')
                         .within(self.page))

        create(Builder('image')
               .titled('a_img')
               .with_dummy_content()
               .within(gallery))

        create(Builder('image')
               .titled('b_img')
               .with_dummy_content()
               .within(gallery))

        create(Builder('image')
               .titled('c_img')
               .with_dummy_content()
               .within(gallery))

        browser.login().visit(self.page)

        img_list = browser.css('.gallery-item img')
        img_title_list = []

        for img in img_list:
            img_title_list.append(img.get('alt').split(',')[0])

        self.assertEqual(img_title_list, ['c_img', 'b_img', 'a_img'])

    @browsing
    def test_sort_by_modified_ascending(self, browser):
        gallery = create(Builder('sl galleryblock')
                         .titled('My galleryblock')
                         .having(sort_on='modified')
                         .having(sort_order='ascending')
                         .within(self.page))

        create(Builder('image')
               .titled('a_img')
               .with_dummy_content()
               .within(gallery)
               .with_modification_date(DateTime("2014-01-01")))

        create(Builder('image')
               .titled('b_img')
               .with_dummy_content()
               .within(gallery)
               .with_modification_date(DateTime("2016-01-01")))

        create(Builder('image')
               .titled('c_img')
               .with_dummy_content()
               .within(gallery)
               .with_modification_date(DateTime("2015-01-01")))

        browser.login().visit(self.page)

        img_list = browser.css('.gallery-item img')
        img_title_list = []

        for img in img_list:
            img_title_list.append(img.get('alt').split(',')[0])

        self.assertEqual(img_title_list, ['a_img', 'c_img', 'b_img'])

    @browsing
    def test_sort_by_modified_descending(self, browser):
        gallery = create(Builder('sl galleryblock')
                         .titled('My galleryblock')
                         .having(sort_on='modified')
                         .having(sort_order='descending')
                         .within(self.page))

        create(Builder('image')
               .titled('a_img')
               .with_dummy_content()
               .within(gallery)
               .with_modification_date(DateTime("2014-01-01")))

        create(Builder('image')
               .titled('b_img')
               .with_dummy_content()
               .within(gallery)
               .with_modification_date(DateTime("2016-01-01")))

        create(Builder('image')
               .titled('c_img')
               .with_dummy_content()
               .within(gallery)
               .with_modification_date(DateTime("2015-01-01")))

        browser.login().visit(self.page)

        img_list = browser.css('.gallery-item img')
        img_title_list = []

        for img in img_list:
            img_title_list.append(img.get('alt').split(',')[0])

        self.assertEqual(img_title_list, ['b_img', 'c_img', 'a_img'])

    @browsing
    def test_image_title_with_umlaut(self, browser):
        """
        This test makes sure that gallery block does not fail when
        it contains image objects having umlauts in their title.
        """
        gallery = create(Builder('sl galleryblock')
                         .titled('My Gallery Block')
                         .within(self.page))
        create(Builder('image')
               .titled(u'T\xe4st')
               .with_dummy_content()
               .within(gallery))

        browser.login()
        browser.open(self.page)
        self.assertEqual(
            u'T\xe4st',
            browser.css('.ftw-simplelayout-galleryblock .sl-block-content a').first.attrib['title']
        )
        self.assertEqual(
            u'T\xe4st, enlarged picture.',
            browser.css('.ftw-simplelayout-galleryblock .sl-block-content a img').first.attrib['alt']
        )
