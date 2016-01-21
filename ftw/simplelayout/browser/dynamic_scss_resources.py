from ftw.simplelayout.utils import get_block_types
from ftw.simplelayout.utils import normalize_portal_type
from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.resource import DynamicSCSSResource
from zope.interface import provider
import hashlib


TEMPLATE = """
#plone-contentmenu-factories {{
  {0} {{
    display: none !important;
  }}
}}
"""


@provider(ISCSSResourceFactory)
def hide_blocks_in_factory_menu(context, request):

    selectors = []

    for block_fti in get_block_types():
        selectors.append(
            u'.contenttype-{0}'.format(
                normalize_portal_type(block_fti.getId())))

    cachekey = hashlib.md5(''.join(selectors)).hexdigest()

    if len(selectors):
        source = TEMPLATE.format(', '.join(selectors))
    else:
        source = ''

    return DynamicSCSSResource('simplelayout_hide_blocks.scss',
                               slot='addon',
                               source=source,
                               cachekey=cachekey)
