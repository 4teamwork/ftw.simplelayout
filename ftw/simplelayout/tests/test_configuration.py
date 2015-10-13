from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.configuration import block_uids_in_page
from ftw.simplelayout.configuration import block_uids_missing_in_config
from ftw.simplelayout.configuration import columns_in_config
from ftw.simplelayout.configuration import flattened_block_uids
from ftw.simplelayout.configuration import synchronize_page_config_with_blocks
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.testing import staticuid
from zExceptions import Unauthorized
from zope.interface.verify import verifyObject


class TestPageConfiguration(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestPageConfiguration, self).setUp()
        self.setup_sample_ftis(self.layer['portal'])

    def test_implements_interface(self):
        config = IPageConfiguration(create(Builder('sample container')))
        verifyObject(IPageConfiguration, config)

    def test_setting_and_loading_config(self):
        config = IPageConfiguration(create(Builder('sample container')))
        config.store(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]}]}
        )
        self.assertEquals(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]}]},
            config.load())

        config.store(
            {'default': [{'cols': [{'blocks': [{'uid': 'bar'}]}]}]}
        )
        self.assertEquals(
            {'default': [{'cols': [{'blocks': [{'uid': 'bar'}]}]}]},
            config.load())

    def test_config_is_recursive_persistent(self):
        config = IPageConfiguration(create(Builder('sample container')))
        config.store(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]}]}
        )
        self.assert_recursive_persistence(config.load())

    def test_default_config_is_recursive_persistent(self):
        config = IPageConfiguration(create(Builder('sample container')))
        self.assert_recursive_persistence(config.load())

    def test_loaded_config_mutations_are_not_stored(self):
        config = IPageConfiguration(create(Builder('sample container')))
        config.store(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]}]}
        )

        config.load()['default'][0]['cols'][0]['blocks'].append(
            {'uid': 'bar'})

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]}]},
            config.load())

    def test_unauthorized_when_not_allowed_to_change_layouts(self):
        page = create(Builder('sample container'))
        config = IPageConfiguration(page)
        config.store(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'},
                                               {'uid': 'bar'}]}]},
                         {'cols': [{'blocks': []},
                                   {'blocks': []}]}]}
        )

        # The user should not change layouts
        page.manage_permission('ftw.simplelayout: Change Layouts',
                               roles=[],
                               acquire=0)

        # When he changes layouts, Unauthorized is raised
        with self.assertRaises(Unauthorized):
            config.store(
                {'default': [{'cols': [{'blocks': [{'uid': 'foo'},
                                                   {'uid': 'bar'}]}]}]}
            )

        # But he is allowed to move blocks
        config.store(
            {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]},
                         {'cols': [{'blocks': [{'uid': 'bar'}]},
                                   {'blocks': []}]}]}
        )


class TestPageConfigFunctions(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestPageConfigFunctions, self).setUp()
        self.setup_sample_ftis(self.layer['portal'])

    def test_column_blocks_in_config(self):
        config = {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]},
                              {'cols': [{'blocks': [{'uid': 'bar'}]},
                                        {'blocks': []}]}],
                  'sidebar': [{'cols': [{'blocks': [{'uid': 'baz'},
                                                    {'uid': 'foobar'}]}]}]}

        self.assertEquals(
            [{'blocks': [{'uid': 'foo'}]},
             {'blocks': [{'uid': 'bar'}]},
             {'blocks': []},
             {'blocks': [{'uid': 'baz'}, {'uid': 'foobar'}]}],
            columns_in_config(config))

    def test_flattened_block_uids(self):
        config = {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]},
                              {'cols': [{'blocks': [{'uid': 'bar'}]},
                                        {'blocks': []}]}],
                  'sidebar': [{'cols': [{'blocks': [{'uid': 'baz'},
                                                    {'uid': 'foobar'}]}]}]}

        self.assertEquals(['foo', 'bar', 'baz', 'foobar'],
                          flattened_block_uids(config))

    @staticuid('staticuid')
    def test_block_uids_in_page(self):
        page = create(Builder('sample container'))
        create(Builder('sample block').within(page))
        create(Builder('sample block').within(page))

        self.assertEquals(
            ['staticuid00000000000000000000002',
             'staticuid00000000000000000000003'],
            block_uids_in_page(page))

    @staticuid('staticuid')
    def test_block_uids_missing_in_config(self):
        page = create(Builder('sample container'))
        create(Builder('sample block').within(page))
        self.assertEquals(
            ['staticuid00000000000000000000002'],
            block_uids_missing_in_config(page))

        IPageConfiguration(page).store(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'staticuid00000000000000000000002'}]}]}]})

        create(Builder('sample block').within(page))
        create(Builder('sample block').within(page))

        self.assertEquals(
            ['staticuid00000000000000000000003',
             'staticuid00000000000000000000004'],
            block_uids_missing_in_config(page))

    @staticuid('staticuid')
    def test_synchronize_page_config_with_blocks(self):
        page = create(Builder('sample container'))

        create(Builder('sample block').within(page))
        IPageConfiguration(page).store(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'staticuid00000000000000000000002'},
                {'uid': 'staticuid00000000000000000000004'}]}]}]})

        create(Builder('sample block').within(page))

        result = synchronize_page_config_with_blocks(page)
        self.assertEquals(
            {'added': ['staticuid00000000000000000000003'],
             'removed': ['staticuid00000000000000000000004']},
            result)

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'staticuid00000000000000000000002'},
                {'uid': 'staticuid00000000000000000000003'}]}]}]},
            IPageConfiguration(page).load())

    @staticuid('staticuid')
    def test_synchronize_page_config_with_blocks_on_empty_page(self):
        page = create(Builder('sample container'))
        create(Builder('sample block').within(page))
        result = synchronize_page_config_with_blocks(page)
        self.assertEquals(
            {'added': ['staticuid00000000000000000000002'],
             'removed': []},
            result)

        self.assertEquals(
            {'default': [{'cols': [{'blocks': [
                {'uid': 'staticuid00000000000000000000002'}]}]}]},
            IPageConfiguration(page).load())

    def test_store_partial_updates(self):
        page = create(Builder('sample container'))
        config = IPageConfiguration(page)

        state = {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]},
                             {'cols': [{'blocks': [{'uid': 'bar'}]},
                                       {'blocks': []}]}],
                 'sidebar': [{'cols': [{'blocks': [{'uid': 'baz'},
                                                   {'uid': 'foobar'}]}]}]}
        config.store(state)

        partial_state = {'sidebar': [{'cols': [
            {'blocks': [{'uid': 'baz'}]}]}]}
        config.store(partial_state)

        # Remove block "foobar" from "sidebar" slot
        new_state = {'default': [{'cols': [{'blocks': [{'uid': 'foo'}]}]},
                                 {'cols': [{'blocks': [{'uid': 'bar'}]},
                                           {'blocks': []}]}],
                     'sidebar': [{'cols': [{'blocks': [{'uid': 'baz'}]}]}]}

        self.assertEquals(new_state, config.load())


class TestBlockConfiguration(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestBlockConfiguration, self).setUp()
        self.setup_sample_ftis(self.layer['portal'])

    def test_implements_interface(self):
        config = IBlockConfiguration(create(Builder('sample block')))
        verifyObject(IBlockConfiguration, config)

    def test_config_is_recursive_persistent(self):
        config = IBlockConfiguration(create(Builder('sample block')))
        config.store({'scale': 'mini'})
        self.assert_recursive_persistence(config.load())
