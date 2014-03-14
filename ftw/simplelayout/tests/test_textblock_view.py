from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.browser.textblock import parse_css
from ftw.simplelayout.interfaces import IDisplaySettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedBlobImage
from StringIO import StringIO
from unittest2 import TestCase
from zope.component import queryMultiAdapter


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

    def test_get_simplelayout_view(self):
        self.assertEquals('simplelayout',
                          self.view.get_simplelayout_view().__name__)


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
