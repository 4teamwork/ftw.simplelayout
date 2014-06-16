from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.app.textfield.value import RichTextValue
from unittest2 import TestCase


class TestSearchableTextIndexer(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        super(TestSearchableTextIndexer, self).setUp()
        self.contentpage = create(Builder('sl content page')
                                  .titled(u'ContentPage'))
        self.textblock = create(Builder('sl textblock')
                                .titled(u'TextBlock')
                                .within(self.contentpage)
                                .having(text=RichTextValue(u'asdf'))
                                .having(show_title=False))

    def search_for(self, term, path=None):
        query = {'SearchableText': term,
                 'portal_type': 'ftw.simplelayout.ContentPage'}
        if path:
            query['path'] = path
        return self.layer['portal'].portal_catalog(query)

    def test_searchable_text_is_indexed_on_container(self):
        result = self.search_for('asdf')
        assert len(result) == 1, 'Expect exactly one brain'
        self.assertEquals(self.contentpage,
                          result[0].getObject(),
                          'Expect the contentpage which has a textblock with'
                          ' the text "Text"')
