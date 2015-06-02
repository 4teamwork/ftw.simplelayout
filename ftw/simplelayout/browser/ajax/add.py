from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.simplelayout.interfaces import ISimplelayoutPage
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from zope.component import adapts
from zope.interface import Interface
from zope.interface import implements
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError
import json

import logging

logger = logging.getLogger("Plone")


class AddViewTraverser(object):
    """Add view traverser.
    """
    adapts(ISimplelayoutPage, Interface)
    implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        ttool = getToolByName(self.context, 'portal_types')
        ti = ttool.getTypeInfo(name)
        if ti is not None:
            add_view = AddView(self.context, self.request, ti)

            if add_view is not None:
                add_view.__name__ = ti.factory
                template = ViewPageTemplateFile('templates/add.pt')
                add_view.index = BoundPageTemplate(template, add_view)
                return add_view.__of__(self.context)

        raise TraversalError(self.context, name)


class AddForm(DefaultAddForm):

    def createAndAdd(self, data):
        obj = super(AddForm, self).createAndAdd(data)
        self.obj_uid = obj.UID()
        aq_obj = obj.__of__(self.context)
        self.obj_html = aq_obj()
        return obj

    def render(self):
        if self._finishedAdd:
            return json.dumps(dict(proceed=True))
        return super(AddForm, self).render()


class AddView(DefaultAddView):
    form = AddForm

    def render(self):
        if hasattr(self.form_instance, 'obj_uid'):
            self.request.response.setHeader('Content-Type', 'application/json')
            return json.dumps(dict(
                uid=self.form_instance.obj_uid,
                content=self.form_instance.obj_html,
                proceed=True,
            ))

        return json.dumps(dict(
            content=super(AddView, self).render(),
            proceed=False,
        ))
