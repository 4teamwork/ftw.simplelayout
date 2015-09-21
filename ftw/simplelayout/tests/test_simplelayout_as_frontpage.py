from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
import transaction


class TestSimplelayoutAsFrontPage(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

        # Make sample block addable on plone root
        types_tool = self.portal.portal_types
        plonesite_fti = types_tool.get('Plone Site')
        addable_types = list(plonesite_fti.allowed_content_types)

        plonesite_fti.allowed_content_types = tuple(
            addable_types + ['ftw.simplelayout.tests.test_ajax_change_block_view.ISampleDX'])
        transaction.commit()

    @browsing
    def test_simplelayout_on_plone_root(self, browser):
        create(Builder('sample block'))
        browser.login().visit(view='@@simplelayout-view')
        self.assertTrue(browser.css('.sl-block-content'))

    def test_addable_types_on_plone_root(self):

        view = self.portal.restrictedTraverse('@@sl-toolbox-view')

        result = [item.get('contentType')
                  for item in list(view.addable_blocks())]

        result.sort()

        self.assertEquals(
            ['sampleblock'],
            result)
