from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from plone.app.textfield.value import RichTextValue
import transaction


class TestSearchableTextIndexer(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup_sample_ftis(self.portal)
        self.setup_block_views()
        transaction.commit()

        self.contentpage = create(Builder('sample container')
                                  .titled(u'ContentPage'))
        self.textblock = create(Builder('sample block')
                                .titled(u'TextBlock')
                                .within(self.contentpage)
                                .having(text=RichTextValue(u'asdf')))

    def search_for(self, term, path=None):
        query = {'SearchableText': term,
                 'portal_type': 'SampleContainer'}
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

    def test_searchable_text_is_up_to_date_on_delete(self):
        self.contentpage.manage_delObjects(['textblock'])
        result = self.search_for('asdf')
        self.assertEquals(0, len(result), 'Expect no entry')

    def test_searchable_text_is_up_to_date_on_move(self):
        second_page = create(Builder('sample container')
                             .titled(u'ContentPage2'))

        cut = self.contentpage.manage_cutObjects([self.textblock.getId()])
        second_page.manage_pasteObjects(cut)

        result = self.search_for('asdf')
        self.assertEquals(result[0].getURL(), second_page.absolute_url())

    def test_searchable_text_is_up_to_date_on_copy(self):
        second_page = create(Builder('sample container')
                             .titled(u'ContentPage2'))

        copy = self.contentpage.manage_copyObjects([self.textblock.getId()])
        second_page.manage_pasteObjects(copy)

        result = self.search_for('asdf')
        self.assertEquals(2, len(result), 'Expect 2 brains.')
