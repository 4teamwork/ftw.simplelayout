from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from Products.CMFPlone.utils import _createObjectByType
from plone.testing.z2 import Browser
from unittest2 import TestCase
import transaction


class TestSimplelayoutView(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutView, self).setUp()

        portal = self.layer['portal']
        self.context = portal.get(portal.invokeFactory(
                'Page', 'test-simplelayout-view'))

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
        paragraph = self.context.get(self.context.invokeFactory(
            'Paragraph', 'first-paragraph', title='First Paragraph',
            text='the paragraph text'))
        paragraph.reindexObject()

        ignored_file = _createObjectByType(
            'File', self.context, id='datii', title='Datii')

        ignored_file.reindexObject()

        transaction.commit()

        self.browser.open(self.url)
        self.assertEqual(self.browser.url, self.url)
        self.assertIn('the paragraph text', self.browser.contents)
        self.assertNotIn('First Paragraph', self.browser.contents)
        self.assertNotIn('Datii', self.browser.contents)

        paragraph.setShowTitle(True)
        transaction.commit()

        self.browser.open(self.url)
        self.assertEqual(self.browser.url, self.url)
        self.assertIn('First Paragraph', self.browser.contents)
