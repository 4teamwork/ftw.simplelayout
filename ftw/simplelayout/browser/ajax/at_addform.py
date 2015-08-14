from ftw.simplelayout import _
from ftw.simplelayout.browser.ajax.addform import AddView
from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.utils import get_block_html
from plone.dexterity.browser.add import DefaultAddForm
from plone.supermodel import model
from zope import schema


# A simple add form for archetypes based blocks which contains only a title
# field. Other fields can be edited using the edit form.
class IATAddFormSchema(model.Schema):

    title = schema.TextLine(
        title=_(u"label_title", default=u"Title"),
        required=True,
    )


class ATAddForm(DefaultAddForm):

    def createAndAdd(self, data):
        id_ = self.context.generateUniqueId(self.portal_type)
        title = data['title'].encode('utf8')
        new_id = self.context.invokeFactory(self.portal_type, id_)
        obj = self.context[new_id]
        obj.processForm(values=dict(title=title))
        self._finishedAdd = True
        self.obj_uid = obj.UID()
        self.obj_html = get_block_html(obj)
        return obj

    def render(self):
        if self._finishedAdd:
            return json_response(self.request, proceed=True)
        return super(ATAddForm, self).render()

    @property
    def schema(self):
        return IATAddFormSchema

    @property
    def additionalSchemata(self):
        return ()

    @property
    def label(self):
        return _(u"Add ${name}", mapping={'name': self.portal_type})


class ATAddView(AddView):
    form = ATAddForm
