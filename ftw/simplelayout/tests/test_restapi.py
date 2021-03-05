from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testbrowser import browsing
from plone.uuid.interfaces import IUUID
import transaction


class TestSimplelayoutRestApi(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestSimplelayoutRestApi, self).setUp()
        self.layer['portal'].manage_permission(
            'plone.restapi: Use REST API',
            roles=['Anonymous']
        )
        self.setup_sample_ftis(self.layer['portal'])

    @browsing
    def test_page_state_is_in_response(self, browser):
        page = create(Builder('sample container'))

        config = {u'default': [{u'cols': [{u'blocks': [{u'uid': u'foo'}]}]},
                               {u'cols': [{u'blocks': [{u'uid': u'bar'}]},
                                          {u'blocks': []}]}],
                  u'sidebar': [{u'cols': [{u'blocks': [{u'uid': u'baz'},
                                                       {u'uid': u'foobar'}]}]}]}

        IPageConfiguration(page).store(config)
        transaction.commit()

        browser.open(page.absolute_url(), method='GET',
                     headers={'Accept': 'application/json'})
        self.assertDictEqual(config, browser.json['simplelayout'])

    @browsing
    def test_page_state_is_in_response_on_plone_root(self, browser):
        config = {u'default': [{u'cols': [{u'blocks': [{u'uid': u'foo'}]}]},
                               {u'cols': [{u'blocks': [{u'uid': u'bar'}]},
                                          {u'blocks': []}]}],
                  u'sidebar': [{u'cols': [{u'blocks': [{u'uid': u'baz'},
                                                       {u'uid': u'foobar'}]}]}]}

        IPageConfiguration(self.layer['portal']).store(config)
        transaction.commit()

        browser.open(self.layer['portal'].absolute_url(), method='GET',
                     headers={'Accept': 'application/json'})
        self.assertDictEqual(config, browser.json['simplelayout'])

    @browsing
    def test_blocks_are_resturned_as_uid_map(self, browser):

        page = create(Builder('sample container'))
        block1 = create(Builder('sample block').within(page))
        block2 = create(Builder('sample block').within(page))

        IPageConfiguration(page).store(
            {'default': [{'cols': [{'blocks': [
                {'uid': IUUID(block1)}, {'uid': IUUID(block2)}
            ]}]}]})
        transaction.commit()

        browser.open(page.absolute_url(), method='GET',
                     headers={'Accept': 'application/json'})

        self.assertItemsEqual(
            [IUUID(block1), IUUID(block2)],
            browser.json['slblocks'].keys()
        )

        self.assertEquals(
            'SampleBlock',
            browser.json['slblocks'][IUUID(block1)]['@type']
        )
        self.assertEquals(
            'SampleBlock',
            browser.json['slblocks'][IUUID(block2)]['@type']
        )
