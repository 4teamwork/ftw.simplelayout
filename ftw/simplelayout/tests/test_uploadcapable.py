from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.browser import uploadcapable
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from Products.ATContentTypes.interfaces.file import IATFile
from unittest2 import TestCase
from zope.component import queryAdapter


class TestUploadCapableAdapter(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestUploadCapableAdapter, self).setUp()
        self.portal = self.layer['portal']
        self.page = create(Builder('sl content page').titled(u'A page'))
        self.filelistingblock = create(Builder('sl listingblock')
                                       .within(self.page))

    def test_adapter_registration_on_listingblock(self):
        adapter = queryAdapter(self.filelistingblock, IQuickUploadFileFactory)
        self.assertIsNotNone(adapter)
        self.assertIsInstance(
            adapter, uploadcapable.FileListingQuickUploadCapableFileFactory)

    def test_portal_type_is_alway_a_file(self):
        adapter = queryAdapter(self.filelistingblock, IQuickUploadFileFactory)
        # creates
        adapter('test.jpg', None, None, None, None, None)
        contents = self.filelistingblock.listFolderContents()

        self.assertNotEqual(
            [], contents,
            "It was not possible to create the file. Please check the adapter")

        self.assertTrue(IATFile.providedBy(contents[0]))
