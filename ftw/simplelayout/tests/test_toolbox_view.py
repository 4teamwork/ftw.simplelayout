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
        self.maxDiff = None
        browser.login().visit(self.container, view='@@sl-toolbox-view')
        response = browser.json

        self.assertEquals(
            {u'move': {u'class': u'icon-move move',
                       u'title': u'Move layout'},
             u'delete': {u'class': u'icon-delete delete',
                         u'title': u'Delete layout'},
             u'layout-reverse': {u'class': u'icon-layout-reverse reload',
                                 u'data-layoutreverse': u'layout-reverse',
                                 u'href': u'./sl-ajax-reload-layout-view',
                                 u'rules': [2, 3],
                                 u'title': u'Invert layout'},
             u'layout112': {u'class': u'icon-layout112 reload',
                            u'title': u'1-1-2 layout',
                            u'href': u'./sl-ajax-reload-layout-view',
                            u'rules': [3],
                            u'data-layout112': u'layout112'},
             u'golden-ratio': {u'class': u'icon-golden-ratio reload',
                               u'title': u'golden ratio',
                               u'href': u'./sl-ajax-reload-layout-view',
                               u'data-golden_ratio': u'golden-ratio',
                               u'rules': [2]},
             u'layout121': {u'class': u'icon-layout121 reload',
                            u'title': u'1-2-1 layout',
                            u'href': u'./sl-ajax-reload-layout-view',
                            u'data-layout121': u'layout121',
                            u'rules': [3]},
             u'layout13': {u'class': u'icon-layout13 reload',
                           u'data-layout13': u'layout13',
                           u'href': u'./sl-ajax-reload-layout-view',
                           u'rules': [2],
                           u'title': u'1-3 layout'}},
            response['layoutActions'])
