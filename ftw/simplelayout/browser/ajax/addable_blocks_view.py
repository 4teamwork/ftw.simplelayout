from ftw.simplelayout.interfaces import ISimplelayoutBlock
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.constrains import ISelectableConstrainTypes
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryUtility
from zope.publisher.browser import BrowserView


class AddableBlocks(BrowserView):

    template = ViewPageTemplateFile('templates/addable_blocks.pt')

    def __call__(self):
        return self.template()

    def addable_blocks(self):
        block_types = set(self._get_block_types())
        allowed_types = set(ISelectableConstrainTypes(
            self.context).getImmediatelyAddableTypes())
        return block_types & allowed_types

    def _get_block_types(self):
        types_tool = getToolByName(self.context, 'portal_types')

        for type_name in types_tool.objectIds():
            dx_fti = queryUtility(IDexterityFTI, name=type_name)
            if not dx_fti:
                continue
            else:
                if ISimplelayoutBlock.__identifier__ in dx_fti.behaviors:
                    yield type_name
