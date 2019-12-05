from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.utils import IS_PLONE_5
from ftw.testbrowser import browsing
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from plone.registry.interfaces import IRegistry
from plone.uuid.interfaces import IUUID
from StringIO import StringIO
from unittest import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds
import json
import transaction


if IS_PLONE_5:
    from Products.CMFPlone.interfaces.controlpanel import IImagingSchema


class TestTextBlockRendering(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

        self.image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')

    @browsing
    def test_teaser_url_external_on_image_and_title(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(external_link='http://www.4teamwork.ch')
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(open_image_in_overlay=True))

        browser.login().visit(block, view='@@block_view')
        self.assertEquals(
            'http://www.4teamwork.ch',
            browser.css('h2 a').first.attrib['href'])

        self.assertEquals(
            'http://www.4teamwork.ch',
            browser.css('.sl-image a').first.attrib['href'])

    @browsing
    def test_teaser_url_internal(self, browser):
        intids = getUtility(IIntIds)
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(internal_link=RelationValue(
                               intids.getId(self.page)))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(open_image_in_overlay=True))

        browser.login().visit(block, view='@@block_view')

        self.assertEquals(
            self.page.absolute_url(),
            browser.css('h2 a').first.attrib['href'])

        self.assertEquals(
            self.page.absolute_url(),
            browser.css('.sl-image a').first.attrib['href'])

    @browsing
    def test_init_scale_is_first_from_block_actions(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        browser.login().visit(block, view='@@block_view')
        self.assertEquals('sl-image sl_textblock_small left',
                          browser.css('.sl-image').first.attrib['class'])

    @browsing
    def test_change_image_scale(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        payload = {'data': json.dumps({'uid': IUUID(block), 'scale': 'large'})}
        browser.login().visit(self.page,
                              view='sl-ajax-reload-block-view',
                              data=payload)
        browser.visit(block, view='@@block_view')

        self.assertEquals('sl-image large left',
                          browser.css('.sl-image').first.attrib['class'])

    @browsing
    def test_textblock_title_not_rendered_when_empty(self, browser):
        """
        This test makes sure that the title of the block is only rendered
        if there is a title. Otherwise we'll end up with an empty HTML
        tag in the template.
        """
        textblock = create(Builder('sl textblock')
                           .titled('My textblock')
                           .having(show_title=True)
                           .within(self.page))

        browser.login().visit(self.page)

        title_css_selector = '.ftw-simplelayout-textblock h2'

        # Make sure the title is here (in its tag).
        self.assertEqual('My textblock',
                         browser.css(title_css_selector).first.text)

        # Remove the title of the block and make sure the tag is no longer
        # there.
        textblock.title = ''
        transaction.commit()
        browser.login().visit(self.page)
        self.assertEqual([], browser.css(title_css_selector))

    @browsing
    def test_image_alt_text_is_rendered(self, browser):
        """
        This test makes sure that the image's alt text is rendered in the
        template.
        """
        alt_text = u'A very nice im\xe4ge'
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(image_alt_text=alt_text))

        payload = {'data': json.dumps({'uid': IUUID(block), 'scale': 'large'})}
        browser.login().visit(self.page,
                              view='sl-ajax-reload-block-view',
                              data=payload)
        browser.visit(self.page)

        self.assertEquals(
            alt_text,
            browser.css('.ftw-simplelayout-textblock img').first.attrib['alt']
        )

    @browsing
    def test_image_alt_text_empty(self, browser):
        """
        This test makes sure that there is an alt property on the img tag
        even if no alternative text has been entered.
        """
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        payload = {'data': json.dumps({'uid': IUUID(block), 'scale': 'large'})}
        browser.login().visit(self.page,
                              view='sl-ajax-reload-block-view',
                              data=payload)
        browser.visit(block, view='@@block_view')

        self.assertEquals('', browser.css('img').first.attrib['alt'])

    @browsing
    def test_image_overlay(self, browser):
        """
        This test makes sure that the link to the overlay contains
        the url to the image to be displayed in the overlay.
        """
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(open_image_in_overlay=True,
                               ))

        browser.login().visit(block, view='@@block_view')
        link_url = browser.css('a.colorboxLink').first.attrib['href']

        browser.open(link_url)

        if IS_PLONE_5:
            self.assertEquals('image/png', browser.headers['content-type'])
        else:
            self.assertEquals('image/jpeg', browser.headers['content-type'])

    @browsing
    def test_image_overlay_when_scale_is_missing(self, browser):
        if IS_PLONE_5:
            registry = queryUtility(IRegistry)
            sizes = registry.forInterface(IImagingSchema, prefix="plone").allowed_sizes

        else:
            ptool = api.portal.get_tool('portal_properties')
            sizes = ptool.get('imaging_properties').allowed_sizes

        # Remove the colorbox scale.
        allowed_sizes = filter(lambda x: not x.startswith('colorbox'), sizes)

        if IS_PLONE_5:
            registry.forInterface(IImagingSchema, prefix="plone").allowed_sizes = allowed_sizes
        else:
            ptool.get('imaging_properties').allowed_sizes = tuple(allowed_sizes)
        transaction.commit()

        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(open_image_in_overlay=True))
        browser.login().visit(block, view='@@block_view')

        # There must be no link to the overlay since we were unable to
        # determine the url to the overlay image.
        self.assertEquals(
            [],
            browser.css('a.colorboxLink')
        )

    @browsing
    def test_auto_appending_enlarged_picture_for_overlay(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(open_image_in_overlay=True,
                               image_alt_text='Some alt text'))

        browser.login().visit(block, view='@@block_view')
        self.assertTrue(
            browser.css('a.colorboxLink').first.attrib['title'].endswith(
                'enlarged picture.'),
            'Expect "enlarged picture." hint in alt text of img.')

    @browsing
    def test_title_only_css_class(self, browser):
        create(Builder('sl textblock')
               .within(self.page)
               .titled('TextBlock title'))

        browser.login().visit(self.page)
        self.assertTrue(
            browser.css('.sl-block.titleOnly'), 'Expext title only class.')

    @browsing
    def test_data_caption_holds_caption_of_image(self, browser):
        """
        This test makes sure that there is an attribute "data-caption"
        on the link opening the colorbox and that it holds the caption
        defined on the textblock.
        """
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(image_caption=u'The caption')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif'))
                       .having(open_image_in_overlay=True,))

        browser.login().visit(block, view='@@block_view')
        self.assertEqual(
            u'The caption',
            browser.css('a.colorboxLink').first.attrib['data-caption']
        )

    def set_config(self, config={}):
        api.portal.set_registry_record(
            'image_limits', config, ISimplelayoutDefaultSettings)

        transaction.commit()

    @browsing
    def test_show_soft_limit_indicator_if_soft_limit_is_not_satisfied(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        browser.login().visit(block)
        self.assertEquals(0, len(browser.css('.softLimitIndicator')))

        self.set_config({
            block.portal_type: [
                u'soft: width={}'.format(block.image._width + 100)
            ]}
        )

        browser.visit(block)

        self.assertEquals(1, len(browser.css('.softLimitIndicator')))

    @browsing
    def test_show_hard_limit_indicator_if_hard_limit_is_not_satisfied(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        browser.login().visit(block)
        self.assertEquals(0, len(browser.css('.hardLimitIndicator')))

        self.set_config({
            block.portal_type: [
                u'hard: width={}'.format(block.image._width + 100)
            ]}
        )

        browser.visit(block)

        self.assertEquals(1, len(browser.css('.hardLimitIndicator')))

    @browsing
    def test_show_only_hard_limit_indicator_if_hard_and_soft_limit_are_not_satisfied(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        browser.login().visit(block)
        self.assertEquals(0, len(browser.css('.limitIndicator')))

        self.set_config({
            block.portal_type: [
                u'soft: width={}'.format(block.image._width + 200),
                u'hard: width={}'.format(block.image._width + 100)
            ]}
        )

        browser.visit(block)

        self.assertEquals(1, len(browser.css('.limitIndicator')))
        self.assertEquals(1, len(browser.css('.hardLimitIndicator')))

    @browsing
    def test_do_not_show_limit_indicator_if_all_limits_are_satisfied(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        browser.login().visit(block)
        self.assertEquals(0, len(browser.css('.limitIndicator')))

        self.set_config({
            block.portal_type: [
                u'soft: width={}'.format(block.image._width - 100),
                u'hard: width={}'.format(block.image._width - 200)
            ]}
        )

        browser.visit(block)
        self.assertEquals(0, len(browser.css('.limitIndicator')))

    @browsing
    def test_only_show_limit_indicator_for_editors(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        self.set_config({
            block.portal_type: [
                u'soft: width={}'.format(block.image._width + 100)
            ]}
        )

        browser.login().visit(block)
        self.assertEquals(1, len(browser.css('.limitIndicator')))

        browser.logout().visit(block)
        self.assertEquals(0, len(browser.css('.limitIndicator')))

    @browsing
    def test_limit_indicator_respects_cropped_image(self, browser):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page)
                       .with_dummy_image()
                       .with_cropped_image())

        image_limit = block.cropped_image._width + 100

        self.set_config({
            block.portal_type: [
                u'soft: width={}'.format(image_limit)
            ]}
        )

        # This only verifies the image widths for further assertions.
        # The image should be higher thant the limit and the cropped image
        # should be lower than the limit.
        self.assertGreater(block.image._width, image_limit)
        self.assertLess(block.cropped_image._width, image_limit)

        browser.login().visit(block)
        self.assertEquals(1, len(browser.css('.limitIndicator')))

    @browsing
    def test_display_corpped_image_if_available(self, browser):
        # Do not commit the transaction in this test. Otherwise the test will
        # always pass because the scaled image will be recreated even if it's
        # the same image as before the transaction.

        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page)
                       .with_dummy_image()
                       .with_cropped_image())

        block_view = block.restrictedTraverse('block_view')
        browser.open_html(block_view())

        url = browser.css('.sl-image img').first.get('src')

        block.cropped_image = None

        browser.open_html(block_view())
        self.assertNotEqual(browser.css('.sl-image img').first.get('src'), url)

    @browsing
    def test_show_cropped_image_in_overlay_if_attribute_is_set(self, browser):
        # Do not commit the transaction in this test. Otherwise the test will
        # always pass because the scaled image will be recreated even if it's
        # the same image as before the transaction.

        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page)
                       .with_dummy_image()
                       .with_cropped_image()
                       .having(
                           open_image_in_overlay=True,
                           use_cropped_image_for_overlay=False))

        block_view = block.restrictedTraverse('block_view')
        browser.open_html(block_view())

        url = browser.css('.sl-image .colorboxLink').first.get('href')

        block.use_cropped_image_for_overlay = True

        browser.open_html(block_view())

        self.assertNotEqual(browser.css('.sl-image .colorboxLink').first.get('href'), url)
