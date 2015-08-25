from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.interfaces import ISimplelayoutActions
from ftw.simplelayout.utils import get_block_types
from ftw.simplelayout.utils import normalize_portal_type
from plone.app.content.browser.folderfactories import _allowedTypes
from Products.CMFCore.Expression import Expression
from Products.CMFCore.Expression import getExprContext
from Products.CMFPlone.interfaces.constrains import IConstrainTypes
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.publisher.browser import BrowserView


class AddableBlocks(BrowserView):

    def __call__(self):
        return json_response(self.request, dict(self.addable_blocks()))

    def addable_blocks(self):
        block_types = get_block_types()
        allowed_types = self._addable_types()

        default_actions = getMultiAdapter((self.context, self.request),
                                          ISimplelayoutActions)

        for fti in block_types:
            if fti in allowed_types:
                if IDexterityFTI.providedBy(fti):
                    add_url = Expression(fti.add_view_expr)(
                        getExprContext(self.context, self.context))
                    add_url = add_url.replace('++add++', '++add_block++')
                else:
                    add_url = "{}/++add_block++{}".format(
                        self.context.absolute_url(), fti.id)

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
                        'title': translate(msgid=fti.Title(),
                                           domain=fti.i18n_domain,
                                           context=self.request),
                        'description': translate(msgid=fti.Description(),
                                                 domain=fti.i18n_domain,
                                                 context=self.request),
                        'contentType': normalized_portal_type,
                        'formUrl': add_url,
                        'actions': actions.actions,
                    }
                )

    def _addable_types(self):
        allowed_types = _allowedTypes(self.request, self.context)
        constrain = IConstrainTypes(self.context, None)
        if constrain is None:
            return allowed_types
        else:
            locally_allowed = constrain.getLocallyAllowedTypes()
            return [fti for fti in allowed_types
                    if fti.getId() in locally_allowed]
