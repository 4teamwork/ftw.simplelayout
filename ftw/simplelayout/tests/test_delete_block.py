from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
import json
import transaction


class TestBlockDelete(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_block_fti(self.portal)
        transaction.commit()

        self.contentpage = create(Builder('sl content page'))
        # TODO test locking and link integrity (messages).

    def get_payload(self, block):
        blocks = [IUUID(block)]
        return {'data': json.dumps({'blocks': blocks})}

    @browsing
    def test_delete_block(self, browser):
        block = create(Builder('sample block').within(self.contentpage))
        browser.login().visit(self.contentpage,
                              view='@@sl-ajax-delete-blocks-view',
                              data=self.get_payload(block))

        browser.find_button_by_label('Delete').click()

        self.assertEquals(0, len(self.contentpage.objectValues()))
