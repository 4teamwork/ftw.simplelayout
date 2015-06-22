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


class ImageBlockWalker(Walker):
    """Custom catalog walker for image blocks, but it does not touch other
    images."""

    def walk(self):

        catalog = self.catalog
        query = {
            'portal_type': self.src_portal_type,
            'meta_type': self.src_meta_type,
            'path': "/".join(self.portal.getPhysicalPath()),
        }
        if HAS_LINGUA_PLONE and 'Language' in catalog.indexes():
            query['Language'] = 'all'

        brains = catalog(query)
        limit = getattr(self, 'limit', False)
        if limit:
            brains = brains[:limit]

        for brain in brains:
            try:
                obj = brain.getObject()
            except AttributeError:
                LOG.error("Couldn't access %s" % brain.getPath())
                continue
            try:
                state = obj._p_changed
            except:
                state = 0
            if obj is not None:
                # Only yield if parent is a simplelayout page.
                if ISimplelayout.providedBy(obj.aq_parent):
                    yield obj
                    # safe my butt
                    if state is None:
                        obj._p_deactivate()

registerWalker(ImageBlockWalker)


def migrate_image_blocks(portal, migrator):
    walker = ImageBlockWalker(portal, migrator)()
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

        slot = getattr(self.old, '_simplelayout_slot', None)

        if len(page_config['default']) == 1 and len(page_config['default'][0]['cols']) == 1:
            # Do nothing, the block order is already OK (positionInParent)
            pass
        elif len(page_config['default']) == 1 and len(page_config['default'][0]['cols']) == 2:
            # Two columns one container and on layout
            if slot == 'A':
                page_config['default'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif slot == 'B':
                page_config['default'][0]['cols'][1]['blocks'].append(
                    {'uid': IUUID(self.new)})
            else:
                pass

        elif len(page_config['default']) == 2:
            # Two layouts, one containter. Firs layout has one column and the
            # second layout has two columns

            if slot == 'A':
                # First layout, column one (the only column)
                page_config['default'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif slot == 'B':
                # Second layout, first column
                page_config['default'][1]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

            elif slot == 'C':
                # Second layout, second column
                page_config['default'][1]['cols'][1]['blocks'].append(
                    {'uid': IUUID(self.new)})

            else:
                pass

        if len(page_config.keys()) == 2:
            # Assume there is one more container called additional
            if slot == 'D':
                page_config['additional'][0]['cols'][0]['blocks'].append(
                    {'uid': IUUID(self.new)})

        config.store(page_config)
