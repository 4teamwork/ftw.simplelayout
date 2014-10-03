from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.browser.blocks.textblock import parse_css
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from StringIO import StringIO
from unittest2 import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.intid.interfaces import IIntIds


class TestTextBlockView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(image=NamedBlobImage(data=image.read(),
                                                    filename=u'test.gif')))
        self.view = block.restrictedTraverse('@@block_view')

    def test_get_default_scaled_image(self):
        # Width and height are currently hart coded  in the textblock view
        scale = self.view.get_scaled_image()
        width = self.view.calculate_min_image_width()

        self.assertEquals(('width', width), scale.key[-1])

        # The height is set to 10000, so it doesn't matters while scaling.
        self.assertEquals(('height', 10000), scale.key[-2])

    def test_scaled_image_based_on_image_styles(self):
        display = queryMultiAdapter((self.view.context, self.view.request),
                                    IDisplaySettings)

        display.set_image_styles('width:123px')

        scale = self.view.get_scaled_image()
        self.assertEquals(('width', 123), scale.key[-1])

    def test_scaled_image_based_on_image_styles_incl_height(self):
        display = queryMultiAdapter((self.view.context, self.view.request),
                                    IDisplaySettings)

        display.set_image_styles('width:123px;height:200px;')

        scale = self.view.get_scaled_image()
        self.assertEquals(('width', 123), scale.key[-1])
        self.assertEquals(('height', 200), scale.key[-2])

    def test_get_simplelayout_view(self):
        self.assertEquals('simplelayout-view',
                          self.view.get_simplelayout_view().__name__)

    def test_get_default_image_wrapper_css_class(self):
        self.assertEquals('sl-img-wrapper float-image-none',
                          self.view.get_image_wrapper_css_class())

    def test_get_change_image_wrapper_css_class(self):
        display = queryMultiAdapter((self.view.context, self.view.request),
                                    IDisplaySettings)

        display.set_image_styles('width:123px;float:left')

        self.assertEquals('sl-img-wrapper float-image-left',
                          self.view.get_image_wrapper_css_class())

    def test_imag_tag(self):
        display = queryMultiAdapter((self.view.context, self.view.request),
                                    IDisplaySettings)

        display.set_image_styles('width:123px;height:200px;')
        img_tag = self.view.img_tag()

        self.assertIn('title="TextBlock title"',
                      img_tag,
                      'Title attribute is wrong or not set.')
        self.assertIn('alt="TextBlock title"',
                      img_tag,
                      'Title attribute is wrong or not set.')
        self.assertIn('width="1"',
                      img_tag,
                      'width attribute is wrong or not set.')
        self.assertIn('height="1"',
                      img_tag,
                      'Height attribute is wrong or not set.')
        self.assertIn('style="width:123px;height:200px;"',
                      img_tag,
                      'Style attribute is wrong or not set.')
        self.assertIn(
            'src="{0}/@@images'.format(self.view.context.absolute_url()),
            img_tag,
            'Src attribute is wrong or not set.')


class TestTextBlockRendering(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

        self.image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')

    @browsing
    def test_teaser_url_external(self, browser):
        block = create(Builder('sl textblock')
                       .within(self.page)
                       .titled('TextBlock title')
                       .having(text=RichTextValue('The text'))
                       .having(external_link='http://www.4teamwork.ch')
                       .having(image=NamedBlobImage(data=self.image.read(),
                                                    filename=u'test.gif')))

        browser.login().visit(block, view='@@block_view')
        self.assertEquals(
            'http://www.4teamwork.ch',
            browser.css('[data-simplelayout-url]').first.attrib['data-simplelayout-url'])
        self.assertTrue(browser.css('img[data-simplelayout-url]'),
                        'No linked image found')

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
                                                    filename=u'test.gif')))

        browser.login().visit(block, view='@@block_view')
        self.assertEquals(self.page.absolute_url(),
                          browser.css('[data-simplelayout-url]').first.attrib[
                              'data-simplelayout-url'])
        self.assertTrue(browser.css('img[data-simplelayout-url]'),
                        'No linked image found')


class TestCssStyleParser(TestCase):

    def test_strip_px(self):
        styles = 'float:left;width:500px'
        self.assertEquals('500', parse_css(styles, 'width'))

    def test_get_attr(self):
        styles = 'float:left;width:500px'
        self.assertEquals('left', parse_css(styles, 'float'))

    def test_no_attr(self):
        styles = 'float:left;width:500px'
        self.assertIsNone(parse_css(styles, 'height'))
