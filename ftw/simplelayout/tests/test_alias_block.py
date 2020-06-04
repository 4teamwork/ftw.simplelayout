from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from lxml import etree
from plone import api
from plone.app.textfield.value import RichTextValue
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
        self.assertEquals('The selected Content cannot be selected',
                          browser.css('#formfield-form-widgets-alias .error').first.text)

    @browsing
    def test_dont_allow_pages_with_alias_block(self, browser):
        browser.login().visit(self.page1)
        alias = create(Builder('sl aliasblock')
                       .having(alias=RelationValue(
                           self.intids.getId(self.textblock)))
                       .within(self.page2))

        browser.login().visit(self.page1)
        factoriesmenu.add('AliasBlock')

        form = browser.find_form_by_field('Alias Content')
        form.find_widget('Alias Content').fill(self.page2)

        browser.find_button_by_label('Save').click()
        self.assertEquals(['There were some errors.'],
                          statusmessages.error_messages())
        self.assertEquals('The selected ContentPage contains a Aliasblock and cannot be selected',
                          browser.css('#formfield-form-widgets-alias .error').first.text)

    @browsing
    def test_aliasblock_renders_contentpage(self, browser):
        create(Builder('sl textblock')
               .titled(u'\xc4s Bl\xf6ckli')
               .having(text=RichTextValue(u'<p>Some html</p>'))
               .within(self.page1))
        listing = create(Builder('sl listingblock')
                         .titled(u'Downloads')
                         .within(self.page1))
        create(Builder('file')
               .titled(u'A file')
               .with_dummy_content()
               .within(listing))

        create(Builder('sl videoblock')
               .having(video_url='https://youtu.be/W42x6-Wf3Cs')
               .within(self.page1))

        create(Builder('sl aliasblock')
               .having(alias=RelationValue(
                       self.intids.getId(self.page1)))
               .within(self.page2))

        browser.login().visit(self.page1)
        html_page1_layout1 = etree.tostring(
            browser.css('#content-core #default .sl-layout').first.node,
            pretty_print=True
        )
        browser.visit(self.page2)
        html_aliasblock_layout1 = etree.tostring(
            browser.css('.sl-alias-block .sl-layout').first.node,
            pretty_print=True
        )
        self.assertEquals(html_page1_layout1, html_aliasblock_layout1)
