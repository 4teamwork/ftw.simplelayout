from ftw.simplelayout.utils import get_block_types
from ftw.simplelayout.utils import normalize_portal_type
from ftw.theming.interfaces import ISCSSResourceFactory
from ftw.theming.resource import SCSSResource
from zope.interface import provider


TEMPLATE = """
#plone-contentmenu-factories {{
  {0} {{
    display: none !important;
  }}
}}
"""


@provider(ISCSSResourceFactory)
def hide_blocks_in_factory_menu(context, request):

    selectors = ['']

    for block_fti in get_block_types():
        selectors.append(
            u'.contenttype-{0}'.format(
                normalize_portal_type(block_fti.getId())))

    return SCSSResource('simplelayout_hide_blocks.scss',
                        slot='addon',
                        source=TEMPLATE.format(', '.join(selectors)))
