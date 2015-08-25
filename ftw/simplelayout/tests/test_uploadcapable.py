from collective.quickupload.interfaces import IQuickUploadFileFactory
from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.contenttypes.browser import uploadcapable
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
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
        upload = queryAdapter(self.filelistingblock, IQuickUploadFileFactory)
        upload('test.jpg',
               'File title',
               'File description',
               'image/jpeg',
               'DATA',
               None)  # portal_type should be forced as 'File'.
        contents = self.filelistingblock.listFolderContents()

        self.assertEquals(1, len(contents), 'Expect exactly one item')
