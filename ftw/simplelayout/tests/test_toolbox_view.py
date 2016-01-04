from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing


class TestToolBoxView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

        self.container = create(Builder('sample container'))

    @browsing
    def test_addable_blocks(self, browser):
        browser.login().visit(self.container, view='@@sl-toolbox-view')
        response = browser.json

        self.assertEquals(
            [
                {u'formUrl': u'http://nohost/plone/samplecontainer/++add_block++SampleBlock',
                              u'contentType': u'sampleblock',
                              u'description': u'',
                              u'actions': {u'edit': {u'href': u'./sl-ajax-edit-block-view',
                                                     u'class': u'edit icon-edit',
                                                     u'title': u'Edit block'},
                                           u'move': {u'class': u'move icon-move',
                                                     u'title': u'Move block'},
                                           u'delete': {u'href': u'./sl-ajax-delete-blocks-view',
                                                       u'class': u'delete icon-delete',
                                                       u'title': u'Delete block'}},
                              u'title': u'SampleBlock'}
            ],
            response['blocks'])

    @browsing
    def test_layout_actions(self, browser):
        browser.login().visit(self.container, view='@@sl-toolbox-view')
        response = browser.json

        self.assertEquals(
            {u'move': {u'class': u'icon-move move',
                                    u'title': u'Move layout'},
                          u'delete': {u'class': u'icon-delete delete',
                                      u'title': u'Delete layout'}},
            response['layoutActions'])
