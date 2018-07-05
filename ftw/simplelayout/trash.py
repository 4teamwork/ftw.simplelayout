from AccessControl import getSecurityManager
from Acquisition import aq_inner
from Acquisition import aq_parent
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.trash.interfaces import IIsRestoreAllowedAdapter
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IIsRestoreAllowedAdapter)
@adapter(ISimplelayoutBlock, Interface)
def is_restoring_bock_allowed(context, request):
    parent = aq_parent(aq_inner(context))
    return bool(getSecurityManager().checkPermission('Modify portal content', parent))
