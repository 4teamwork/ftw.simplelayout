from copy import deepcopy
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.interfaces import ISimplelayoutContainerConfig
from operator import itemgetter
from operator import methodcaller
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.uuid.interfaces import IUUID
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implements


SL_ANNOTATION_KEY = 'ftw.simplelayout.pageconfiguration'
BLOCK_ANNOTATION_KEY = 'ftw.simplelayout.blockconfiguration'


def make_resursive_persistent(conf):
    """Convert the given layout configuration to a rows/columns/blocks
       mapping.
    """
    # TODO: validate data

    def persist(data):
        if isinstance(data, dict):
            data = PersistentMapping(data)

            for key, value in data.items():
                data[key] = persist(value)

        elif isinstance(data, list):
            return PersistentList(map(persist, data))

        else:
            # Usually we got basestrings, or integer here, so do nothing.
            pass

        return data

    return persist(conf)


def columns_in_config(config, container=None):
    """Returns each column-dict found in the config.
    """
    columns = []

    if container is None:
        containers = config.values()
    else:
        containers = [config.get(container, [{"cols": [{"blocks": []}]}])]

    for container in containers:
        for layout in container:
            columns.extend(layout.get('cols', ()))

    return columns


def flattened_block_uids(config):
    """Accepting a page configuration, this function returns a flat list of block
    uids found in the configuration in order of appearance.
    """

    uids = []

    for column in columns_in_config(config):
        for block in column.get('blocks', ()):
            uids.append(block.get('uid'))

    return uids


def block_uids_in_page(page):
    """Returns a list of block UIDs of a page.
    """
    return map(IUUID, filter(ISimplelayoutBlock.providedBy, page.objectValues()))


def block_uids_missing_in_config(page):
    """Returns a list of UIDs of blocks, which are missing in the page's config.
    """

    in_config = flattened_block_uids(IPageConfiguration(page).load())
    return filter(lambda uid: uid not in in_config, block_uids_in_page(page))


def synchronize_page_config_with_blocks(page):
    """Updates the page config:
    - adds blocks to the config, which exist in the page but not in the config
    - removes blocks from the config, which do no longer exist in the page

    A dict with ``added`` and ``removed`` block UIDs is returned.
    """

    config = IPageConfiguration(page).load()
    columns = columns_in_config(config)
    existing_uids = block_uids_in_page(page)
    removed = []

    for column in columns:
        new_blocks = []
        for block in column.get('blocks', ()):
            if block['uid'] in existing_uids:
                new_blocks.append(block)
            else:
                removed.append(block['uid'])

        column['blocks'][:] = new_blocks

    # Add missing blocks to the bottom of the first column of the "default"
    # container.
    added = block_uids_missing_in_config(page)
    for uid in added:
        default_columns = columns_in_config(config, container='default')
        default_columns[0]['blocks'].append({'uid': uid})

    IPageConfiguration(page).store(config)
    return {'added': added, 'removed': removed}


def has_slot_layout_changed(old_data, new_data):
    old_layouts = map(len, map(itemgetter('cols'), old_data))
    new_layouts = map(len, map(itemgetter('cols'), new_data))
    return old_layouts != new_layouts


class PageConfiguration(object):
    """Adapter for storing simplelayout page configuration.
    """
    implements(IPageConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, conf, update_positions=True):
        self.check_permission(conf)
        annotations = IAnnotations(self.context)

        storage = annotations.get(SL_ANNOTATION_KEY, None)
        if storage:
            storage.update(make_resursive_persistent(conf))
        else:
            annotations[SL_ANNOTATION_KEY] = make_resursive_persistent(conf)

        if update_positions:
            self.update_object_positions()

    def load(self):
        annotations = IAnnotations(self.context)
        default_state = deepcopy(self._default_page_config())
        page_state = deepcopy(annotations.setdefault(
            SL_ANNOTATION_KEY,
            make_resursive_persistent(default_state)))

        for slotname in default_state:
            if not page_state.get(slotname):
                page_state[slotname] = default_state[slotname]

        return page_state

    def check_permission(self, new_state):
        if api.user.has_permission('ftw.simplelayout: Change Layouts',
                                   obj=self.context):
            return

        # The user does not have the permission to manipulate the
        # structure. But the new configuration is serialized from the DOM
        # So we need to check if the user has manipulated the DOM by
        # himself. This is done by checking the stored state and the new state
        # generated from the DOM.

        old_state = self.load()

        for slot_name, new_slot_state in new_state.items():
            if slot_name not in old_state:
                continue

            if has_slot_layout_changed(old_state[slot_name], new_slot_state):
                raise Unauthorized()

    def get_ordered_blocks(self):
        """Returns all blocks in the page, ordered by the order stored
        in the page state.
        """
        uid_order = flattened_block_uids(self.load())

        def block_sort_key(block):
            uid = IUUID(block)
            if uid not in uid_order:
                return '~'
            else:
                return uid_order.index(uid)

        blocks = filter(ISimplelayoutBlock.providedBy,
                        map(self.context._getOb,
                            self.context.objectIds()))
        blocks.sort(key=block_sort_key)
        return blocks

    def update_object_positions(self):
        """Update the positions of the sl blocks in the orderable folder.
        """
        block_ids = map(methodcaller('getId'), self.get_ordered_blocks())
        self.context.moveObjectsToTop(block_ids)

    def _default_page_config(self):
        """Returns a default page config"""
        request = getattr(self.context, 'REQUEST', getSite().REQUEST)
        adapter = queryMultiAdapter((self.context, request),
                                    ISimplelayoutContainerConfig)

        if adapter is not None:
            layout = adapter.default_page_layout()
            if layout is not None:
                return layout

        return {'default': [{"cols": [{"blocks": []}]}]}


class BlockConfiguration(object):
    """Adapter for storing block configuration.
    """
    implements(IBlockConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, data):
        annotations = IAnnotations(self.context)
        annotations[BLOCK_ANNOTATION_KEY] = PersistentMapping(data)

    def load(self):
        annotations = IAnnotations(self.context)
        return annotations.setdefault(BLOCK_ANNOTATION_KEY,
                                      PersistentMapping())
