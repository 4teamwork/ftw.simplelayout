from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.uuid.interfaces import IUUID
import json


def unwrap_persistence(conf):
    """Unwrap recursice persistent page state
    """
    def unwrap(data):
        if isinstance(data, PersistentMapping):
            data = dict(data)
            for key, value in data.items():
                data[key] = unwrap(value)
        elif isinstance(data, PersistentList):
            return list(map(unwrap, data))
        else:
            # Usually we got basestrings, or integer here, so do nothing.
            pass
        return data
    return unwrap(conf)


def update_page_state(block, event):
    """Update the uid of the new created block in the page state.
    block: new block
    event.original: origin of the copy event - usually the simplelayout page"""

    # Only update page state, if the original object is a Simplelayout page.
    if not ISimplelayout.providedBy(event.original):
        return

    origin_block_uid = IUUID(event.original.get(block.id))
    page_config = IPageConfiguration(block.aq_parent)
    page_state = unwrap_persistence(page_config.load())

    new_block_uid = IUUID(block)
    new_page_state = json.loads(
        json.dumps(page_state).replace(origin_block_uid,
                                       new_block_uid))

    page_config.store(new_page_state)
