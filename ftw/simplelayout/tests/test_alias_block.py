from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from plone import api
from unittest import TestCase
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import transaction


class TestAliasBlockRendering(TestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def setUp(self):
        self.page1 = create(Builder('sl content page'))
        self.page2 = create(Builder('sl content page'))
        self.textblock = create(Builder('sl textblock')
                                .titled(u'\xc4s Bl\xf6ckli')
                                .within(self.page1))

        self.intids = getUtility(IIntIds)

    @browsing
    def test_create_aliasblock(self, browser):
        alias = create(Builder('sl aliasblock')
                       .having(alias=RelationValue(
                           self.intids.getId(self.textblock)))
                       .within(self.page2))

        browser.visit(self.page2)
        block_elements = browser.visit(alias).css('.sl-alias-block')

        self.assertEqual(len(block_elements), 1)

    @browsing
    def test_add_aliasblock_using_factoriesmenu(self, browser):
        browser.login().visit(self.page2)
        factoriesmenu.add('AliasBlock')

        form = browser.find_form_by_field('Alias Content')
        form.find_widget('Alias Content').fill(self.textblock)
        browser.find_button_by_label('Save').click()

        self.assertTrue(browser.css('.sl-alias-block'))

    @browsing
    def test_render_textblock_in_aliasblock(self, browser):
        create(Builder('sl aliasblock')
               .having(alias=RelationValue(
                       self.intids.getId(self.textblock)))
               .within(self.page2))

        browser.visit(self.page2)
        visit_link = browser.css('.sl-alias-block-visit-block').first.text
        textblock_title = browser.css('.sl-alias-block h2').first.text

        self.assertEqual(u'\U0001f517 Visit embedded block', visit_link)
        self.assertEqual(u'\xc4s Bl\xf6ckli', textblock_title)

    @browsing
    def test_has_message_if_referenced_block_was_deleted(self, browser):
        create(Builder('sl aliasblock')
               .having(alias=RelationValue(
                       self.intids.getId(self.textblock)))
               .within(self.page2))

        api.content.delete(obj=self.textblock, check_linkintegrity=False)
        transaction.commit()
        browser.visit(self.page2)
        block_content = browser.css('.sl-alias-block').first.text

        self.assertEqual(u'The embedded block does not exist.', block_content)

    @browsing
    def test_custom_selectable_implementation(self, browser):
        folder = create(Builder('folder')
                        .titled(u'A folder'))

        browser.login().visit(self.page1)
        factoriesmenu.add('AliasBlock')

        form = browser.find_form_by_field('Alias Content')
        form.find_widget('Alias Content').fill(folder)

        browser.find_button_by_label('Save').click()
        self.assertEquals(['There were some errors.'],
                          statusmessages.error_messages())
        self.assertEquals('Constraint not satisfied',
                          browser.css('#formfield-form-widgets-alias .error').first.text)
