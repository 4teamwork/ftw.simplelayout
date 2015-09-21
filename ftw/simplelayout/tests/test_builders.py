from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testing import staticuid
import transaction


class TestPageBuilder(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    @staticuid('staticuid')
    def test_page_builder_with_blocks(self):
        page = create(Builder('sl content page')
                      .with_blocks(Builder('sl textblock'),
                                   Builder('sl textblock')))

        # reset transaction to verify that page state is comitted
        transaction.begin()
        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'staticuid00000000000000000000002'},
                {'uid': 'staticuid00000000000000000000003'}]}]}]},
            IPageConfiguration(page).load())
