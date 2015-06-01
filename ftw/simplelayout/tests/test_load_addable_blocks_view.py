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

        view = page.restrictedTraverse('@@sl-ajax-addable-blocks-view')

        allowed_block_types = [item[0]
                               for item in view.addable_blocks()]
        result = list(allowed_block_types)
        result.sort()

        self.assertEquals(
            ['ftw-simplelayout-listingblock',
             'ftw-simplelayout-mapblock',
             'ftw-simplelayout-textblock',
             'ftw-simplelayout-videoblock'],
            result)

    def test_addable_blocks_json(self):
        page = create(Builder('sl content page'))
        view = page.restrictedTraverse('@@sl-ajax-addable-blocks-view')
        addable_types_json = json.loads(view())

        self.maxDiff = None

        self.assertDictEqual(
            {u'title': u'ListingBlock',
             u'description': u'Use this block for File or listings or galleries',
             u'contentType': u'ftw-simplelayout-listingblock',
             u'actions': {u'delete': {u'class': u'delete icon-delete',
                                      u'href': u'./sl-ajax-delete-blocks-view',
                                      u'title': u'Delete block'},
                          u'edit': {u'class': u'edit icon-edit',
                                    u'href': u'./sl-ajax-edit-block-view',
                                    u'title': u'Edit block'},
                          u'move': {u'class': u'move icon-move', u'title': u'Move block'}},
             u'formUrl': u'{0}/++add_block++ftw.simplelayout.ListingBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[u'ftw-simplelayout-listingblock'])

        self.assertDictEqual(
            {u'title': u'TextBlock',
             u'description': u'Use this block for text and/or one image.',
             u'contentType': u'ftw-simplelayout-textblock',
             u'actions': {u'delete': {u'class': u'delete icon-delete',
                                      u'href': u'./sl-ajax-delete-blocks-view',
                                      u'title': u'Delete block'},
                          u'edit': {u'class': u'edit icon-edit',
                                    u'href': u'./sl-ajax-edit-block-view',
                                    u'title': u'Edit block'},
                          u'image': {u'class': u'icon-image server-action',
                                     u'data-scale': u'large',
                                     u'data-imagefloat': u'no-float',
                                     u'href': u'./sl-ajax-reload-block-view',
                                     u'title': u'Image without floating'},
                          u'imageLeft': {u'class': u'icon-image-left server-action',
                                         u'data-scale': u'mini',
                                         u'data-imagefloat': u'left',
                                         u'href': u'./sl-ajax-reload-block-view',
                                         u'title': u'Float image left'},
                          u'imageLeftLarge': {u'class': u'icon-image-left-large server-action',
                                              u'data-scale': u'preview',
                                              u'data-imagefloat': u'left',
                                              u'href': u'./sl-ajax-reload-block-view',
                                              u'title': u'Float large image left'},
                          u'imageRight': {u'class': u'icon-image-right server-action',
                                          u'data-scale': u'mini',
                                          u'data-imagefloat': u'right',
                                          u'href': u'./sl-ajax-reload-block-view',
                                          u'title': u'Float image right'},
                          u'imageRightLarge': {u'class': u'icon-image-right-large server-action',
                                               u'data-scale': u'preview',
                                               u'data-imagefloat': u'right',
                                               u'href': u'./sl-ajax-reload-block-view',
                                               u'title': u'Float large image right'},
                          u'move': {u'class': u'move icon-move',
                                    u'title': u'Move block'}},
             u'formUrl': u'{0}/++add_block++ftw.simplelayout.TextBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[u'ftw-simplelayout-textblock'])
