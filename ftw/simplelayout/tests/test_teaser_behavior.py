from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.behaviors import ITeaser
# from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
# from ftw.testbrowser import browsing
# from ftw.testbrowser.pages import factoriesmenu
# from ftw.testbrowser.pages import statusmessages
from unittest2 import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
# from ftw.testbrowser.widgets import autocomplete


class TestTeaserBehavior(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page'))
        self.intids = getUtility(IIntIds)

    def test_textblock_has_internal_link_and_external_link_field(self):
        textblock = create(Builder('sl textblock')
                           .within(self.page)
                           .having(external_link='http://www.4teamwork.ch')
                           .having(internal_link=RelationValue(
                                   self.intids.getId(self.page))))

        self.assertEquals('http://www.4teamwork.ch',
                          ITeaser(textblock).external_link)
        self.assertEquals(self.page,
                          ITeaser(textblock).internal_link.to_object)

# class TestSampleTypes(TestCase):

#     layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

#     def setUp(self):
#         self.page = create(Builder('sl content page'))

#     @browsing
#     def test_form_invariant(self, browser):
#         browser.login().visit(self.page)
#         factoriesmenu.add('TextBlock')
#         browser.fill({'External URL': 'http://www.4teamwork.ch',
#                       'Internal link': self.page})

#         browser.find_button_by_label('Save').click()
#         self.assertEquals('', statusmessages.error_messages)

