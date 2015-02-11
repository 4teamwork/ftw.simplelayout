from ftw.simplelayout import _
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from ftw.simplelayout.utils import normalize_portal_type
from zope.component import queryUtility
from zope.publisher.browser import BrowserView
import json


class AddableBlocks(BrowserView):

    def __call__(self):
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return json.dumps(dict(self.addable_blocks()))

    def addable_blocks(self):
        block_types = set(self._get_block_types())
        allowed_types = set(ISelectableConstrainTypes(
            self.context).getImmediatelyAddableTypes())

        for fti in block_types:
            if fti.id in allowed_types:
                add_url = Expression(fti.add_view_expr)(
                    getExprContext(self.context, self.context))
                add_url = add_url.replace('++add++', '++add_block++')

                yield (
                    normalize_portal_type(fti.id),
                    {
                        'title': _(fti.Title()),
                        'description': _(fti.Description()),
                        'contentType': normalize_portal_type(fti.id),
                        'formUrl': add_url,
                        'actions': {
                            'edit': {
                                'class': 'Edit icon-edit',
                                'title': 'Edit block',
                            },
                            'imageLeft': {
                                'class': 'icon-image-left server-action',
                                'title': 'Float image left',
                                'href': './sl-ajax-reload-block-view',
                                'data-scale': 'mini'
                            },
                            'imageFloatNone': {
                                'class': 'icon-image server-action',
                                'title': 'image',
                                'href': './sl-ajax-reload-block-view',
                                'data-scale': 'large'
                            },
                        },
                    }
                )

    def _get_block_types(self):
        types_tool = getToolByName(self.context, 'portal_types')
        typeids = types_tool.objectIds()
        typeids.sort()
        for type_id in typeids:
            dx_fti = queryUtility(IDexterityFTI, name=type_id)
            if not dx_fti:
                continue
            else:
                if ISimplelayoutBlock.__identifier__ in dx_fti.behaviors:
                    yield dx_fti
