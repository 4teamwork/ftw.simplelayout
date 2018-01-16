from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import IS_PLONE_5
from ftw.testbrowser import browsing
from unittest2 import skipUnless
from unittest2 import TestCase
import transaction


@skipUnless(not IS_PLONE_5, 'requires plone < 5')
class TestMapBlock(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        super(TestMapBlock, self).setUp()
        self.portal = self.layer['portal']
        self.page = create(Builder('sl content page').titled(u'A page'))

    @browsing
    def test_mapblock_title_is_rendered_by_default(self, browser):
        block = create(Builder('sl mapblock')
                       .titled('My mapblock')
                       .within(self.page))

        browser.login().visit(self.page)

        title_css_selector = '.ftw-simplelayout-mapblock h2'

        # The title is rendered by default.
        self.assertEqual('My mapblock',
                         browser.css(title_css_selector).first.text)

        # Disable the rendering of the title.
        browser.visit(block, view='edit')
        browser.fill({'Show title': False}).save()
        self.assertEqual([], browser.css(title_css_selector))

    @browsing
    def test_mapblock_title_not_rendered_when_empty(self, browser):
        """
        Makesure that the title of the block is only rendered
        if there is a title. Otherwise we'll end up with an empty HTML
        tag in the template.
        """
        block = create(Builder('sl mapblock')
                       .titled('My mapblock')
                       .within(self.page))

        browser.login().visit(self.page)

        title_css_selector = '.ftw-simplelayout-mapblock h2'

        # The title is rendered by default.
        self.assertEqual('My mapblock',
                         browser.css(title_css_selector).first.text)

        # Remove the title of the block and make sure the tag is no longer
        # there.
        block.title = ''
        transaction.commit()
        browser.login().visit(self.page)
        self.assertEqual([], browser.css(title_css_selector))
