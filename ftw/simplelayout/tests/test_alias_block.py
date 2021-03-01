from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.utils import IS_PLONE_5
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from lxml import etree
from plone import api
from plone.app.textfield.value import RichTextValue
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from unittest import skipUnless
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
import difflib
import json
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

    def assert_html(self, page_html, aliasblock_html):
        diff = difflib.unified_diff(
            page_html.strip().split('\n'),
            aliasblock_html.strip().split('\n'),
            fromfile='page',
            tofile='aliasblock'
        )
        output = list(diff)
        if len(output) != 0:
            self.fail('HTML differs:\n{}'.format('\n'.join(output)))

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

        browser.login().visit(self.page2)
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

        self.assertEqual(u'The content is no longer accessible to you', block_content)

    @browsing
    @skipUnless(IS_PLONE_5, 'Link integrity check for DX only works with Plone 5')
    def test_link_integrity_message_if_target_will_be_deleted(self, browser):
        create(Builder('sl aliasblock')
               .having(alias=RelationValue(
                       self.intids.getId(self.textblock)))
               .within(self.page2))

        payload = {'data': json.dumps({'block': IUUID(self.textblock)})}
        browser.login().visit(self.page1,
                              view='@@sl-ajax-delete-blocks-view',
                              data=payload)

        browser.parse(browser.json['content'])
        self.assertEquals(
            'These internal links will be broken',
            browser.css('#content-core > div p').first.text
        )

        self.assertEquals(
            'These internal links will be broken',
            browser.css('#content-core > div p').first.text
        )

        self.assertEquals(
            u'AliasBlock: "{}"'.format(self.textblock.Title().decode('utf-8')),
            browser.css('#content-core > div ul li a').first.text
        )

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
        self.assertEquals('The selected content cannot be selected',
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
        self.assertEquals('The selected ContentPage contains a Aliasblock or is the '
                          'page you are creating the block on and thus cannot be selected',
                          browser.css('#formfield-form-widgets-alias .error').first.text)

    @browsing
    def test_dont_allow_creating_block_on_current_page(self, browser):
        browser.login().visit(self.page1)
        factoriesmenu.add('AliasBlock')

        form = browser.find_form_by_field('Alias Content')
        form.find_widget('Alias Content').fill(self.page1)

        browser.find_button_by_label('Save').click()
        self.assertEquals(['There were some errors.'],
                          statusmessages.error_messages())
        self.assertEquals('The selected ContentPage contains a Aliasblock or is the '
                          'page you are creating the block on and thus cannot be selected',
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
        self.assert_html(html_page1_layout1, html_aliasblock_layout1)

    @browsing
    def test_respect_view_permission(self, browser):
        alias = create(Builder('sl aliasblock')
                       .having(alias=RelationValue(
                           self.intids.getId(self.textblock)))
                       .within(self.page2))

        self.page1.manage_permission('View', roles=[])
        self.page1.reindexObjectSecurity()
        transaction.commit()
        browser.login().visit(self.page2)
        self.assertEquals('The content is no longer accessible to you',
                          browser.css('.sl-alias-block p').first.text)

    @browsing
    def test_google_api_key_is_on_add_and_edit_form(self, browser):
        browser.login().visit(self.page2, view='++add_block++ftw.simplelayout.AliasBlock')
        browser.parse(browser.json['content'])
        self.assertTrue(browser.css('[data-googlejs]'), 'Googlejs should be there.')

        aliasblock = create(Builder('sl aliasblock')
                            .having(alias=RelationValue(
                                self.intids.getId(self.textblock)))
                            .within(self.page2))

        browser.visit(aliasblock, view='edit.json')
        browser.parse(browser.json['content'])
        self.assertTrue(browser.css('[data-googlejs]'), 'Googlejs should be there.')
