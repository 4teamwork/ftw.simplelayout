from ftw.simplelayout.browser.ajax.utils import json_response
from ftw.simplelayout.utils import get_block_html
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from Products.statusmessages.interfaces import IStatusMessage


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
                                 proceed=True)

        return json_response(self.request,
                             content=super(AddView, self).render(),
                             proceed=False)
