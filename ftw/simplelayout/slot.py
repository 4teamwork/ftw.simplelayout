from Acquisition import aq_base
from Products.CMFPlone.utils import base_hasattr


SIMPLELAYOUT_SLOT_ATTR = 'sl_slot_information'


def get_slot_id(slot):
    return 'sl-slot-{0}'.format(str(slot))


def get_slot_information(block):
    return getattr(aq_base(block), SIMPLELAYOUT_SLOT_ATTR, 'None')


def set_slot_information(block, slot):
    slot = slot.lstrip('sl-slot-')
    if base_hasattr(block, SIMPLELAYOUT_SLOT_ATTR):
        aq_base(block).manage_changeProperties(
            **{SIMPLELAYOUT_SLOT_ATTR: slot})
    else:
        aq_base(block).manage_addProperty(SIMPLELAYOUT_SLOT_ATTR,
                                          slot,
                                          'string')
