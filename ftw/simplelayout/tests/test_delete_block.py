from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
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
        self.setup_sample_ftis(self.portal)
        transaction.commit()

        self.contentpage = create(Builder('sample container'))
        # TODO test locking and link integrity (messages).

    def get_payload(self, block):
        block = IUUID(block)
        return {'data': json.dumps({'block': block})}

    @browsing
    def test_delete_block(self, browser):
        block = create(Builder('sample block').within(self.contentpage))
        browser.login().visit(self.contentpage,
                              view='@@sl-ajax-delete-blocks-view',
                              data=self.get_payload(block))

        browser.parse(browser.json['content'])

        browser.find('Delete').click()

        self.assertEquals(0, len(self.contentpage.objectValues()))


class TestRemoveBlockWithinNonSimplelayoutContainer(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

    @browsing
    def test_block_deletion_within_non_simplelayout_container(self, browser):
        """
        This tests ensures that simplelayout blocks can be deleted if they
        are container within a non-simplelayout container.
        """
        # Create a non-simplelayoutish container (this is the case with
        # a `ftw.book.Book` where we first spotted the issue).
        container = create(Builder('folder'))

        # Create a simplelayout block within a non-simplelayoutish
        # container (this is the case with `ftw.book.Chapter` created
        # within a `ftw.book Book` where we first spotted the issue).
        block = create(Builder('sample block').titled('the block').within(container))
        self.assertEqual(['the-block'], container.objectIds())

        # Now delete the block. This triggers
        # `ftw.simplelayout.handlers.update_page_state_on_block_remove` which
        # used to fail if the container was non-simplelayoutish.
        browser.login().visit(container, view='folder_contents')
        browser.visit(block, view='delete_confirmation')
        browser.find_button_by_label('Delete').click()

        # Make sure the block has gone. This is not the real goal of this
        # test. But if we get here, the deletion of the block was successful.
        self.assertEqual([], container.objectIds())
