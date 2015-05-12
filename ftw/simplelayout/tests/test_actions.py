from collections import OrderedDict
from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.simplelayout.interfaces import ISimplelayoutActions
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.interface import Interface


class TestBlockReloadView(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.contentpage = create(Builder('sl content page'))
        self.portal = self.layer['portal']

    def test_amount_of_default_actions(self):
        actions = getMultiAdapter((self.contentpage, self.contentpage.REQUEST),
                                  ISimplelayoutActions)

        self.assertEquals(3, len(actions.default_actions()))

    def test_default_actions_are_move_edit_and_delete(self):
        actions = getMultiAdapter((self.contentpage, self.contentpage.REQUEST),
                                  ISimplelayoutActions)

        default_actions = actions.default_actions()

        self.assertIn('move', default_actions)
        self.assertIn('edit', default_actions)
        self.assertIn('delete', default_actions)

    def test_specific_actions_are_NONE_by_default(self):
        actions = getMultiAdapter((self.contentpage, self.contentpage.REQUEST),
                                  ISimplelayoutActions)

        self.assertIsNone(actions.specific_actions())

    def test_specific_actions_for_dummy_block(self):
        self.setup_sample_block_fti(self.portal)

        class DummyBlockActions(DefaultActions):

            def specific_actions(self):
                return OrderedDict(dummy={'class': '',
                                          'title': '',
                                          'href': '',
                                          'data-scale': 'mini'})

        provideAdapter(DummyBlockActions,
                       adapts=(Interface, Interface),
                       name='sample-actions')

        actions = getMultiAdapter((self.contentpage, self.contentpage.REQUEST),
                                  ISimplelayoutActions,
                                  name='sample-actions')

        self.assertEquals(4, len(actions.actions))
        self.assertIn('dummy', actions.actions)
