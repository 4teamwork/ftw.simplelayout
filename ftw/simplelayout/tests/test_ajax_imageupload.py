from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.namedfile.file import NamedBlobImage
from StringIO import StringIO
from unittest2 import TestCase
from zExceptions import BadRequest
from zope.component import getMultiAdapter


class TestAjaxImageUploadView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

    def test_no_image(self):
        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-image-upload')

        with self.assertRaises(BadRequest):
            upload()

    def test_image_upload(self):
        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')  # 1x1 px gif

        image.filename = 'test.gif'
        self.page.REQUEST.set('image', image)
        self.page.REQUEST.set('filename', 'test.gif')

        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-image-upload')

        upload()

        block = self.page['test.gif']

        self.assertTrue(isinstance(block.image, NamedBlobImage))
        self.assertEquals(1, block.image._width)
        self.assertEquals(1, block.image._height)
        self.assertEquals(image.filename, block.image.filename)

    def test_filename_starting_with_underscore(self):
        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')  # 1x1 px gif

        image.filename = '_test.gif'
        self.page.REQUEST.set('image', image)
        self.page.REQUEST.set('filename', '_test.gif')

        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-image-upload')

        upload()

        self.assertIn('test.gif', self.page.objectIds())
