from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.portlets.portlet import Assignment
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.app.textfield.value import RichTextValue
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletManager
from plone.uuid.interfaces import IUUID
from zope.component import getMultiAdapter
from zope.component import getUtility
import transaction


class TestSimplelayoutPortlet(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()

        self.container = create(Builder('sample container'))
        self.block = create(Builder('sample block')
                            .titled('TextBlock title')
                            .within(self.container)
                            .having(text=RichTextValue('The text'))
                            )

        create(Builder('sample block')
               .titled('TextBlock not in portlet')
               .within(self.container)
               )

    def setup_portlet(self, manager='plone.rightcolumn'):
        manager = getUtility(IPortletManager, name=manager)
        mapping = getMultiAdapter((self.container, manager),
                                  IPortletAssignmentMapping)
        mapping['sl-portlet'] = Assignment()
        transaction.commit()

    def setup_block(self, container='portletright'):
        page_config = IPageConfiguration(self.container)
        page_config.store({container: [
            {
                "cols": [
                    {
                        "blocks": [
                            {
                                "uid": IUUID(self.block)
                            }
                        ]
                    }
                ]
            }]})
        transaction.commit()

    @browsing
    def test_simplelayout_portlet_on_the_right(self, browser):
        self.setup_portlet()
        self.setup_block()
        browser.login().visit(self.container)

        self.assertTrue(browser.css('.portlet.SimplelayoutPortlet'),
                        'There should be a simplelayout portlet.')

        self.assertEquals(
            'OK',
            browser.css('.portlet.SimplelayoutPortlet .sl-block').first.text)

    @browsing
    def test_simplelayout_portlet_on_the_left(self, browser):
        self.setup_portlet(manager='plone.leftcolumn')
        self.setup_block(container='portletleft')
        browser.login().visit(self.container)

        self.assertTrue(browser.css('.portlet.SimplelayoutPortlet'),
                        'There should be a simplelayout portlet.')

        self.assertEquals(
            'OK',
            browser.css('.portlet.SimplelayoutPortlet .sl-block').first.text)

    @browsing
    def test_portlet_is_not_visible_when_empty_if_user_cannot_edit(self, browser):
        self.setup_portlet()
        browser.visit(self.container)

        self.assertFalse(browser.css('.portlet.SimplelayoutPortlet'),
                         'Portlet is empty and should not be visible')

    @browsing
    def test_portlet_is_not_visible_when_empty_and_disable_border_is_true(self, browser):
        self.setup_portlet()
        browser.login().visit(self.container, data={'disable_border': 1})

        self.assertFalse(browser.css('.portlet.SimplelayoutPortlet'),
                         'Portlet is empty and should not be visible')

    def test_simplelayout_portlet_not_available_on_non_simplelayout_types(self):
        """
        This test makes sure that the simplelayout portlet is not available on
        non-simplelayout items.

        This prevents the logs from flooding with error like:

            TypeError:
                'Could not adapt',
                <ATLink at /plone/samplecontainer/link used for /plone/samplecontainer/link>,
                <InterfaceClass ftw.simplelayout.interfaces.IPageConfiguration>
        """
        self.setup_portlet()
        self.setup_block()

        # Add "Link" to addable types of "SampleContainer".
        fti = self.portal.portal_types.get('SampleContainer')
        allowed_content_types = list(fti.allowed_content_types)
        allowed_content_types += ['File']
        fti.allowed_content_types = tuple(set(allowed_content_types))
        transaction.commit()

        # Create a link below the container where the portlet is assigned.
        link = create(Builder('file').within(self.container))

        # Get the portlet renderer on the link.
        request = self.layer['request']
        view = link.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=link)
        assignment = Assignment()
        renderer = getMultiAdapter(
            (link, request, view, manager, assignment),
            IPortletRenderer
        )

        # Make sure the portlet is not available.
        self.assertFalse(renderer.available)
