from ftw.simplelayout import _
from ftw.simplelayout.interfaces import ISimplelayoutActions
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.utils import normalize_portal_type
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
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

        default_actions = getMultiAdapter((self.context, self.request),
                                          ISimplelayoutActions)

        for fti in block_types:
            if fti.id in allowed_types:
                add_url = Expression(fti.add_view_expr)(
                    getExprContext(self.context, self.context))
                add_url = add_url.replace('++add++', '++add_block++')

                normalized_portal_type = normalize_portal_type(fti.id)

                specific_actions = queryMultiAdapter(
                    (self.context, self.request),
                    ISimplelayoutActions,
                    name='{0}-actions'.format(normalized_portal_type))

                if specific_actions:
                    actions = specific_actions
                else:
                    actions = default_actions

                yield (
                    normalized_portal_type,
                    {
                        'title': _(fti.Title()),
                        'description': _(fti.Description()),
                        'contentType': normalized_portal_type,
                        'formUrl': add_url,
                        'actions': actions.actions,
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
