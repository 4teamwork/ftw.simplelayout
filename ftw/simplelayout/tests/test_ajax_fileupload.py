from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.namedfile.file import NamedBlobImage
from plone.uuid.interfaces import IUUID
from StringIO import StringIO
from unittest2 import TestCase
from zExceptions import BadRequest
from zope.component import getMultiAdapter


class TestAjaxFileUploadView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))

    def test_no_contenttype(self):
        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-file-upload')

        with self.assertRaises(BadRequest):
            upload()

    def test_no_content(self):
        self.page.REQUEST.set('contenttype', 'ftw.simplelayout.TextBlock')
        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-file-upload')

        with self.assertRaises(BadRequest):
            upload()

    def test_upload_block_with_image(self):
        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')  # 1x1 px gif

        image.filename = 'test.gif'
        self.page.REQUEST.set('file', image)
        self.page.REQUEST.set('filename', 'test.gif')
        self.page.REQUEST.set('contenttype', 'ftw.simplelayout.TextBlock')

        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-file-upload')

        upload()

        block = self.page['test.gif']

        self.assertTrue(isinstance(block.image, NamedBlobImage))
        self.assertEquals(1, block.image._width)
        self.assertEquals(1, block.image._height)
        self.assertEquals(image.filename, block.image.filename)

    def test_upload_filename_starting_with_underscore(self):
        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')  # 1x1 px gif

        image.filename = '_test.gif'
        self.page.REQUEST.set('file', image)
        self.page.REQUEST.set('filename', '_test.gif')
        self.page.REQUEST.set('contenttype', 'ftw.simplelayout.TextBlock')

        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-file-upload')

        upload()

        self.assertIn('test.gif', self.page.objectIds())

    def test_create_diffrent_contenttype(self):
        listingblock = create(Builder('sl listingblock').within(self.page))
        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')  # 1x1 px gif

        image.filename = 'test.gif'
        listingblock.REQUEST.set('file', image)
        listingblock.REQUEST.set('filename', 'test.gif')
        listingblock.REQUEST.set('contenttype', 'ftw.simplelayout.File')

        upload = getMultiAdapter(
            (listingblock, listingblock.REQUEST),
            name='sl-ajax-file-upload')

        upload()
        file_ = listingblock['test.gif']

        self.assertEquals('ftw.simplelayout.File', file_.portal_type)

    def test_upload_in_given_parent(self):
        listingblock = create(Builder('sl listingblock').within(self.page))

        image = StringIO(
            'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00'
            '\x00!\xf9\x04\x04\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00'
            '\x01\x00\x00\x02\x02D\x01\x00;')  # 1x1 px gif

        image.filename = '_test.gif'
        self.page.REQUEST.set('file', image)
        self.page.REQUEST.set('filename', '_test.gif')
        self.page.REQUEST.set('contenttype', 'ftw.simplelayout.File')
        self.page.REQUEST.set('container_uuid', IUUID(listingblock))

        upload = getMultiAdapter(
            (self.page, self.page.REQUEST),
            name='sl-ajax-file-upload')

        upload()

        self.assertIn('test.gif', listingblock.objectIds())
