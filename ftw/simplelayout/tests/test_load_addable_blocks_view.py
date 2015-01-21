from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from unittest2 import TestCase
import json


class TestAddableBlocksView(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        super(TestAddableBlocksView, self).setUp()

    def test_addable_blocks_view(self):
        page = create(Builder('sl content page'))

        view = page.restrictedTraverse('@@addable-blocks.json')

        allowed_block_types = [item['content_type']
                               for item in view.addable_blocks()]
        result = list(allowed_block_types)
        result.sort()

        self.assertEquals(
            ['ftw-simplelayout-listingblock',
             'ftw-simplelayout-textblock'],
            result)

    def test_addable_blocks_json(self):
        page = create(Builder('sl content page'))
        view = page.restrictedTraverse('@@addable-blocks.json')
        addable_types_json = json.loads(view())

        self.maxDiff = None

        self.assertDictEqual(
            {u'title': u'ListingBlock',
             u'description': u'Use this block for File or listings or galleries',
             u'content_type': u'ftw-simplelayout-listingblock',
             u'form_url': u'{0}/++add++ftw.simplelayout.ListingBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[0])

        self.assertDictEqual(
            {u'title': u'TextBlock',
             u'description': u'Use this block for text and/or one image.',
             u'content_type': u'ftw-simplelayout-textblock',
             u'form_url': u'{0}/++add++ftw.simplelayout.TextBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[1])
