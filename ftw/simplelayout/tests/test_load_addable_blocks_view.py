from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import IS_PLONE_5
from unittest2 import skipUnless
from unittest2 import TestCase
import json


@skipUnless(not IS_PLONE_5, 'requires plone < 5')
class TestAddableBlocksDefaultContent(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestAddableBlocksDefaultContent, self).setUp()

    def test_addable_blocks_view(self):
        page = create(Builder('sl content page'))

        view = page.restrictedTraverse('@@sl-toolbox-view')

        result = [item.get('contentType')
                  for item in list(view.addable_blocks())]
        result.sort()

        self.assertEquals(
            ['ftw-simplelayout-aliasblock',
             'ftw-simplelayout-filelistingblock',
             'ftw-simplelayout-galleryblock',
             'ftw-simplelayout-mapblock',
             'ftw-simplelayout-textblock',
             'ftw-simplelayout-videoblock'],
            result)

    def test_addable_blocks_json(self):
        page = create(Builder('sl content page'))
        view = page.restrictedTraverse('@@sl-toolbox-view')

        addable_types_json = json.loads(view())['blocks']

        self.maxDiff = None


        self.assertDictEqual(
            {u'title': u'TextBlock',
             u'description': u'The text block renders text and images.',
             u'contentType': u'ftw-simplelayout-textblock',
             u'actions': {u'cropping': {u'class': u'icon-crop crop-image',
                                        u'href': u'./sl-ajax-crop-image',
                                        u'title': u'Crop image'},
                          u'delete': {u'class': u'delete icon-delete',
                                      u'href': u'./sl-ajax-delete-blocks-view',
                                      u'title': u'Delete block'},
                          u'edit': {u'class': u'edit icon-edit',
                                    u'href': u'./sl-ajax-edit-block-view',
                                    u'title': u'Edit block'},
                          u'image': {u'class': u'icon-image block-server-action',
                                     u'data-scale': u'sl_textblock_large',
                                     u'data-imagefloat': u'no-float',
                                     u'href': u'./sl-ajax-reload-block-view',
                                     u'title': u'Image without floating'},
                          u'imageLeft': {u'class': u'icon-image-left block-server-action',
                                         u'data-scale': u'sl_textblock_small',
                                         u'data-imagefloat': u'left',
                                         u'href': u'./sl-ajax-reload-block-view',
                                         u'title': u'Float image left'},
                          u'imageLeftLarge': {u'class': u'icon-image-left-large block-server-action',
                                              u'data-scale': u'sl_textblock_middle',
                                              u'data-imagefloat': u'left',
                                              u'href': u'./sl-ajax-reload-block-view',
                                              u'title': u'Float large image left'},
                          u'imageRight': {u'class': u'icon-image-right block-server-action',
                                          u'data-scale': u'sl_textblock_small',
                                          u'data-imagefloat': u'right',
                                          u'href': u'./sl-ajax-reload-block-view',
                                          u'title': u'Float image right'},
                          u'imageRightLarge': {u'class': u'icon-image-right-large block-server-action',
                                               u'data-scale': u'sl_textblock_middle',
                                               u'data-imagefloat': u'right',
                                               u'href': u'./sl-ajax-reload-block-view',
                                               u'title': u'Float large image right'},
                          u'move': {u'class': u'move icon-move',
                                    u'title': u'Move block'}},
             u'formUrl': u'{0}/++add_block++ftw.simplelayout.TextBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[0])

        self.assertDictEqual(
            {u'title': u'FileListingBlock',
             u'description': u'The file listing block renders a list of uploaded files with configurable header which can be used to change the order of the listing.',
             u'contentType': u'ftw-simplelayout-filelistingblock',
             u'actions': {u'delete': {u'class': u'delete icon-delete',
                                      u'href': u'./sl-ajax-delete-blocks-view',
                                      u'title': u'Delete block'},
                          u'edit': {u'class': u'edit icon-edit',
                                    u'href': u'./sl-ajax-edit-block-view',
                                    u'title': u'Edit block'},
                          u'upload': {u'class': u'upload icon-image-upload',
                                      u'href': u'./sl-ajax-upload-block-view',
                                      u'title': u'Upload'},
                          u'folderContents': {u'class': u'icon-folder-contents redirect',
                                              u'href': u'/folder_contents',
                                              u'title': u'Go to folder contents for managing files'},
                          u'move': {u'class': u'move icon-move',
                                    u'title': u'Move block'}},
             u'formUrl': u'{0}/++add_block++ftw.simplelayout.FileListingBlock'.format(
                 page.absolute_url())
             },
            addable_types_json[1])
