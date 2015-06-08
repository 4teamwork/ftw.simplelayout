from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from plone.uuid.interfaces import IUUID
from Products.contentmigration.basemigrator.walker import CatalogWalker
from Products.contentmigration.basemigrator.walker import HAS_LINGUA_PLONE
from Products.contentmigration.basemigrator.walker import LOG
from Products.contentmigration.basemigrator.walker import registerWalker
from Products.contentmigration.basemigrator.walker import Walker
from ftw.simplelayout.interfaces import ISimplelayout


def migrate(portal, migrator):
    """return a CatalogWalker instance in order
    to have its output after migration"""
    walker = CatalogWalker(portal, migrator)()
    return walker


class BlockMixin():

    def migrate_simplelayout_block_state(self):
        old_image_layout = self.old.__annotations__.get('imageLayout', 'small')
        config = IBlockConfiguration(self.new)
        configdata = config.load()

        if old_image_layout == 'small':
            configdata['scale'] = 'mini'
            configdata['imagefloat'] = 'left'

        if old_image_layout == 'middle':
            configdata['scale'] = 'preview'
            configdata['imagefloat'] = 'left'

        if old_image_layout in ['full', 'no-image']:
            configdata['scale'] = 'large'
            configdata['imagefloat'] = 'no-float'

        if old_image_layout == 'middle-right':
            configdata['scale'] = 'preview'
            configdata['imagefloat'] = 'right'

        if old_image_layout == 'small-right':
            configdata['scale'] = 'mini'
            configdata['imagefloat'] = 'right'

        config.store(configdata)

    def migrate_block_slot_column_position(self):
        page = self.new.aq_parent
        config = IPageConfiguration(page)
        page_config = config.load()
        if len(page_config['default']) == 1 and len(page_config['default'][0]['cols']) == 1:
            # Do nothing, the block order is already OK (positionInParent)
            pass
        elif len(page_config['default']) == 1 and len(page_config['default'][0]['cols']) == 2:
            # Two columns one container and on layout
            if getattr(self.old, '_simplelayout_slot') == 'A':
                page_config['default'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif getattr(self.old, '_simplelayout_slot') == 'B':
                page_config['default'][0]['cols'][1]['blocks'].append(
                    {'uid': IUUID(self.new)})
            else:
                pass

        elif len(page_config['default']) == 2:
            # Two layouts, one containter. Firs layout has one column and the
            # second layout has two columns

            if getattr(self.old, '_simplelayout_slot') == 'A':
                # First layout, column one (the only column)
                page_config['default'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif getattr(self.old, '_simplelayout_slot') == 'B':
                # Second layout, first column
                page_config['default'][1]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif getattr(self.old, '_simplelayout_slot') == 'C':
                # Second layout, second column
                page_config['default'][1]['cols'][1]['blocks'].append(
                    {'uid': IUUID(self.new)})

            else:
                pass

        if len(page_config.keys()) == 2:
            # Assume there is one more container called additional
            if getattr(self.old, '_simplelayout_slot') == 'D':
                page_config['additional'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

        config.store(page_config)
