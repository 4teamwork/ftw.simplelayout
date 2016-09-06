from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.simplelayout.testing import SimplelayoutTestCase
from zope.component import getUtility
from plone.dexterity.interfaces import IDexterityFTI


class TestTextBlockRendering(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

        self.setup_sample_ftis(self.portal)
        self.setup_block_views()
        fti = getUtility(IDexterityFTI, name='SampleContainer')
        behaviors = list(fti.behaviors)
        behaviors.append('ftw.simplelayout.interfaces.IContentPageShowTitle')
        fti.behaviors = tuple(behaviors)

        self.page = create(Builder('sample container').titled(u'A page'))

    @browsing
    def test_title_doesnt_show_if_show_title_is_false(self, browser):
        browser.login().visit(self.page, view='edit')

        form = browser.find_form_by_field('Show title')
        form.css('input[type="checkbox"]')[0].checked = False
        form.submit()

        self.assertFalse(
            browser.css('.documentFirstHeading').text)

    @browsing
    def test_title_shows_if_show_title_is_true(self, browser):
        browser.login().visit(self.page)

        self.assertEqual(
            ['A page'],
            browser.css('.documentFirstHeading').text)
