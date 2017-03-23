from Acquisition import aq_inner
from Acquisition import aq_parent
from DateTime import DateTime
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
import json


def unwrap_persistence(conf):
    """Unwrap recursice persistent page state
    """
    def unwrap(data):
        if isinstance(data, (PersistentMapping, dict)):
            data = dict(data)
            for key, value in data.items():
                data[key] = unwrap(value)
        elif isinstance(data, (PersistentList, list, tuple, set)):
            return list(map(unwrap, data))
        else:
            # Usually we got basestrings, or integer here, so do nothing.
            pass
        return data
    return unwrap(conf)


def update_page_state_on_copy_paste_block(block, event):
    """Update the uid of the new created block in the page state.
    block: new block
    event.original: origin of the copy event - usually the simplelayout page"""

    # Only update page state, if the original object is a Simplelayout page.
    if not ISimplelayout.providedBy(event.original):
        return

    # The event is triggered recursively - we need to check if the block is
    # actually part of the original page
    if event.original.get(block.id) is None:
        return

    origin_block_uid = IUUID(event.original.get(block.id))
    page_config = IPageConfiguration(block.aq_parent)
    page_state = unwrap_persistence(page_config.load())

    new_block_uid = IUUID(block)
    new_page_state = json.loads(
        json.dumps(page_state).replace(origin_block_uid,
                                       new_block_uid))

    # We should not update object positions here, because:
    # 1. "Ordered folder" makes sure that the order is the same as before
    #    when copy / pasting.
    # 2. Updating positions does not work here, because our objects are not
    #    acquisition wrappable yet (since not yet pasted) and the updating
    #    mechanism will trigger events (such as plone.app.referenceablebehavior),
    #    which require acquisition.
    page_config.store(new_page_state, update_positions=False)


def update_page_state_on_block_remove(block, event):

    if event.newParent is None:
        # Be sure it's not cut/paste
        block_uid = IUUID(block)
        parent = aq_parent(aq_inner(block))

        # Do nothing if the event wasn't fired by the block's parent.
        # This happens when an ancestor is deleted, e.g. the Plone site itself.
        if parent is not event.oldParent:
            return

        config = IPageConfiguration(parent)
        page_state = config.load()

        for container in page_state.values():
            for layout in container:
                for column in layout['cols']:
                    cache_amound_blocks = len(column['blocks'])
                    column['blocks'] = [item for item in column['blocks']
                                        if item['uid'] != block_uid]
                    if cache_amound_blocks != len(column['blocks']):
                        # Block has been removed
                        break
        config.store(page_state)


def modify_parent_on_block_edit(block, event):
    parent = aq_parent(aq_inner(block))

    # Parent may be None.
    # Example: ObjectGeoreferencedEvent triggers Modified event, but the obj is
    # not yet added to a container
    if parent is None:
        return

    if IPloneSiteRoot.providedBy(parent):
        parent.setModificationDate(DateTime())
    else:
        parent.reindexObject()
