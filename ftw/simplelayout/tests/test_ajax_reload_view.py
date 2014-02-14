from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
from zExceptions import BadRequest
from zope.component import getMultiAdapter


class TestAjaxReloadView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.block = create(Builder('sl textblock')
                            .within(self.page)
                            .having(text=RichTextValue('The text')))

    def test_block_reload_view(self):

        self.block.REQUEST.set('uuid', IUUID(self.block))

        view = getMultiAdapter((self.block, self.block.REQUEST),
                               name='sl-ajax-reload-block-view')
        block_view = self.block.restrictedTraverse('@@block_view')
        self.assertEqual(view(), block_view())

    def test_block_reload_view_no_uuid(self):
        view = getMultiAdapter((self.block, self.block.REQUEST),
                               name='sl-ajax-reload-block-view')

        with self.assertRaises(BadRequest):
            view()
