from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.trash.trasher import Trasher
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID


class TestTrashIntegration(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestTrashIntegration, self).setUp()
        self.setup_sample_ftis(self.layer['portal'])

    def test_requires_modify_portal_content_permission_for_restoring_blocks(self):
        """ftw.trash by default requires the "Add portal content" permission on the
        parent of an object in order to restore the object.
        For simplelayout blocks we want a different behavior: since we consider blocks
        to be part of the content of their page, restoring blocks should only work when
        the user has the "Modify portal content" permission.
        We wouldn't want users to be able to restore blocks of published pages, the user
        would need to retract or revise the page first.
        """

        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])

        page = create(Builder('sample container'))
        block = create(Builder('sample block').within(page))
        Trasher(block).trash()

        # Make sure that the default behavior does not apply by removing the
        # add portal content permission from the user.
        page.manage_permission('Add portal content', roles=[], acquire=False)

        page.manage_permission('Modify portal content', roles=['Manager'], acquire=False)
        self.assertTrue(Trasher(block).is_restorable())

        page.manage_permission('Modify portal content', roles=[], acquire=False)
        self.assertFalse(Trasher(block).is_restorable())
