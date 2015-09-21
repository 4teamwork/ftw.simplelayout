from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
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
