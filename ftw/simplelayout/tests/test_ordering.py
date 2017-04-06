from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.configuration import columns_in_config
from ftw.simplelayout.configuration import synchronize_page_config_with_blocks
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase


class TestOrdering(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def test_blocks_are_ordered_by_simplelayout_order(self):
        page = create(
            Builder('sl content page').titled(u'Page')
            .with_blocks(Builder('sl textblock').titled(u'Block 1'),
                         Builder('sl textblock').titled(u'Block 2')))

        self.assert_order(page, 'block-1', 'block-2')
        self.reverse_sl_block_order(page)
        self.assert_order(page, 'block-2', 'block-1')

    def test_non_blocks_are_ordered_normally(self):
        page = create(
            Builder('sl content page').titled(u'Page')
            .with_blocks(Builder('sl content page').titled(u'Page 1'),
                         Builder('sl content page').titled(u'Page 2')))

        self.assert_order(page, 'page-1', 'page-2')
        page.getOrdering().moveObjectsToTop(['page-2'])
        self.assert_order(page, 'page-2', 'page-1')

    def test_changing_blocks_moves_them_to_top(self):
        page = create(
            Builder('sl content page').titled(u'Page')
            .with_blocks(Builder('sl textblock').titled(u'Block 1'),
                         Builder('sl content page').titled(u'Page 1'),
                         Builder('sl textblock').titled(u'Block 2'),
                         Builder('sl content page').titled(u'Page 2')))

        self.assert_order(page, 'block-1', 'block-2', 'page-1', 'page-2')
        page.getOrdering().moveObjectsToTop(['page-2'])
        self.assert_order(page, 'page-2', 'block-1', 'block-2', 'page-1')
        self.reverse_sl_block_order(page)
        self.assert_order(page, 'block-2', 'block-1', 'page-2', 'page-1')

    def test_orering_on_site_root(self):
        portal = self.layer['portal']
        create(Builder('sl textblock').titled(u'Block 1').within(portal))
        create(Builder('sl textblock').titled(u'Block 2').within(portal))
        synchronize_page_config_with_blocks(portal)

        self.assertEquals(['block-1', 'block-2'],
                          filter(lambda id_: id_.startswith('block'),
                                 portal.objectIds()))
        self.reverse_sl_block_order(portal)
        self.assertEquals(['block-2', 'block-1'],
                          filter(lambda id_: id_.startswith('block'),
                                 portal.objectIds()))

    def reverse_sl_block_order(self, container):
        config = IPageConfiguration(container).load()
        for column in columns_in_config(config):
            column['blocks'].reverse()

        config = IPageConfiguration(container).store(config)

    def assert_order(self, container, *child_ids):
        self.assertEquals(list(child_ids), container.objectIds())
        self.assert_positions_consistent(container)

    def assert_positions_consistent(self, container):
        """Make sure that the positions are consistently incremented.
        This is verified on order to avoid problems when using multiple
        ordering strategies in combination.
        """
        ordering = container.getOrdering()
        ids = ordering.idsInOrder()
        self.assertEquals(range(len(ids)),
                          map(ordering.getObjectPosition, ids))
