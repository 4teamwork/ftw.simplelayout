from ftw.simplelayout.browser.ajax.addform import AddView
from ftw.simplelayout.browser.ajax.at_addform import ATAddView
from ftw.simplelayout.interfaces import ISimplelayout
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError
from plone.dexterity.interfaces import IDexterityFTI


class AddViewTraverser(object):
    """Add view traverser.
    """
    adapts(ISimplelayout, Interface)
    implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        ttool = getToolByName(self.context, 'portal_types')
        ti = ttool.getTypeInfo(name)
        if ti is not None:

            if not IDexterityFTI.providedBy(ti):
                # not DX content, assume AT
                add_view = ATAddView(self.context, self.request, ti)
            else:
                add_view = AddView(self.context, self.request, ti)

            if add_view is not None:
                add_view.__name__ = ti.factory
                template = ViewPageTemplateFile('templates/add.pt')
                add_view.index = BoundPageTemplate(template, add_view)
                return add_view.__of__(self.context)

        raise TraversalError(self.context, name)
