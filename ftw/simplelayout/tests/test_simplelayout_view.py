from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from plone.testing.z2 import Browser
from unittest2 import TestCase
import transaction


class TestSimplelayoutView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()

        portal = self.layer['portal']
        self.context = portal.get(portal.invokeFactory(
                'Folder', 'test-simplelayout-view'))

        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.url = self.context.absolute_url() + '/@@simplelayout'

    def tearDown(self):
        super(TestSimplelayoutView, self).tearDown()

        portal = self.layer['portal']
        portal.manage_delObjects(['test-simplelayout-view'])

        transaction.commit()

    def test_view_renders(self):
        self.browser.open(self.url)
        self.assertEqual(self.browser.url, self.url)
