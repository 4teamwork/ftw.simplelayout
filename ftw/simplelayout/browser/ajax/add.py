from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.utils import get_block_html
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import BoundPageTemplate
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import adapts
from zope.interface import implements
from zope.interface import Interface
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError


class AddViewTraverser(object):
    """Add view traverser.
    """
    adapts(ISimplelayout, Interface)
    implements(ITraversable)

    template = ViewPageTemplateFile('templates/add.pt')

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
                add_view.index = BoundPageTemplate(self.template.im_func,
                                                   add_view)
                return add_view.__of__(self.context)

        raise TraversalError(self.context, name)


class AddForm(DefaultAddForm):

    def createAndAdd(self, data):
        obj = super(AddForm, self).createAndAdd(data)
        self.obj_uid = obj.UID()
        aq_obj = obj.__of__(self.context)
        self.obj_html = get_block_html(aq_obj)
        return obj

    def render(self):
        if self._finishedAdd:
            return json_response(self.request, proceed=True)
        return super(AddForm, self).render()


class AddView(DefaultAddView):
    form = AddForm

    def render(self):
        if hasattr(self.form_instance, 'obj_uid'):
            obj = uuidToObject(self.form_instance.obj_uid)
            self.request.response.setHeader('Content-Type', 'application/json')

            # Consume all statusmessages
            IStatusMessage(self.request).show()

            return json_response(self.request,
                                 uid=self.form_instance.obj_uid,
                                 url=obj.absolute_url(),
                                 content=self.form_instance.obj_html,
                                 proceed=True,
                                 id=obj.id)

        return json_response(self.request,
                             content=super(AddView, self).render(),
                             proceed=False)
